import type { LocaleKey } from "./ko";

export const en: Record<LocaleKey, string> = {
  // Header
  "header.title": "Korean Red Cross Blood Donation AI",

  // Sidebar
  "sidebar.simple_query": "Simple Query Processing",
  "sidebar.complex_analysis": "Complex Condition Analysis",
  "sidebar.vector_search": "Guideline Vector Search",
  "sidebar.reranking": "Search Result Reranking",
  "sidebar.dev_metrics": "Developer Metrics",
  "sidebar.token_usage": "Token Usage",
  "sidebar.placeholder": "Shown after running demo",

  // Page
  "page.demo1a": "Demo 1a: Drug Lookup",
  "page.demo1b": "Demo 1b: Conditional",
  "page.demo2": "Demo 2: Model Compare",
  "page.demo3_vision": "Demo 3: Vision",
  "page.demo3_translate": "Demo 3: Translate",
  "page.custom": "Free Question",
  "page.reset": "Reset",

  // Demo cards
  "demo.1a.title": "Demo 1a: Drug Lookup",
  "demo.1a.badge": "Eligible",
  "demo.1a.desc": "Blood donation eligibility after aspirin",
  "demo.1a.query_preview": "Can I donate blood after taking aspirin?",

  "demo.1b.title": "Demo 1b: Conditional",
  "demo.1b.badge": "Conditional",
  "demo.1b.desc": "Blood donation eligibility after tattoo",
  "demo.1b.query_preview": "Got a tattoo last month, can I donate?",

  "demo.2.title": "Demo 2: Model Compare",
  "demo.2.desc": "Command A vs A Reasoning side-by-side",
  "demo.2.query_preview": "Papua New Guinea travel + aspirin",

  "demo.3.title": "Demo 3: Extension Feasibility",
  "demo.3.desc": "Vision OCR & multilingual support",

  "demo.extra.badge": "Extra",
  "demo.extra.title": "Complex Conditions",
  "demo.extra.query_preview": "BP medication + BP 158mmHg",

  // Classification
  "classification.simple": "Simple",
  "classification.complex": "Complex",

  // Judgment
  "judgment.eligible": "Eligible",
  "judgment.conditional": "Conditional",
  "judgment.ineligible": "Ineligible",
  "judgment.wait_days": "Wait: {days} days",
  "judgment.source": "Source",

  // Chat input
  "chat.placeholder": "Ask a blood donation question...",

  // Model compare
  "compare.loading": "Running both models simultaneously...",
  "compare.thinking": "Detect complex conditions → Independent search\n→ Cross analysis → Final judgment",

  // Vision
  "vision.title": "Vision Structured Prescription Analysis",
  "vision.input_image": "Input Image",
  "vision.analyzing": "Analyzing with Vision...",
  "vision.result": "Vision Extraction Result",
  "vision.pipeline_result": "Pipeline Analysis Result",
  "vision.timing": "Vision analysis + pipeline",

  // Translate pipeline
  "translate.title": "Multilingual Translation Pipeline",
  "translate.step_en_to_kr": "EN → KR Translation",
  "translate.step_search": "Search + Judgment",
  "translate.step_kr_to_en": "KR → EN Translation",

  // Common
  "common.conditional_note": "Additional verification needed. Please consult at the donation center.",
};
