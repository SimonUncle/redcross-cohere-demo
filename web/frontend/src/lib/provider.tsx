"use client";

import { useState, useCallback, useMemo } from "react";
import { AppContext, type AppState, type DemoMode } from "./store";
import type {
  ToolCall,
  JudgmentResult,
  ClassificationResult,
  TokenUsage,
  CompareResult,
} from "./api";

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<DemoMode>("idle");
  const [query, setQuery] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const [toolPlan, setToolPlan] = useState("");
  const [classification, setClassification] =
    useState<ClassificationResult | null>(null);
  const [toolCalls, setToolCalls] = useState<ToolCall[]>([]);
  const [judgment, setJudgment] = useState<JudgmentResult | null>(null);
  const [answer, setAnswer] = useState("");
  const [tokens, setTokens] = useState<TokenUsage | null>(null);
  const [compareResult, setCompareResult] = useState<CompareResult | null>(
    null
  );
  const [timing, setTiming] = useState<AppState["timing"]>(null);
  const [visionOcrText, setVisionOcrText] = useState("");
  const [translateSteps, setTranslateSteps] = useState<
    { step: number; label: string; content: string }[]
  >([]);

  const appendStreamingText = useCallback((chunk: string) => {
    setStreamingText((prev) => prev + chunk);
  }, []);

  const appendToolPlan = useCallback((chunk: string) => {
    setToolPlan((prev) => prev + chunk);
  }, []);

  const addToolCall = useCallback((tc: ToolCall) => {
    setToolCalls((prev) => [...prev, tc]);
  }, []);

  const updateToolCall = useCallback((index: number, tc: Partial<ToolCall>) => {
    setToolCalls((prev) =>
      prev.map((item, i) => (i === index ? { ...item, ...tc } : item))
    );
  }, []);

  const reset = useCallback(() => {
    setQuery("");
    setIsStreaming(false);
    setStreamingText("");
    setToolPlan("");
    setClassification(null);
    setToolCalls([]);
    setJudgment(null);
    setAnswer("");
    setTokens(null);
    setCompareResult(null);
    setTiming(null);
    setVisionOcrText("");
    setTranslateSteps([]);
  }, []);

  const value = useMemo<AppState>(
    () => ({
      mode,
      setMode,
      query,
      setQuery,
      isStreaming,
      setIsStreaming,
      streamingText,
      setStreamingText,
      appendStreamingText,
      toolPlan,
      setToolPlan,
      appendToolPlan,
      classification,
      setClassification,
      toolCalls,
      setToolCalls,
      addToolCall,
      updateToolCall,
      judgment,
      setJudgment,
      answer,
      setAnswer,
      tokens,
      setTokens,
      timing,
      setTiming,
      compareResult,
      setCompareResult,
      visionOcrText,
      setVisionOcrText,
      translateSteps,
      setTranslateSteps,
      reset,
    }),
    [
      mode,
      query,
      isStreaming,
      streamingText,
      toolPlan,
      classification,
      toolCalls,
      judgment,
      answer,
      tokens,
      timing,
      compareResult,
      visionOcrText,
      translateSteps,
      appendStreamingText,
      appendToolPlan,
      addToolCall,
      updateToolCall,
      reset,
    ]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}
