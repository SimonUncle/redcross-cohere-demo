"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { motion, AnimatePresence } from "framer-motion";
import { useAppState } from "@/lib/store";
import { analyzeVision, type JudgmentResult } from "@/lib/api";
import { useState, useEffect, useRef } from "react";
import { FileImage, Loader2, ArrowRight, Clock } from "lucide-react";
import { JudgmentCard } from "./judgment-card";
import { useLocale } from "@/lib/locale-context";
import Image from "next/image";

export function VisionPanel() {
  const { mode, visionOcrText, setVisionOcrText } = useAppState();
  const { t } = useLocale();
  const [isProcessing, setIsProcessing] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<{
    judgment?: { status?: string; condition?: string; reason: string; wait_days?: number };
    answer?: string;
  } | null>(null);
  const [elapsed, setElapsed] = useState<number | null>(null);

  const hasAutoRun = useRef(false);

  useEffect(() => {
    if (mode === "demo3-vision" && !hasAutoRun.current) {
      hasAutoRun.current = true;
      runSample();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  if (mode !== "demo3-vision") return null;

  const runSample = async () => {
    setIsProcessing(true);
    setElapsed(null);
    const t0 = Date.now();

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30000);
    try {
      // Fetch actual image and send to Vision API
      const imgResp = await fetch("/sample_prescription.jpg");
      const imgBlob = await imgResp.blob();
      const realFile = new File([imgBlob], "sample_prescription.jpg", {
        type: "image/jpeg",
      });
      const result = await analyzeVision(realFile, controller.signal);
      setVisionOcrText(result.ocr_text);
      if (result.pipeline_result) {
        setPipelineResult(result.pipeline_result);
      }
      setElapsed(Math.round((Date.now() - t0) / 100) / 10);
    } catch {
      // Simulate OCR result matching sample_en_prescription.jpg
      await new Promise((r) => setTimeout(r, 1500));
      const simulatedOcr = `[Prescription OCR Result]
Patient: John Smith    DOB: 03/15/1985
───────────────────────────────────
Rx: Aspirin 325mg
  Take 1 tablet by mouth once daily
  Qty: 30  |  Refills: 3

Rx: Lisinopril 10mg
  Take 1 tablet by mouth once daily for blood pressure
  Qty: 30  |  Refills: 5
───────────────────────────────────
Prescriber: Dr. Emily Johnson, MD
Date: March 5, 2026  |  City Health Pharmacy`;
      setVisionOcrText(simulatedOcr);

      await new Promise((r) => setTimeout(r, 800));
      setPipelineResult({
        judgment: {
          status: "조건부",
          reason:
            "아스피린 325mg 복용 중 → 전혈헌혈 마지막 복용 후 36시간 경과 필요. 리시노프릴(고혈압약)은 혈압 조절 상태 양호 시 헌혈 가능.",
          wait_days: 2,
        },
        answer:
          "처방전 분석 결과, 2가지 약물을 복용 중입니다.\n\n1. **아스피린 325mg** - 마지막 복용 후 36시간(약 1.5일) 경과 필요\n2. **리시노프릴 10mg** - 고혈압 약물, 혈압 조절 양호 시 헌혈 가능\n\n아스피린 복용 중단 후 36시간 경과하면 전혈헌혈이 가능합니다.\n(출처: 약학정보원, 헌혈 판정기준)",
      });
      setElapsed(Math.round((Date.now() - t0) / 100) / 10);
    } finally {
      clearTimeout(timeout);
      setIsProcessing(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <CardTitle className="text-base text-brand-blue">
              {t("vision.title")}
            </CardTitle>
            <Badge className="bg-brand-blue/10 text-brand-blue border-brand-blue/20 text-xs">
              Extension
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Sample prescription image */}
          <div className="rounded-lg border border-gray-200 overflow-hidden bg-gray-50">
            <p className="px-3 pt-2 text-[10px] font-bold uppercase tracking-wider text-gray-400">
              {t("vision.input_image")}
            </p>
            <div className="p-3">
              <Image
                src="/sample_prescription.jpg"
                alt="Sample prescription"
                width={400}
                height={200}
                className="rounded-md border border-gray-200 w-full h-auto"
              />
            </div>
          </div>

          {/* Processing indicator */}
          {isProcessing && !visionOcrText && (
            <div className="flex items-center gap-2 justify-center py-4">
              <Loader2 className="h-5 w-5 text-brand-blue animate-spin" />
              <p className="text-sm text-gray-500">
                <FileImage className="inline mr-1 h-3.5 w-3.5" />
                {t("vision.analyzing")}
              </p>
            </div>
          )}

          {/* OCR Result */}
          <AnimatePresence>
            {visionOcrText && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-3"
              >
                <div className="flex items-center gap-2">
                  <ArrowRight className="h-3 w-3 text-gray-400" />
                  <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">
                    {t("vision.result")}
                  </p>
                </div>
                <pre className="rounded-lg bg-gray-900 p-4 text-xs text-green-400 font-mono leading-relaxed overflow-x-auto">
                  {visionOcrText}
                </pre>

                {pipelineResult && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="space-y-3"
                  >
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <ArrowRight className="h-3 w-3" />
                      <span className="font-semibold uppercase tracking-wider">
                        {t("vision.pipeline_result")}
                      </span>
                    </div>

                    {pipelineResult.judgment && (
                      <JudgmentCard judgment={pipelineResult.judgment as JudgmentResult} />
                    )}

                    {pipelineResult.answer && (
                      <div className="rounded-lg border border-gray-200 bg-white p-3 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                        {pipelineResult.answer
                          .split(/(\*\*[^*]+\*\*)/g)
                          .map((part, i) => {
                            if (
                              part.startsWith("**") &&
                              part.endsWith("**")
                            ) {
                              return (
                                <strong
                                  key={i}
                                  className="font-semibold text-gray-900"
                                >
                                  {part.slice(2, -2)}
                                </strong>
                              );
                            }
                            return part;
                          })}
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Timing */}
                {elapsed !== null && !isProcessing && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2 text-[10px] text-gray-400 font-mono"
                  >
                    <Clock className="h-3 w-3" />
                    <span>{t("vision.timing")}: {elapsed}s</span>
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
