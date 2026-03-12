"use client";

import { createContext, useContext } from "react";
import type {
  ChatResponse,
  ToolCall,
  JudgmentResult,
  ClassificationResult,
  TokenUsage,
  CompareResult,
} from "./api";

export type DemoMode =
  | "idle"
  | "demo1"
  | "demo1b"
  | "demo2"
  | "demo3-vision"
  | "demo3-translate"
  | "custom";

export interface AppState {
  mode: DemoMode;
  setMode: (mode: DemoMode) => void;

  // Chat
  query: string;
  setQuery: (q: string) => void;
  isStreaming: boolean;
  setIsStreaming: (s: boolean) => void;
  streamingText: string;
  setStreamingText: (t: string) => void;
  appendStreamingText: (chunk: string) => void;
  toolPlan: string;
  setToolPlan: (t: string) => void;
  appendToolPlan: (chunk: string) => void;

  // Results
  classification: ClassificationResult | null;
  setClassification: (c: ClassificationResult | null) => void;
  toolCalls: ToolCall[];
  setToolCalls: (tc: ToolCall[]) => void;
  addToolCall: (tc: ToolCall) => void;
  updateToolCall: (index: number, tc: Partial<ToolCall>) => void;
  judgment: JudgmentResult | null;
  setJudgment: (j: JudgmentResult | null) => void;
  answer: string;
  setAnswer: (a: string) => void;
  tokens: TokenUsage | null;
  setTokens: (t: TokenUsage | null) => void;

  // Timing
  timing: { classify: number; tool_loop: number; judgment: number; total: number } | null;
  setTiming: (t: { classify: number; tool_loop: number; judgment: number; total: number } | null) => void;

  // Compare mode
  compareResult: CompareResult | null;
  setCompareResult: (r: CompareResult | null) => void;

  // Vision
  visionOcrText: string;
  setVisionOcrText: (t: string) => void;

  // Translate
  translateSteps: { step: number; label: string; content: string }[];
  setTranslateSteps: (
    s: { step: number; label: string; content: string }[]
  ) => void;

  // Reset
  reset: () => void;
}

export const AppContext = createContext<AppState | null>(null);

export function useAppState(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useAppState must be used within AppProvider");
  return ctx;
}
