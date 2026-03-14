"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";
import { useAppState } from "@/lib/store";
import { ToolTimeline } from "./tool-timeline";
import { JudgmentCard } from "./judgment-card";
import { Separator } from "@/components/ui/separator";
import { useState } from "react";
import { ChevronDown, ChevronRight, User } from "lucide-react";
import type { ChatResponse } from "@/lib/api";
import { useLocale } from "@/lib/locale-context";

export function ModelCompare() {
  const { compareResult, query, isStreaming } = useAppState();
  const { t } = useLocale();

  if (!compareResult && !isStreaming) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-4"
    >
      {/* User query */}
      {query && (
        <div className="flex justify-end">
          <div className="flex max-w-[90%] items-start gap-2">
            <div className="rounded-2xl rounded-tr-sm bg-navy/5 border border-navy/10 px-4 py-2.5">
              <p className="text-sm text-gray-800 leading-relaxed">{query}</p>
            </div>
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-navy/10">
              <User className="h-3.5 w-3.5 text-navy" />
            </div>
          </div>
        </div>
      )}

      {/* Loading */}
      {isStreaming && !compareResult && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-navy border-t-transparent" />
            {t("compare.loading")}
          </div>
        </div>
      )}

      {/* Side by side */}
      {compareResult && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <ModelPanel
            title="Command A"
            headerColor="bg-gray-500"
            data={compareResult.command_a}
            showThinking={false}
          />
          <ModelPanel
            title="A Reasoning"
            headerColor="bg-navy"
            data={compareResult.reasoning}
            showThinking={true}
          />
        </div>
      )}
    </motion.div>
  );
}

function ModelPanel({
  title,
  headerColor,
  data,
  showThinking,
}: {
  title: string;
  headerColor: string;
  data: ChatResponse;
  showThinking: boolean;
}) {
  const [thinkingOpen, setThinkingOpen] = useState(false);
  const { t } = useLocale();

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="overflow-hidden">
        <CardHeader
          className={`${headerColor} py-2.5 px-4 text-white`}
        >
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-semibold">{title}</CardTitle>
            <div className="flex items-center gap-2">
              {data.timing?.total && (
                <span className="text-[10px] text-white/70">
                  {data.timing.total}s
                </span>
              )}
              {data.tokens && (
                <span className="text-[10px] text-white/70">
                  {data.tokens.input_tokens + data.tokens.output_tokens} tok
                </span>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-4">
          <div className="space-y-3">
              {/* Thinking section (Reasoning only) */}
              {showThinking && (
                <div
                  className="cursor-pointer rounded-md border border-navy/10 bg-navy/5 p-2.5"
                  onClick={() => setThinkingOpen(!thinkingOpen)}
                >
                  <div className="flex items-center gap-2 text-xs font-medium text-navy">
                    {thinkingOpen ? (
                      <ChevronDown className="h-3 w-3" />
                    ) : (
                      <ChevronRight className="h-3 w-3" />
                    )}
                    Thinking Process
                  </div>
                  {thinkingOpen && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="mt-2 text-xs text-gray-600 leading-relaxed"
                    >
                      {t("compare.thinking")}
                    </motion.div>
                  )}
                </div>
              )}

              {/* Tool calls */}
              {data.tool_calls && data.tool_calls.length > 0 && (
                <ToolTimeline toolCalls={data.tool_calls} />
              )}

              <Separator />

              {/* Judgment */}
              {data.judgment && <JudgmentCard judgment={data.judgment} />}

              {/* Answer */}
              {data.answer && (
                <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                  {data.answer.split(/(\*\*[^*]+\*\*)/g).map((part, i) => {
                    if (part.startsWith("**") && part.endsWith("**")) {
                      return (
                        <strong key={i} className="font-semibold text-gray-900">
                          {part.slice(2, -2)}
                        </strong>
                      );
                    }
                    if (part.startsWith("> ")) {
                      return (
                        <span
                          key={i}
                          className="block border-l-2 border-gray-300 pl-3 italic text-gray-500 my-1"
                        >
                          {part.slice(2)}
                        </span>
                      );
                    }
                    return part;
                  })}
                </div>
              )}
            </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
