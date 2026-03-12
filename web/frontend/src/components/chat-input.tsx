"use client";

import { useState } from "react";
import { useAppState } from "@/lib/store";
import { useLocale } from "@/lib/locale-context";
import { streamChat } from "@/lib/api";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";

function handleSSEEvent(
  event: { event: string; data: unknown },
  state: ReturnType<typeof useAppState>
) {
  const data = event.data as Record<string, unknown>;

  switch (event.event) {
    case "classification":
      state.setClassification(
        data as unknown as ReturnType<typeof useAppState>["classification"]
      );
      break;
    case "tool_call":
      state.addToolCall(
        data as unknown as ReturnType<typeof useAppState>["toolCalls"][0]
      );
      break;
    case "judgment":
      state.setJudgment(
        data as unknown as ReturnType<typeof useAppState>["judgment"]
      );
      break;
    case "text_delta": {
      const chunk = (data as { text?: string }).text || "";
      state.appendStreamingText(chunk);
      break;
    }
    case "answer":
      state.setAnswer((data as { text?: string }).text || "");
      break;
    case "timing":
      state.setTiming(data as ReturnType<typeof useAppState>["timing"]);
      break;
    case "done":
      if (state.streamingText) {
        state.setAnswer(state.streamingText);
      }
      state.setTokens(
        (data as { total_tokens?: unknown }).total_tokens as ReturnType<
          typeof useAppState
        >["tokens"]
      );
      state.setIsStreaming(false);
      break;
  }
}

export function ChatInput() {
  const [input, setInput] = useState("");
  const state = useAppState();
  const { t } = useLocale();

  const handleSubmit = async () => {
    const query = input.trim();
    if (!query || state.isStreaming) return;

    setInput("");
    state.reset();
    state.setMode("custom");
    state.setQuery(query);
    state.setIsStreaming(true);

    try {
      for await (const event of streamChat({ query })) {
        handleSSEEvent(event, state);
      }
    } catch (err) {
      console.error("Stream error:", err);
    } finally {
      state.setIsStreaming(false);
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3 shadow-[0_-2px_10px_rgba(0,0,0,0.05)]">
      <div className="mx-auto flex max-w-[1440px] items-center gap-3 lg:px-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit();
            }
          }}
          placeholder={t("chat.placeholder")}
          disabled={state.isStreaming}
          className="flex-1 rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm outline-none transition-colors placeholder:text-gray-400 focus:border-navy/40 focus:bg-white disabled:opacity-50"
        />
        <Button
          size="sm"
          onClick={handleSubmit}
          disabled={!input.trim() || state.isStreaming}
          className="h-10 w-10 shrink-0 rounded-lg bg-navy p-0 hover:bg-navy/90 disabled:opacity-30"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
