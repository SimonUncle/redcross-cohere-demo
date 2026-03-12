"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { ToolCall } from "@/lib/api";
import { useState } from "react";
import { ChevronDown, ChevronRight, Loader2, CheckCircle2, XCircle } from "lucide-react";

interface ToolTimelineProps {
  toolCalls: ToolCall[];
}

export function ToolTimeline({ toolCalls }: ToolTimelineProps) {
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  if (toolCalls.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-0"
    >
      <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
        Tool Calls
      </p>
      <div className="relative ml-2.5">
        {/* Vertical line */}
        <div className="absolute left-0 top-2 bottom-2 w-px bg-gray-200" />

        <AnimatePresence>
          {toolCalls.map((tc, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.15, duration: 0.3 }}
              className="relative mb-3 pl-6"
            >
              {/* Dot */}
              <div className="absolute left-0 top-2 -translate-x-1/2">
                {tc.status === "running" ? (
                  <Loader2 className="h-3.5 w-3.5 text-brand-blue animate-spin" />
                ) : tc.status === "error" ? (
                  <XCircle className="h-3.5 w-3.5 text-brand-red" />
                ) : (
                  <CheckCircle2 className="h-3.5 w-3.5 text-brand-green" />
                )}
              </div>

              {/* Content */}
              <div className="rounded-md border border-gray-100 bg-white p-2.5 shadow-sm">
                <div
                  className="flex cursor-pointer items-center gap-2"
                  onClick={() =>
                    setExpanded((prev) => ({ ...prev, [i]: !prev[i] }))
                  }
                >
                  <span className="text-[10px] font-medium text-gray-400">
                    Step {i + 1}
                  </span>
                  <code className="text-xs font-semibold text-navy">
                    {tc.tool}
                  </code>
                  <code className="text-[10px] text-gray-400">
                    ({Object.values(tc.args).join(", ")})
                  </code>
                  <div className="ml-auto">
                    {tc.result ? (
                      expanded[i] ? (
                        <ChevronDown className="h-3 w-3 text-gray-400" />
                      ) : (
                        <ChevronRight className="h-3 w-3 text-gray-400" />
                      )
                    ) : null}
                  </div>
                </div>

                <AnimatePresence>
                  {expanded[i] && tc.result && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-2 overflow-hidden"
                    >
                      <div className="rounded bg-gray-50 px-2.5 py-2 text-xs text-gray-600 leading-relaxed border border-gray-100">
                        {tc.result}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
