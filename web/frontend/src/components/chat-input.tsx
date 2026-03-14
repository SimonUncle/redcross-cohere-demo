"use client";

import { useState, useRef } from "react";
import { useAppState } from "@/lib/store";
import { useLocale } from "@/lib/locale-context";
import { runStream } from "@/lib/sse-handler";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";

export function ChatInput() {
  const [input, setInput] = useState("");
  const state = useAppState();
  const { t, locale } = useLocale();
  const abortRef = useRef<AbortController | null>(null);

  const handleSubmit = async () => {
    const query = input.trim();
    if (!query || state.isStreaming) return;
    setInput("");
    await runStream({
      query, lang: locale, mode: "custom", state, abortRef,
    });
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
