import type { MutableRefObject } from "react";
import type { AppState, DemoMode } from "./store";
import { streamChat } from "./api";

/**
 * 공통 SSE 이벤트 핸들러
 * api.py가 content_delta → text_delta로 변환하므로 content_delta 핸들러 불필요
 */
export function handleSSEEvent(
  event: { event: string; data: unknown },
  state: AppState
) {
  const data = event.data as Record<string, unknown>;

  switch (event.event) {
    case "classification":
      state.setClassification(data as unknown as AppState["classification"]);
      break;

    case "tool_call": {
      const tc = data as {
        step?: number;
        status?: string;
        tool?: string;
        args?: Record<string, string>;
        result?: string;
      };
      if (tc.status === "running") {
        state.addToolCall({
          tool: tc.tool || "",
          args: tc.args || {},
          status: "running",
        });
      } else if (tc.status === "done") {
        state.updateToolCall((tc.step || 1) - 1, {
          result: tc.result,
          status: "done",
        });
      } else {
        state.addToolCall(tc as unknown as AppState["toolCalls"][0]);
      }
      break;
    }

    case "tool_result": {
      const idx = (data as { index?: number }).index ?? state.toolCalls.length - 1;
      state.updateToolCall(idx, {
        result: (data as { result?: string }).result,
        status: "done",
      });
      break;
    }

    case "judgment":
      state.setJudgment(data as unknown as AppState["judgment"]);
      break;

    case "text_delta":
    case "stream": {
      const chunk = (data as { text?: string }).text || "";
      state.appendStreamingText(chunk);
      break;
    }

    case "tool_plan":
      state.appendToolPlan((data as { text?: string }).text || "");
      break;

    case "thinking":
    case "citation":
      break;

    case "answer":
      state.setAnswer((data as { text?: string }).text || "");
      break;

    case "timing":
      state.setTiming(data as AppState["timing"]);
      break;

    case "tokens":
      state.setTokens(data as unknown as AppState["tokens"]);
      break;

    case "done": {
      // answer 설정은 runStream의 finally에서 로컬 변수로 처리 (stale closure 방지)
      const doneData = data as { total_tokens?: unknown };
      if (doneData.total_tokens) {
        state.setTokens(doneData.total_tokens as AppState["tokens"]);
      }
      break;
    }
  }
}

/**
 * 스트리밍 실행 헬퍼 — abort, reset, stream, event handling, cleanup 통합
 * demo-cards.tsx, chat-input.tsx에서 공유
 */
export async function runStream(opts: {
  query: string;
  lang: string;
  mode: DemoMode;
  state: AppState;
  abortRef: MutableRefObject<AbortController | null>;
  fallback?: (state: AppState) => Promise<void>;
}) {
  const { query, lang, mode, state, abortRef, fallback } = opts;

  abortRef.current?.abort();
  const controller = new AbortController();
  abortRef.current = controller;

  state.reset();
  state.setMode(mode);
  state.setQuery(query);
  state.setIsStreaming(true);

  let localText = "";

  try {
    for await (const event of streamChat({ query, lang }, controller.signal)) {
      if (controller.signal.aborted) break;
      handleSSEEvent(event, state);
      // 로컬에서 text 추적 (stale closure 방지)
      if (event.event === "text_delta" || event.event === "stream") {
        localText += ((event.data as Record<string, unknown>).text as string) || "";
      }
    }
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") return;
    console.error("Stream error:", err);
    if (fallback) await fallback(state);
  } finally {
    if (localText) {
      state.setAnswer(localText);
    }
    state.setIsStreaming(false);
  }
}
