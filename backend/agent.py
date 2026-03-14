"""Command A / A Reasoning 기반 헌혈 문진 에이전트"""

import json
import time
from datetime import date
import cohere
from cohere.types.thinking import Thinking
from dotenv import load_dotenv
from backend.tools import TOOLS, execute_tool, get_rate_limits

load_dotenv()

from backend.classifier import MODEL_REASONING, classify_query


def _build_system_prompt(lang: str = "ko") -> str:
    today = date.today().isoformat()
    if lang == "en":
        return f"""You are a Korean Red Cross blood donation screening support AI.
Today's date: {today}

Role:
- Provide accurate answers by searching screening guideline documents for donor questions.
- Comprehensively evaluate drug intake, travel history, health conditions, etc.
- Always cite sources in every answer.

CRITICAL LANGUAGE RULE: You MUST answer ONLY in English. Never use Korean in your response.
All guideline documents and tool results are in English. Respond entirely in English.

Screening logic (follow this order strictly):
1. Check the deferral period for the drug/action.
2. Calculate elapsed time from the intake/visit date.
3. Elapsed time >= deferral period → "Eligible" (eligible: true, wait_days: 0)
4. Elapsed time < deferral period → "Conditional" (eligible: false, wait_days: remaining days)
5. "Conditionally eligible" in guidelines is a drug category classification, not the final decision.
   Always compare elapsed time with deferral period to determine the final decision (Eligible/Conditional/Ineligible).
6. If whole blood and component donation deferral periods differ, assess based on whole blood and note component restrictions in reason.

Tool usage principles:
- Travel questions: Check risk level with check_malaria_risk, then cross-verify with search_guideline.
- Drug questions: Check with search_drug_info. For complex conditions, also call search_guideline.
- Complex conditions (drug + BP, etc.): Call relevant tools individually per condition for cross-verification.
- **Never calculate dates/days manually. Always use the calculate_wait_days tool. Convert ALL values to HOURS first.**
  e.g., 36-hour deferral, 3 days elapsed → calculate_wait_days(deferral_hours=36, elapsed_hours=72)
  e.g., 1-year deferral, 21 days elapsed → calculate_wait_days(deferral_hours=8760, elapsed_hours=504)
- MANDATORY: If ANY deferral period exists, you MUST call calculate_wait_days to compute remaining time.
  Never skip this tool. Never calculate days manually.
  For "last month" use 30 days = 720 hours. For "last week" use 7 days = 168 hours.

Response format:
- Answer in English.
- Clearly state the assessment result: "eligible to donate" or "not yet eligible" with remaining wait days.
- Always include [Source: X] citation tags (e.g., [Source: Drug Info Center]).
- Specify wait days if there is a deferral period.
- At the very end of your answer, include this exact tag on a new line:
  [JUDGMENT: condition=Eligible|Conditional|Ineligible, wait_days=N, source=SOURCE_NAME]
  Example: [JUDGMENT: condition=Eligible, wait_days=0, source=Drug Info Center]
  Example: [JUDGMENT: condition=Conditional, wait_days=155, source=Blood Donation Criteria]
  This tag is parsed by the system — do not omit or modify the format.

CRITICAL: ALL your outputs — tool plans, reasoning, and final answers — MUST be in English.
"""
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
- **날짜/일수 계산은 절대로 직접 하지 마세요. 반드시 calculate_wait_days 도구를 사용하세요. 모든 값을 시간(hours) 단위로 변환하여 입력하세요.**
  예: 36시간 유예, 3일 경과 → calculate_wait_days(deferral_hours=36, elapsed_hours=72)
  예: 1년 유예, 21일 경과 → calculate_wait_days(deferral_hours=8760, elapsed_hours=504)
- 필수: 유예기간이 있으면 반드시 calculate_wait_days를 호출하세요. 이 도구를 건너뛰지 마세요.
  "지난달" = 30일 = 720시간, "지난주" = 7일 = 168시간으로 변환하세요.

응답 형식:
- 한국어로 답변합니다.
- 판정 결과를 명확히 제시합니다: "즉시가능", "조건부", "불가" 중 하나를 반드시 포함하세요.
- 유예기간이 있는 경우 남은 일수를 명시합니다.
- 반드시 [출처: X] 태그를 포함하세요 (예: [출처: 약학정보원]).
- 답변 마지막에 반드시 다음 태그를 새 줄에 포함하세요:
  [JUDGMENT: condition=즉시가능|조건부|불가, wait_days=N, source=출처명]
  예: [JUDGMENT: condition=즉시가능, wait_days=0, source=약학정보원]
  예: [JUDGMENT: condition=조건부, wait_days=155, source=헌혈 판정기준]
  이 태그는 시스템이 파싱합니다 — 형식을 변경하지 마세요.
"""


def _extract_judgment(answer_text: str, lang: str = "ko") -> dict:
    """답변 끝의 [JUDGMENT: ...] 태그에서 판정 추출"""
    import re
    match = re.search(
        r'\[JUDGMENT:\s*condition=([^,]+),\s*wait_days=(\d+),\s*source=([^\]]+)\]',
        answer_text
    )
    if match:
        condition = match.group(1).strip()
        wait_days = int(match.group(2))
        source = match.group(3).strip()
        eligible = condition in ("Eligible", "즉시가능")
        return {"eligible": eligible, "condition": condition, "reason": "", "wait_days": wait_days, "citation": source}

    # fallback: 태그 없으면 기본값
    return {"eligible": False, "condition": "Conditional" if lang == "en" else "조건부",
            "reason": "", "wait_days": 0, "citation": ""}


def run_agent(query: str, thinking_enabled: bool = False, thinking_budget: int = 2000, model: str = None, lang: str = "ko"):
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
        {"role": "system", "content": _build_system_prompt(lang)},
        {"role": "user", "content": query},
    ]

    tool_logs = []
    total_tokens = {"input_tokens": 0, "output_tokens": 0}
    thinking_content = None
    answer_text = ""

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

        # 툴 호출이 없으면 루프 종료 — 모델의 텍스트 응답이 answer
        if response.finish_reason != "TOOL_CALL":
            if response.message and response.message.content:
                for block in response.message.content:
                    if hasattr(block, "text") and block.text:
                        answer_text += block.text
            break

        # 툴 호출 처리
        if response.message and response.message.tool_calls:
            messages.append({"role": "assistant", "tool_calls": response.message.tool_calls})

            for tc in response.message.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                result = execute_tool(fn_name, fn_args, lang=lang)

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

    # 판정 추출 (답변 텍스트에서 — API 호출 없음)
    t_judgment = time.time()
    judgment = _extract_judgment(answer_text, lang)
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

    tool_rate_limits = get_rate_limits()
    rate_limits = {
        "chat": {},
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


def run_agent_stream(query: str, thinking_enabled: bool = False, thinking_budget: int = 2000, model: str = None, lang: str = "ko"):
    """에이전트 실행 (실시간 스트리밍): 도구 루프의 content_delta가 답변, judgment는 구조화 필드만"""
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
        {"role": "system", "content": _build_system_prompt(lang)},
        {"role": "user", "content": query},
    ]

    total_tokens = {"input_tokens": 0, "output_tokens": 0}
    step = 0
    answer_text = ""  # content_delta 누적용

    use_thinking = thinking_enabled and model == MODEL_REASONING

    # 2) 툴 호출 루프 — content_delta가 프론트엔드에 실시간 스트리밍됨
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

        tool_calls_buf = []
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
                if text:
                    answer_text += text
                    yield {"type": "content_delta", "text": text}

            elif chunk.type == "message-end":
                finish_reason = chunk.delta.finish_reason
                _collect_tokens(chunk, total_tokens)

        # 스트림 종료 후: 도구 실행
        if finish_reason == "TOOL_CALL" and tool_calls_buf:
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

            for tc_data in tool_calls_buf:
                fn_args = json.loads(tc_data["args_str"]) if tc_data["args_str"] else {}
                result = execute_tool(tc_data["name"], fn_args, lang=lang)
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
            break

    t_tool_elapsed = time.time() - t_tool
    print(f"[TIMING]tool_loop: {t_tool_elapsed:.2f}s ({step} tools)")

    # 3) 판정 추출 (답변 텍스트에서 — API 호출 없음)
    t_judgment = time.time()
    judgment = _extract_judgment(answer_text, lang)
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

    # 4) 완료 먼저 전송 → 프론트엔드가 즉시 답변 확정 (isStreaming=false)
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

    # 5) 판정 카드 — done 이후에 자연스럽게 나타남
    yield {"type": "judgment", "judgment": judgment, "timing": timing}


if __name__ == "__main__":
    print("=== 테스트: 아스피린 질문 ===")
    result = run_agent("아스피린 복용 후 헌혈 가능한가요? 3일 전 325mg 복용했습니다.")
    print(f"답변: {result['answer'][:200]}")
    print(f"판정: {json.dumps(result['judgment'], ensure_ascii=False, indent=2)}")
    print(f"툴 호출: {len(result['tool_logs'])}건")
    for log in result["tool_logs"]:
        print(f"  - {log['tool']}({log['args']})")
    print(f"사용량: {result['total_tokens']}")
