"use client";

import { motion } from "framer-motion";
import { useAppState } from "@/lib/store";
import { QueryBadge } from "./query-badge";
import { ToolTimeline } from "./tool-timeline";
import { JudgmentCard } from "./judgment-card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { User, Bot, Clock } from "lucide-react";

export function ChatArea() {
  const {
    query,
    isStreaming,
    streamingText,
    toolPlan,
    classification,
    toolCalls,
    judgment,
    answer,
    timing,
    tokens,
  } = useAppState();

  if (!query) return null;

  const displayText = answer || streamingText;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <ScrollArea className="max-h-[calc(100vh-420px)]">
        <div className="space-y-4 p-1">
          {/* Classification badge */}
          {classification && (
            <div className="flex justify-center">
              <QueryBadge classification={classification} />
            </div>
          )}

          {/* User message */}
          <div className="flex justify-end">
            <div className="flex max-w-[85%] items-start gap-2">
              <div className="rounded-2xl rounded-tr-sm bg-navy/5 border border-navy/10 px-4 py-2.5">
                <p className="text-sm text-gray-800 leading-relaxed">{query}</p>
              </div>
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-navy/10">
                <User className="h-3.5 w-3.5 text-navy" />
              </div>
            </div>
          </div>

          {/* Tool plan (model thinking) */}
          {toolPlan && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mx-4"
            >
              <div className="rounded-lg border border-dashed border-gray-200 bg-gray-50/50 px-3 py-2">
                <p className="text-xs text-gray-500 italic leading-relaxed">{toolPlan}</p>
              </div>
            </motion.div>
          )}

          {/* Tool timeline */}
          {toolCalls.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="mx-4"
            >
              <ToolTimeline toolCalls={toolCalls} />
            </motion.div>
          )}

          {/* Judgment */}
          {judgment && (
            <div className="mx-4">
              <JudgmentCard judgment={judgment} />
            </div>
          )}

          {/* Assistant message */}
          {displayText && (
            <div className="flex justify-start">
              <div className="flex max-w-[85%] items-start gap-2">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-green/10">
                  <Bot className="h-3.5 w-3.5 text-brand-green" />
                </div>
                <div className="rounded-2xl rounded-tl-sm border border-gray-200 bg-white px-4 py-2.5 shadow-sm">
                  <div
                    className={`text-sm text-gray-700 leading-relaxed whitespace-pre-wrap ${
                      isStreaming && !answer ? "streaming-cursor" : ""
                    }`}
                  >
                    {formatMarkdown(displayText)}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Timing bar */}
          {timing && !isStreaming && (
            <motion.div
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="mx-4"
            >
              <div className="flex items-center gap-3 rounded-lg border border-gray-100 bg-gray-50 px-3 py-2">
                <Clock className="h-3 w-3 text-gray-400 shrink-0" />
                <div className="flex items-center gap-2 text-[10px] text-gray-500 font-mono">
                  <span>classify {timing.classify}s</span>
                  <span className="text-gray-300">→</span>
                  <span>tools {timing.tool_loop}s</span>
                  <span className="text-gray-300">→</span>
                  <span>judgment {timing.judgment}s</span>
                  <span className="text-gray-300">=</span>
                  <span className="font-semibold text-navy">{timing.total}s</span>
                </div>
                {tokens && (
                  <span className="ml-auto text-[10px] text-gray-400">
                    {tokens.input_tokens + tokens.output_tokens} tokens
                  </span>
                )}
              </div>
            </motion.div>
          )}

          {/* Loading indicator */}
          {isStreaming && !displayText && toolCalls.length === 0 && (
            <div className="flex justify-start">
              <div className="flex items-start gap-2">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-green/10">
                  <Bot className="h-3.5 w-3.5 text-brand-green" />
                </div>
                <div className="rounded-2xl rounded-tl-sm border border-gray-200 bg-white px-4 py-3 shadow-sm">
                  <div className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:0ms]" />
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:150ms]" />
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-400 animate-bounce [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
    </motion.div>
  );
}

function formatMarkdown(text: string): React.ReactNode {
  // Simple bold formatting: **text**
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-gray-900">
          {part.slice(2, -2)}
        </strong>
      );
    }
    // Handle > blockquotes
    if (part.startsWith("> ")) {
      return (
        <span key={i} className="block border-l-2 border-gray-300 pl-3 italic text-gray-500 my-1">
          {part.slice(2)}
        </span>
      );
    }
    return part;
  });
}
