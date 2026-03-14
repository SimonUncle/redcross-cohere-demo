"""쿼리 복잡도 분류기 — 자동 모델 라우팅"""

MODEL_FAST = "command-a-03-2025"
MODEL_REASONING = "command-a-reasoning-08-2025"

# 복합 조건 키워드
COMPLEX_INDICATORS = [
    # 복수 조건 연결 (KO)
    "그리고", "또한", "동시에", "+",
    # 여행 관련 (KO)
    "여행", "다녀왔", "방문", "출국", "귀국", "해외",
    # 복합 의료 조건 (KO)
    "혈압", "당뇨", "수술", "수혈", "임신",
    # 복수 조건 연결 (EN)
    " and ", "also", "both", "plus",
    # 여행 관련 (EN)
    "travel", "traveled", "travelled", "visited", "trip", "abroad",
    # 복합 의료 조건 (EN)
    "blood pressure", "diabetes", "surgery", "transfusion", "pregnant", "medication",
]

# 여행 기간 키워드 (여행 + 기간 조합 → 복합)
TRAVEL_PERIOD_KEYWORDS = [
    # KO
    "개월", "주", "일", "전", "후", "기간",
    # EN
    "month", "week", "day", "ago", "before", "after", "period",
]


def classify_query(query: str) -> dict:
    """쿼리 복잡도를 분류하여 모델을 자동 선택.

    규칙 기반 분류기 (LLM 호출 없이 즉시 분류).
    PoC에서 실제 쿼리 데이터 확보 후 ML 기반으로 교체 가능.
    """
    query_lower_for_match = query.lower()
    matched = [k for k in COMPLEX_INDICATORS if k in query or k.lower() in query_lower_for_match]
    query_lower = query.lower()
    has_travel = any(k in query for k in ["여행", "다녀왔", "방문", "출국", "귀국", "해외"]) or \
                 any(k in query_lower for k in ["travel", "traveled", "travelled", "visited", "trip", "abroad"])
    has_period = any(k in query or k in query_lower for k in TRAVEL_PERIOD_KEYWORDS)

    is_complex = len(matched) >= 2 or (has_travel and has_period)

    return {
        "complexity": "복합" if is_complex else "단순",
        "model": MODEL_REASONING if is_complex else MODEL_FAST,
        "thinking": is_complex,
        "matched_keywords": matched,
        "reason": f"키워드 {len(matched)}개 매칭" + (", 여행+기간 조합" if has_travel and has_period else "") if matched else "단일 조건",
    }
