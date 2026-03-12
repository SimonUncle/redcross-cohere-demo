"""에이전트 툴 3개 정의 + 실행 함수"""

import os
import time
import cohere
import chromadb
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
COLLECTION_NAME = "blood_donation_guidelines"

co = cohere.ClientV2()
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_collection(name=COLLECTION_NAME)

# 마지막 API 호출의 rate limit 정보 저장
_last_rate_limits = {"embed": {}, "rerank": {}}


def _extract_limits(headers) -> dict:
    """응답 헤더에서 rate limit 정보 추출"""
    return {
        "monthly_limit": int(headers.get("x-endpoint-monthly-call-limit", 0)),
        "trial_limit": int(headers.get("x-trial-endpoint-call-limit", 0)),
        "trial_remaining": int(headers.get("x-trial-endpoint-call-remaining", 0)),
    }


def get_rate_limits() -> dict:
    """마지막 embed/rerank 호출의 rate limit 반환"""
    return dict(_last_rate_limits)

# 툴 스키마 정의
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_guideline",
            "description": "헌혈 판정기준 문서에서 관련 내용 검색. Embed v4 + Rerank 4.0 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색 키워드 (한국어)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_drug_info",
            "description": "판정기준 문서에서 약물의 헌혈 유예 정보 검색. 약물명이 포함된 질문에 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "약물명 (한국어, 예: 아스피린)"}
                },
                "required": ["drug_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_malaria_risk",
            "description": "여행 지역의 말라리아 위험도 및 헌혈 유예기간 조회. 여행력 언급 시 사용.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "국가 또는 지역명 (예: 인도네시아 발리)"}
                },
                "required": ["region"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_wait_days",
            "description": "헌혈 유예기간 남은 일수를 정확히 계산. 날짜 계산이 필요할 때 반드시 이 도구를 사용하세요. 직접 계산하지 마세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "deferral_days": {"type": "integer", "description": "유예기간 (일수, 예: 365)"},
                    "elapsed_days": {"type": "integer", "description": "경과일수 (예: 21)"}
                },
                "required": ["deferral_days", "elapsed_days"]
            }
        }
    }
]


SOURCE_DISPLAY_NAMES = {
    "guideline_drug.pdf": "약학정보원",
    "guideline_malaria.pdf": "질병관리청",
    "guideline_main.pdf": "헌혈 판정기준",
}


def search_guideline(query: str) -> str:
    """Embed v4로 검색 → Rerank 4.0으로 재랭킹 → 상위 3개 반환"""
    # Embed v4로 쿼리 임베딩
    t0 = time.time()
    embed_raw = co.with_raw_response.embed(
        texts=[query],
        model="embed-v4.0",
        input_type="search_query",
        embedding_types=["float"],
    )
    _last_rate_limits["embed"] = _extract_limits(embed_raw.headers)
    query_emb = embed_raw.data.embeddings.float_[0]
    print(f"[TIMING]   embed: {time.time()-t0:.2f}s")

    # ChromaDB 검색 (상위 10개)
    t1 = time.time()
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=min(10, collection.count()),
    )
    print(f"[TIMING]   chromadb: {time.time()-t1:.2f}s")

    if not results["documents"][0]:
        return "관련 문서를 찾을 수 없습니다."

    # Rerank 4.0으로 재랭킹
    docs = results["documents"][0]
    metadatas = results["metadatas"][0]

    t2 = time.time()
    rerank_raw = co.with_raw_response.rerank(
        model="rerank-v4.0-pro",
        query=query,
        documents=docs,
        top_n=3,
    )
    _last_rate_limits["rerank"] = _extract_limits(rerank_raw.headers)
    rerank_results = rerank_raw.data
    print(f"[TIMING]   rerank: {time.time()-t2:.2f}s")

    output_parts = []
    for r in rerank_results.results:
        idx = r.index
        meta = metadatas[idx]
        output_parts.append(
            f"[출처: {SOURCE_DISPLAY_NAMES.get(meta['source'], meta['source'])}] (관련도: {r.relevance_score:.3f})\n{docs[idx]}"
        )

    return "\n\n---\n\n".join(output_parts)


def search_relevance_top1(query: str) -> float:
    """쿼리로 검색 후 rerank top-1 relevance score만 반환 (비교용)"""
    embed_resp = co.embed(
        texts=[query],
        model="embed-v4.0",
        input_type="search_query",
        embedding_types=["float"],
    )
    query_emb = embed_resp.embeddings.float_[0]
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=min(10, collection.count()),
    )
    if not results["documents"][0]:
        return 0.0
    docs = results["documents"][0]
    rerank_resp = co.rerank(
        model="rerank-v4.0-pro",
        query=query,
        documents=docs,
        top_n=1,
    )
    return rerank_resp.results[0].relevance_score if rerank_resp.results else 0.0


def search_drug_info(drug_name: str) -> str:
    """판정기준 문서에서 약물 유예 정보 검색"""
    return search_guideline(f"{drug_name} 헌혈 유예기간 채혈 가능 여부")


def check_malaria_risk(region: str) -> str:
    """말라리아 위험도 조회 — 판정기준 문서에서 지역 정보 검색"""
    return search_guideline(f"{region} 말라리아 위험등급 유예기간 헌혈")


def calculate_wait_days(deferral_days: int, elapsed_days: int) -> str:
    """유예기간 남은 일수를 정확히 계산"""
    remaining = deferral_days - elapsed_days
    if remaining <= 0:
        return f"유예기간 경과 완료. 경과일({elapsed_days}일) >= 유예기간({deferral_days}일). 헌혈 가능합니다."
    else:
        return f"남은 대기일: {remaining}일. 경과일({elapsed_days}일) / 유예기간({deferral_days}일). 아직 헌혈 불가합니다."


# 툴 이름 → 실행 함수 매핑
TOOL_FUNCTIONS = {
    "search_guideline": search_guideline,
    "search_drug_info": search_drug_info,
    "check_malaria_risk": check_malaria_risk,
    "calculate_wait_days": calculate_wait_days,
}


def execute_tool(name: str, args: dict) -> str:
    """툴 이름과 인자로 실행"""
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return f"알 수 없는 툴: {name}"
    return fn(**args)


if __name__ == "__main__":
    print("=== search_guideline 테스트 ===")
    print(search_guideline("아스피린 헌혈"))
    print("\n=== search_drug_info 테스트 ===")
    print(search_drug_info("아스피린"))
    print("\n=== check_malaria_risk 테스트 ===")
    print(check_malaria_risk("인도네시아 발리"))
