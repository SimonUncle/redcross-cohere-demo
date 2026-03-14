const API_BASE = "http://localhost:7070";

// --- Types ---

export interface SSEEvent {
  event: string;
  data: unknown;
}

export interface ChatMessage {
  query: string;
  model?: string;
  lang?: string;
}

export interface ToolCall {
  tool: string;
  args: Record<string, string>;
  result?: string;
  status?: "running" | "done" | "error";
}

export interface JudgmentResult {
  status?: "즉시가능" | "조건부" | "불가";
  condition?: "즉시가능" | "조건부" | "불가";
  eligible?: boolean;
  reason: string;
  wait_days?: number;
  conditions?: string[];
  citation?: string;
}

export interface ClassificationResult {
  type?: "단순" | "복합";
  complexity?: "단순" | "복합";
  model: string;
  keywords?: string[];
  matched_keywords?: string[];
  thinking?: boolean;
  reason?: string;
}

export interface ChatResponse {
  classification?: ClassificationResult;
  tool_calls?: ToolCall[];
  judgment?: JudgmentResult;
  answer?: string;
  tokens?: TokenUsage;
  timing?: { classify: number; tool_loop: number; judgment: number; total: number };
}

export interface CompareResult {
  command_a: ChatResponse;
  reasoning: ChatResponse;
}

export interface VisionResult {
  ocr_text: string;
  extracted_info: Record<string, string>;
  pipeline_result?: ChatResponse;
}

export interface TranslateResult {
  original: string;
  translated_query: string;
  pipeline_result?: ChatResponse;
  translated_answer: string;
}

export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  search_units?: number;
}

// --- SSE Streaming ---

export async function* streamChat(
  msg: ChatMessage,
  signal?: AbortSignal
): AsyncGenerator<SSEEvent, void, unknown> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(msg),
    signal,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    if (signal?.aborted) return;
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let currentEvent = "message";
    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        if (signal?.aborted) return;
        const dataStr = line.slice(5).trim();
        if (dataStr) {
          try {
            const data = JSON.parse(dataStr);
            yield { event: currentEvent, data };
          } catch {
            yield { event: currentEvent, data: dataStr };
          }
        }
      }
    }
  }
}

// --- Compare Models ---

export async function fetchCompare(query: string, lang?: string): Promise<CompareResult> {
  const response = await fetch(`${API_BASE}/api/chat/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, lang: lang || "ko" }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// --- Vision ---

export async function analyzeVision(file: File, signal?: AbortSignal): Promise<VisionResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/vision`, {
    method: "POST",
    body: formData,
    signal,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// --- Translate ---

export async function* streamTranslate(
  text: string,
  direction: string
): AsyncGenerator<SSEEvent, void, unknown> {
  const response = await fetch(`${API_BASE}/api/translate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, direction }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let currentEvent = "message";
    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        const dataStr = line.slice(5).trim();
        if (dataStr) {
          try {
            const data = JSON.parse(dataStr);
            yield { event: currentEvent, data };
          } catch {
            yield { event: currentEvent, data: dataStr };
          }
        }
      }
    }
  }
}
