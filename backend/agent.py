"""Command A Reasoning 기반 헌혈 문진 에이전트"""

import json
import sys
import time
from datetime import date
import cohere
from cohere.types.thinking import Thinking
from dotenv import load_dotenv
from backend.tools import TOOLS, execute_tool, get_rate_limits, _extract_limits

load_dotenv()

from backend.classifier import MODEL_FAST, MODEL_REASONING, classify_query

def _build_system_prompt() -> str:
    today = date.today().isoformat()
    return f"""당신은 대한적십자사 헌혈 문진 지원 AI입니다.
오늘 날짜: {today}

역할:
- 헌혈 희망자의 질문에 대해 판정기준 문서를 검색하여 정확한 답변을 제공합니다.
- 약물 복용, 여행력, 건강 상태 등을 종합적으로 판단합니다.
- 모든 답변에는 반드시 출처를 명시합니다.

판정 원칙:
- 헌혈 가능 여부는 반드시 판정기준 문서에 근거하여 판단합니다.
- 복합 조건(약물 + 혈압 등)은 각 조건을 개별적으로 확인한 후 종합 판정합니다.
- 불확실한 경우 문진 간호사 대면 확인을 권장합니다.

판정 로직 (반드시 이 순서로 판단):
1. 약물/행위의 유예기간을 확인합니다.
2. 사용자의 복용/방문 시점으로부터 경과 시간을 계산합니다.
3. 경과 시간 >= 유예기간 → "즉시가능" (eligible: true, wait_days: 0)
4. 경과 시간 < 유예기간 → "조건부" (eligible: false, wait_days: 남은 일수)
5. 가이드라인의 "조건부 가능"은 약물 카테고리 분류이며, 최종 판정이 아닙니다.
   반드시 경과 시간과 유예기간을 비교하여 최종 판정(즉시가능/조건부/불가)을 결정합니다.
6. 전혈헌혈과 성분헌혈의 유예기간이 다르면, 전혈 기준으로 판정하고 성분 제약은 reason에 명시합니다.

도구 호출 원칙:
- 여행력 질문: check_malaria_risk로 위험등급 확인 후, search_guideline으로 해당 등급의 보류 규정을 교차 검증합니다.
- 약물 질문: search_drug_info로 약물 정보를 확인합니다. 복합 조건이면 search_guideline도 추가 호출합니다.
- 복합 조건(약물 + 혈압 등): 각 조건별로 관련 도구를 개별 호출하여 교차 검증합니다.
- **날짜/일수 계산은 절대로 직접 하지 마세요. 반드시 calculate_wait_days 도구를 사용하세요.**
  예: 유예기간 365일, 경과 21일 → calculate_wait_days(deferral_days=365, elapsed_days=21)

응답 형식:
- 한국어로 답변합니다.
- 판정 결과를 명확히 제시합니다 (즉시가능 / 조건부 / 불가).
- 유예기간이 있는 경우 일수를 명시합니다.
"""

JUDGMENT_SCHEMA = {
    "type": "json_object",
    "json_schema": {
        "type": "object",
        "properties": {
            "eligible": {"type": "boolean", "description": "헌혈 가능 여부"},
            "condition": {"type": "string", "description": "즉시가능 / 조건부 / 불가"},
            "reason": {"type": "string", "description": "판정 근거 (한국어)"},
            "wait_days": {"type": "integer", "description": "유예기간 (일, 없으면 0)"},
            "citation": {"type": "string", "description": "참조한 출처를 쉼표로 구분 (약학정보원, 질병관리청, 헌혈 판정기준 중 해당하는 것 모두)"},
            "answer": {"type": "string", "description": "사용자에게 보여줄 상세 답변. 한국어, 출처 포함, 마크다운 사용 가능."},
        },
        "required": ["eligible", "condition", "reason", "answer"],
    }
}


def run_agent(query: str, thinking_enabled: bool = False, thinking_budget: int = 2000, model: str = None):
    """에이전트 실행: 툴 호출 루프 → 최종 판정 JSON 반환"""
    t_start = time.time()
    co = cohere.ClientV2()

    t0 = time.time()
    classification = classify_query(query)
    print(f"[TIMING]classify: {time.time()-t0:.2f}s")
    if model is None:
        model = classification["model"]
        thinking_enabled = classification["thinking"]

    messages = [
        {"role": "system", "content": _build_system_prompt()},
        {"role": "user", "content": query},
    ]

    tool_logs = []
    total_tokens = {"input_tokens": 0, "output_tokens": 0}
    thinking_content = None

    # 툴 호출 루프 (최대 5회)
    t_tool = time.time()
    for _ in range(5):
        chat_params = {
            "model": model,
            "messages": messages,
            "tools": TOOLS,
            "safety_mode": "CONTEXTUAL",
            "strict_tools": True,
        }

        use_thinking = thinking_enabled and model == MODEL_REASONING
        if use_thinking:
            chat_params["thinking"] = Thinking(type="enabled", token_budget=thinking_budget)
        elif model == MODEL_REASONING:
            chat_params["thinking"] = Thinking(type="disabled")

        response = co.chat(**chat_params)
        if response.usage and response.usage.tokens:
            total_tokens["input_tokens"] += response.usage.tokens.input_tokens or 0
            total_tokens["output_tokens"] += response.usage.tokens.output_tokens or 0

        # thinking 내용 추출
        if use_thinking and response.message and response.message.content:
            for block in response.message.content:
                if hasattr(block, "type") and block.type == "thinking":
                    thinking_content = block.thinking

        # 툴 호출이 없으면 루프 종료
        if response.finish_reason != "TOOL_CALL":
            break

        # 툴 호출 처리
        if response.message and response.message.tool_calls:
            messages.append({"role": "assistant", "tool_calls": response.message.tool_calls})

            for tc in response.message.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                result = execute_tool(fn_name, fn_args)

                preview = result[:2000] + "..." if len(result) > 2000 else result
                tool_logs.append({
                    "tool": fn_name,
                    "args": fn_args,
                    "result": preview,
                    "result_preview": preview,
                    "status": "done",
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

    t_tool_elapsed = time.time() - t_tool
    print(f"[TIMING]tool_loop: {t_tool_elapsed:.2f}s ({len(tool_logs)} tools)")

    # 최종 판정 JSON 생성 (response_format 사용, tools 없이)
    t_judgment = time.time()
    messages_for_judgment = list(messages)
    messages_for_judgment.append({
        "role": "user",
        "content": "위 정보를 바탕으로 헌혈 가능 여부를 JSON으로 판정해주세요. eligible, condition(즉시가능/조건부/불가), reason, wait_days, citation, answer 필드를 포함하세요. answer에는 사용자에게 보여줄 상세 답변(한국어, 출처 포함)을 작성하세요."
    })

    judgment_params = {
        "model": model,
        "messages": messages_for_judgment,
        "response_format": JUDGMENT_SCHEMA,
        "safety_mode": "CONTEXTUAL",
        "thinking": Thinking(type="disabled"),
    }

    judgment_raw = co.with_raw_response.chat(**judgment_params)
    chat_limits = _extract_limits(judgment_raw.headers)
    judgment_response = judgment_raw.data
    if judgment_response.usage and judgment_response.usage.tokens:
        total_tokens["input_tokens"] += judgment_response.usage.tokens.input_tokens or 0
        total_tokens["output_tokens"] += judgment_response.usage.tokens.output_tokens or 0

    # 판정 JSON 파싱
    judgment_text = ""
    if judgment_response.message and judgment_response.message.content:
        for block in judgment_response.message.content:
            if hasattr(block, "text"):
                judgment_text += block.text

    judgment = json.loads(judgment_text) if judgment_text else {}

    # answer는 judgment에서 추출 (LLM 3회 → 2회 최적화)
    answer_text = judgment.pop("answer", "")

    t_judgment_elapsed = time.time() - t_judgment
    t_total = time.time() - t_start
    print(f"[TIMING]judgment: {t_judgment_elapsed:.2f}s")
    print(f"[TIMING]total: {t_total:.2f}s")

    timing = {
        "classify": round(time.time() - t_start - t_tool_elapsed - t_judgment_elapsed, 2),
        "tool_loop": round(t_tool_elapsed, 2),
        "judgment": round(t_judgment_elapsed, 2),
        "total": round(t_total, 2),
    }

    # rate limits 수집 (embed/rerank는 tools.py에서, chat은 여기서)
    tool_rate_limits = get_rate_limits()
    rate_limits = {
        "chat": chat_limits,
        "embed": tool_rate_limits.get("embed", {}),
        "rerank": tool_rate_limits.get("rerank", {}),
    }

    return {
        "answer": answer_text,
        "judgment": judgment,
        "tool_calls": tool_logs,
        "tool_logs": tool_logs,
        "thinking": thinking_content,
        "tokens": total_tokens,
        "total_tokens": total_tokens,
        "rate_limits": rate_limits,
        "classification": classification,
        "timing": timing,
    }


def _collect_tokens(chunk, total_tokens):
    """message-end 이벤트에서 토큰 사용량 집계"""
    if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'usage') and chunk.delta.usage:
        usage = chunk.delta.usage
        if hasattr(usage, 'tokens') and usage.tokens:
            total_tokens["input_tokens"] += getattr(usage.tokens, 'input_tokens', 0) or 0
            total_tokens["output_tokens"] += getattr(usage.tokens, 'output_tokens', 0) or 0


def run_agent_stream(query: str, thinking_enabled: bool = False, thinking_budget: int = 2000, model: str = None):
    """에이전트 실행 (실시간 스트리밍): co.chat_stream()으로 각 토큰 즉시 yield"""
    t_start = time.time()
    co = cohere.ClientV2()

    t0 = time.time()
    classification = classify_query(query)
    t_classify = time.time() - t0
    print(f"[TIMING]classify: {t_classify:.2f}s")
    if model is None:
        model = classification["model"]
        thinking_enabled = classification["thinking"]

    # 1) 분류 결과 즉시 전송
    yield {"type": "classification", "classification": classification}

    messages = [
        {"role": "system", "content": _build_system_prompt()},
        {"role": "user", "content": query},
    ]

    total_tokens = {"input_tokens": 0, "output_tokens": 0}
    step = 0

    use_thinking = thinking_enabled and model == MODEL_REASONING

    # 2) 툴 호출 루프 — co.chat_stream()으로 실시간 스트리밍
    t_tool = time.time()
    for _ in range(5):
        chat_params = {
            "model": model,
            "messages": messages,
            "tools": TOOLS,
            "safety_mode": "CONTEXTUAL",
            "strict_tools": True,
        }

        if use_thinking:
            chat_params["thinking"] = Thinking(type="enabled", token_budget=thinking_budget)
        elif model == MODEL_REASONING:
            chat_params["thinking"] = Thinking(type="disabled")

        # 스트리밍 호출 — 각 토큰이 생성될 때마다 즉시 yield
        tool_calls_buf = []  # [{id, name, args_str, step}]
        content_text = ""
        finish_reason = None

        for chunk in co.chat_stream(**chat_params):
            if chunk.type == "tool-plan-delta":
                tp = chunk.delta.message.tool_plan or ""
                if tp:
                    yield {"type": "tool_plan", "text": tp}

            elif chunk.type == "tool-call-start":
                tc = chunk.delta.message.tool_calls
                step += 1
                tool_calls_buf.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "args_str": "",
                    "step": step,
                })
                yield {"type": "tool_start", "step": step, "tool": tc.function.name, "args": {}}

            elif chunk.type == "tool-call-delta":
                if tool_calls_buf:
                    args_chunk = chunk.delta.message.tool_calls.function.arguments or ""
                    tool_calls_buf[-1]["args_str"] += args_chunk

            elif chunk.type == "content-delta":
                text = chunk.delta.message.content.text or ""
                content_text += text
                if text:
                    yield {"type": "content_delta", "text": text}

            elif chunk.type == "content-start":
                if hasattr(chunk.delta.message.content, 'type') and chunk.delta.message.content.type == "thinking":
                    pass  # thinking content-start

            elif chunk.type == "message-end":
                finish_reason = chunk.delta.finish_reason
                _collect_tokens(chunk, total_tokens)

        # 스트림 종료 후: 도구 실행
        if finish_reason == "TOOL_CALL" and tool_calls_buf:
            # assistant 메시지 재구성 (Cohere API 형식)
            reconstructed_tc = []
            for tc_data in tool_calls_buf:
                reconstructed_tc.append({
                    "id": tc_data["id"],
                    "type": "function",
                    "function": {
                        "name": tc_data["name"],
                        "arguments": tc_data["args_str"],
                    }
                })
            messages.append({"role": "assistant", "tool_calls": reconstructed_tc})

            # 각 도구 실행 → 즉시 yield
            for tc_data in tool_calls_buf:
                fn_args = json.loads(tc_data["args_str"]) if tc_data["args_str"] else {}
                result = execute_tool(tc_data["name"], fn_args)
                preview = result[:2000] + "..." if len(result) > 2000 else result

                yield {
                    "type": "tool_done",
                    "step": tc_data["step"],
                    "tool": tc_data["name"],
                    "args": fn_args,
                    "result": preview,
                    "result_preview": preview,
                    "status": "done",
                }

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_data["id"],
                    "content": result,
                })
        else:
            # 도구 호출 없음 — 루프 탈출
            break

    t_tool_elapsed = time.time() - t_tool
    print(f"[TIMING]tool_loop: {t_tool_elapsed:.2f}s ({step} tools)")

    # 3) 판정 생성 (스트리밍)
    t_judgment = time.time()
    messages_for_judgment = list(messages)
    messages_for_judgment.append({
        "role": "user",
        "content": "위 정보를 바탕으로 헌혈 가능 여부를 JSON으로 판정해주세요. eligible, condition(즉시가능/조건부/불가), reason, wait_days, citation, answer 필드를 포함하세요. answer에는 사용자에게 보여줄 상세 답변(한국어, 출처 포함)을 작성하세요."
    })

    judgment_text = ""
    for chunk in co.chat_stream(
        model=model,
        messages=messages_for_judgment,
        response_format=JUDGMENT_SCHEMA,
        safety_mode="CONTEXTUAL",
        thinking=Thinking(type="disabled"),
    ):
        if chunk.type == "content-delta":
            judgment_text += chunk.delta.message.content.text
        elif chunk.type == "message-end":
            _collect_tokens(chunk, total_tokens)

    judgment = json.loads(judgment_text) if judgment_text else {}
    answer_text = judgment.pop("answer", "")

    t_judgment_elapsed = time.time() - t_judgment
    t_total = time.time() - t_start
    print(f"[TIMING]judgment: {t_judgment_elapsed:.2f}s")
    print(f"[TIMING]total: {t_total:.2f}s")

    timing = {
        "classify": round(t_classify, 2),
        "tool_loop": round(t_tool_elapsed, 2),
        "judgment": round(t_judgment_elapsed, 2),
        "total": round(t_total, 2),
    }

    # 4) 판정 결과 전송
    yield {"type": "judgment", "judgment": judgment, "timing": timing}

    # 5) 답변 전송
    yield {"type": "answer", "text": answer_text}

    # 6) 완료
    tool_rate_limits = get_rate_limits()
    rate_limits = {
        "chat": {},
        "embed": tool_rate_limits.get("embed", {}),
        "rerank": tool_rate_limits.get("rerank", {}),
    }

    yield {
        "type": "result",
        "total_tokens": total_tokens,
        "rate_limits": rate_limits,
    }


if __name__ == "__main__":
    print("=== 테스트: 아스피린 질문 ===")
    result = run_agent("아스피린 복용 후 헌혈 가능한가요? 3일 전 325mg 복용했습니다.")
    print(f"답변: {result['answer'][:200]}")
    print(f"판정: {json.dumps(result['judgment'], ensure_ascii=False, indent=2)}")
    print(f"툴 호출: {len(result['tool_logs'])}건")
    for log in result["tool_logs"]:
        print(f"  - {log['tool']}({log['args']})")
    print(f"사용량: {result['total_tokens']}")
