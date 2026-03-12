export const ko = {
  // Header
  "header.title": "대한적십자사 헌혈 문진 AI",

  // Sidebar
  "sidebar.simple_query": "단순 질의 처리",
  "sidebar.complex_analysis": "복합 조건 분석",
  "sidebar.vector_search": "가이드라인 벡터 검색",
  "sidebar.reranking": "검색 결과 재순위화",
  "sidebar.dev_metrics": "개발자 메트릭",
  "sidebar.token_usage": "토큰 사용량",
  "sidebar.placeholder": "데모 실행 후 표시됩니다",

  // Page
  "page.demo1a": "Demo 1a: 약물 조회",
  "page.demo1b": "Demo 1b: 조건부",
  "page.demo2": "Demo 2: 모델 비교",
  "page.demo3_vision": "Demo 3: Vision",
  "page.demo3_translate": "Demo 3: 번역",
  "page.custom": "자유 질문",
  "page.reset": "초기화",

  // Demo cards
  "demo.1a.title": "Demo 1a: 약물 조회",
  "demo.1a.badge": "즉시가능",
  "demo.1a.desc": "아스피린 복용 후 헌혈 가능 여부",
  "demo.1a.query_preview": "아스피린 복용 후 헌혈 가능한가요?",

  "demo.1b.title": "Demo 1b: 조건부",
  "demo.1b.badge": "조건부",
  "demo.1b.desc": "문신 시술 후 헌혈 가능 여부",
  "demo.1b.query_preview": "지난달에 문신을 했는데 헌혈 가능한가요?",

  "demo.2.title": "Demo 2: 모델 비교",
  "demo.2.desc": "Command A vs A Reasoning 사이드바이사이드",
  "demo.2.query_preview": "파푸아뉴기니 귀국 + 아스피린 복용",

  "demo.3.title": "Demo 3: 확장 Feasibility",
  "demo.3.desc": "Vision OCR 및 다국어 지원 확장",

  "demo.extra.badge": "추가",
  "demo.extra.title": "복합 조건",
  "demo.extra.query_preview": "고혈압 약 복용 + 혈압 158mmHg",

  // Classification
  "classification.simple": "단순",
  "classification.complex": "복합",

  // Judgment
  "judgment.eligible": "즉시가능",
  "judgment.conditional": "조건부",
  "judgment.ineligible": "불가",
  "judgment.wait_days": "대기: {days}일",

  // Chat input
  "chat.placeholder": "헌혈 관련 질문을 입력하세요...",

  // Model compare
  "compare.loading": "두 모델을 동시에 실행 중...",
  "compare.thinking": "복합 조건 감지 → 각 조건 독립 검색\n→ 교차 분석 → 최종 판정",

  // Vision
  "vision.title": "Vision 구조화 처방전 분석",
  "vision.input_image": "입력 이미지",
  "vision.analyzing": "Vision 구조화 분석 중...",
  "vision.result": "Vision 추출 결과",
  "vision.pipeline_result": "파이프라인 분석 결과",
  "vision.timing": "Vision 분석 + 파이프라인",

  // Translate pipeline
  "translate.title": "다국어 번역 파이프라인",
  "translate.step_en_to_kr": "EN → KR 번역",
  "translate.step_search": "검색 + 판정",
  "translate.step_kr_to_en": "KR → EN 번역",

  // Common
  "common.conditional_note": "추가 확인이 필요한 조건입니다. 헌혈의집 방문 시 상담을 권장합니다.",
} as const;

export type LocaleKey = keyof typeof ko;
