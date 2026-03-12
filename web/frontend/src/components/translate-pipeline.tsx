"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";
import { useAppState } from "@/lib/store";
import { streamTranslate } from "@/lib/api";
import { useState, useRef, useEffect, useCallback } from "react";
import {
  ArrowRight,
  Languages,
  Loader2,
  Search,
  FileCheck,
} from "lucide-react";
import { JudgmentCard } from "./judgment-card";
import { useLocale } from "@/lib/locale-context";

export function TranslatePipeline() {
  const { mode, translateSteps, setTranslateSteps } = useAppState();
  const { t } = useLocale();
  const [input, setInput] = useState(
    "I took aspirin 3 days ago. Can I donate blood?"
  );
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [judgment, setJudgment] = useState<{
    status: "즉시가능" | "조건부" | "불가";
    reason: string;
    wait_days?: number;
  } | null>(null);

  const stepsRef = useRef<{ step: number; label: string; content: string }[]>([]);
  const hasAutoRun = useRef(false);

  const handleTranslate = useCallback(async () => {
    if (!input.trim() || isProcessing) return;
    setIsProcessing(true);
    setTranslateSteps([]);
    stepsRef.current = [];
    setJudgment(null);
    setCurrentStep(0);

    try {
      let hasResults = false;
      for await (const event of streamTranslate(input, "en_to_kr")) {
        const data = event.data as Record<string, unknown>;
        if (event.event === "step") {
          hasResults = true;
          setCurrentStep(
            (data.step as number) || 0
          );
          stepsRef.current = [
            ...stepsRef.current,
            {
              step: (data.step as number) || 0,
              label: (data.label as string) || "",
              content: (data.content as string) || "",
            },
          ];
          setTranslateSteps(stepsRef.current);
        } else if (event.event === "judgment") {
          hasResults = true;
          setJudgment(
            data as unknown as typeof judgment
          );
        }
      }
      if (!hasResults) throw new Error("No SSE events received");
    } catch {
      // Simulate pipeline
      setCurrentStep(1);
      stepsRef.current = [
        {
          step: 1,
          label: "EN → KR 번역",
          content:
            "3일 전에 아스피린을 복용했습니다. 헌혈할 수 있나요?",
        },
      ];
      setTranslateSteps(stepsRef.current);
      await new Promise((r) => setTimeout(r, 1000));

      setCurrentStep(2);
      stepsRef.current = [
        ...stepsRef.current,
        {
          step: 2,
          label: "검색 + 판정",
          content:
            "아스피린(아세틸살리실산) 복용 후 전혈헌혈 3일 경과 후 가능. → 즉시가능 판정",
        },
      ];
      setTranslateSteps(stepsRef.current);
      await new Promise((r) => setTimeout(r, 800));

      setJudgment({
        status: "즉시가능",
        reason:
          "아스피린 복용 후 3일이 경과하여 전혈헌혈이 가능합니다.",
      });
      await new Promise((r) => setTimeout(r, 800));

      setCurrentStep(3);
      stepsRef.current = [
        ...stepsRef.current,
        {
          step: 3,
          label: "KR → EN 번역",
          content:
            "You took aspirin 3 days ago. According to the guidelines, whole blood donation is possible after 3 days from the last aspirin intake.\n\n**Result: Eligible for immediate donation.**\n\nNote: For platelet donation (apheresis), a 7-day waiting period is required.",
        },
      ];
      setTranslateSteps(stepsRef.current);
    } finally {
      setIsProcessing(false);
    }
  }, [input, isProcessing, setTranslateSteps]);

  // Auto-run on mount
  useEffect(() => {
    if (mode === "demo3-translate" && !hasAutoRun.current) {
      hasAutoRun.current = true;
      handleTranslate();
    }
  }, [mode, handleTranslate]);

  if (mode !== "demo3-translate") return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <CardTitle className="text-base text-dark-green">
              {t("translate.title")}
            </CardTitle>
            <Badge className="bg-dark-green/10 text-dark-green border-dark-green/20 text-xs">
              Extension
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Input */}
          <div className="flex gap-2">
            <div className="flex-1">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter your question in English..."
                className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm outline-none focus:border-dark-green/50 focus:ring-1 focus:ring-dark-green/20"
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleTranslate();
                }}
              />
            </div>
            <Button
              onClick={handleTranslate}
              disabled={isProcessing}
              className="bg-dark-green hover:bg-dark-green/90"
            >
              {isProcessing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Languages className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Pipeline Steps */}
          <AnimatePresence>
            {translateSteps.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-3"
              >
                {/* Step visualization */}
                <div className="flex items-center justify-center gap-2 py-2">
                  <StepIndicator
                    step={1}
                    label="EN → KR"
                    icon={<Languages className="h-3.5 w-3.5" />}
                    active={currentStep >= 1}
                    current={currentStep === 1 && isProcessing}
                  />
                  <ArrowRight className="h-4 w-4 text-gray-300" />
                  <StepIndicator
                    step={2}
                    label={t("translate.step_search")}
                    icon={<Search className="h-3.5 w-3.5" />}
                    active={currentStep >= 2}
                    current={currentStep === 2 && isProcessing}
                  />
                  <ArrowRight className="h-4 w-4 text-gray-300" />
                  <StepIndicator
                    step={3}
                    label="KR → EN"
                    icon={<FileCheck className="h-3.5 w-3.5" />}
                    active={currentStep >= 3}
                    current={currentStep === 3 && isProcessing}
                  />
                </div>

                {/* Step results */}
                {translateSteps.map((s, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.15 }}
                    className={`rounded-lg border p-3 ${
                      s.step === 1 || s.step === 3
                        ? "border-dark-green/20 bg-dark-green/5"
                        : "border-gray-200 bg-white"
                    }`}
                  >
                    <p className="mb-1.5 text-[10px] font-bold uppercase tracking-wider text-gray-400">
                      Step {s.step}: {s.label}
                    </p>
                    <p
                      className={`text-sm leading-relaxed whitespace-pre-wrap ${
                        s.step === 1 || s.step === 3
                          ? "text-dark-green"
                          : "text-gray-700"
                      }`}
                    >
                      {s.content.split(/(\*\*[^*]+\*\*)/g).map((part, j) => {
                        if (part.startsWith("**") && part.endsWith("**")) {
                          return (
                            <strong key={j} className="font-semibold">
                              {part.slice(2, -2)}
                            </strong>
                          );
                        }
                        return part;
                      })}
                    </p>
                  </motion.div>
                ))}

                {/* Judgment */}
                {judgment && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <JudgmentCard judgment={judgment} />
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </motion.div>
  );
}

function StepIndicator({
  step,
  label,
  icon,
  active,
  current,
}: {
  step: number;
  label: string;
  icon: React.ReactNode;
  active: boolean;
  current: boolean;
}) {
  return (
    <div
      className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
        current
          ? "bg-dark-green text-white shadow-md"
          : active
          ? "bg-dark-green/10 text-dark-green"
          : "bg-gray-100 text-gray-400"
      }`}
    >
      {current ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : icon}
      <span>
        {step}. {label}
      </span>
    </div>
  );
}
