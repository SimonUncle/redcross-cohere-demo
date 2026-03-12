"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { useAppState } from "@/lib/store";
import { useLocale } from "@/lib/locale-context";
import { streamChat, fetchCompare } from "@/lib/api";
import { Search, GitCompare, Puzzle, FileText } from "lucide-react";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export function DemoCards() {
  const state = useAppState();
  const { t } = useLocale();

  const handleDemo1 = async () => {
    state.reset();
    state.setMode("demo1");
    const query = "아스피린 복용 후 헌혈 가능한가요? 3일 전 복용했습니다.";
    state.setQuery(query);
    state.setIsStreaming(true);

    try {
      for await (const event of streamChat({ query })) {
        handleSSEEvent(event, state);
      }
    } catch (err) {
      console.error("Stream error:", err);
      simulateDemo1(state);
    } finally {
      state.setIsStreaming(false);
    }
  };

  const handleDemo1b = async () => {
    state.reset();
    state.setMode("demo1b");
    const query = "지난달에 문신을 했는데 헌혈 가능한가요?";
    state.setQuery(query);
    state.setIsStreaming(true);

    try {
      for await (const event of streamChat({ query })) {
        handleSSEEvent(event, state);
      }
    } catch (err) {
      console.error("Stream error:", err);
      simulateDemo1b(state);
    } finally {
      state.setIsStreaming(false);
    }
  };

  const handleDemo2 = async () => {
    state.reset();
    state.setMode("demo2");
    const query =
      "3주 전 파푸아뉴기니에서 귀국했고, 5일 전 아스피린을 복용했습니다. 헌혈 가능한가요?";
    state.setQuery(query);
    state.setIsStreaming(true);

    try {
      const result = await fetchCompare(query);
      state.setCompareResult(result);
    } catch (err) {
      console.error("Compare error:", err);
      simulateDemo2(state);
    } finally {
      state.setIsStreaming(false);
    }
  };

  const handleDemo3Vision = () => {
    state.reset();
    state.setMode("demo3-vision");
  };

  const handleDemo3Translate = () => {
    state.reset();
    state.setMode("demo3-translate");
  };

  const handleCustomQuery = async (query: string) => {
    if (!query.trim()) return;
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
      simulateCustom(state, query);
    } finally {
      state.setIsStreaming(false);
    }
  };

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-4"
    >
      {/* Main demo cards */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
        {/* Demo 1 */}
        <motion.div variants={item}>
          <Card
            className="cursor-pointer border-l-4 border-l-navy transition-all hover:shadow-lg hover:-translate-y-0.5"
            onClick={handleDemo1}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-semibold text-navy">
                  {t("demo.1a.title")}
                </CardTitle>
                <Badge
                  variant="outline"
                  className="border-navy/30 text-navy text-xs"
                >
                  {t("demo.1a.badge")}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-gray-500">
                {t("demo.1a.desc")}
              </p>
              <div className="flex items-center gap-2 rounded-md bg-gray-50 px-3 py-2 text-xs text-gray-600">
                <Search className="h-3 w-3 shrink-0" />
                <span className="truncate">
                  {t("demo.1a.query_preview")}
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Demo 1b - 조건부 */}
        <motion.div variants={item}>
          <Card
            className="cursor-pointer border-l-4 border-l-amber-500 transition-all hover:shadow-lg hover:-translate-y-0.5"
            onClick={handleDemo1b}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-semibold text-amber-600">
                  {t("demo.1b.title")}
                </CardTitle>
                <Badge
                  variant="outline"
                  className="border-amber-500/30 text-amber-600 text-xs"
                >
                  {t("demo.1b.badge")}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-gray-500">
                {t("demo.1b.desc")}
              </p>
              <div className="flex items-center gap-2 rounded-md bg-gray-50 px-3 py-2 text-xs text-gray-600">
                <Search className="h-3 w-3 shrink-0" />
                <span className="truncate">
                  {t("demo.1b.query_preview")}
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Demo 2 */}
        <motion.div variants={item}>
          <Card
            className="cursor-pointer border-l-4 border-l-brand-red transition-all hover:shadow-lg hover:-translate-y-0.5"
            onClick={handleDemo2}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-semibold text-brand-red">
                  {t("demo.2.title")}
                </CardTitle>
                <Badge
                  variant="outline"
                  className="border-brand-red/30 text-brand-red text-xs"
                >
                  Demo 2
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-gray-500">
                {t("demo.2.desc")}
              </p>
              <div className="flex items-center gap-2 rounded-md bg-gray-50 px-3 py-2 text-xs text-gray-600">
                <GitCompare className="h-3 w-3 shrink-0" />
                <span className="truncate">
                  {t("demo.2.query_preview")}
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Demo 3 */}
        <motion.div variants={item}>
          <Card className="border-l-4 border-l-brand-blue transition-all hover:shadow-lg">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base font-semibold text-brand-blue">
                  {t("demo.3.title")}
                </CardTitle>
                <Badge
                  variant="outline"
                  className="border-brand-blue/30 text-brand-blue text-xs"
                >
                  Feasibility
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-sm text-gray-500">
                {t("demo.3.desc")}
              </p>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1 border-brand-blue/30 text-brand-blue hover:bg-brand-blue/5 text-xs"
                  onClick={handleDemo3Vision}
                >
                  <Puzzle className="mr-1 h-3 w-3" />
                  Vision OCR
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1 border-dark-green/30 text-dark-green hover:bg-dark-green/5 text-xs"
                  onClick={handleDemo3Translate}
                >
                  <FileText className="mr-1 h-3 w-3" />
                  English Mode
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Additional card */}
      <div className="grid grid-cols-1 gap-4">
        <motion.div variants={item}>
          <Card
            className="cursor-pointer border-l-4 border-l-gray-300 transition-all hover:shadow-md hover:-translate-y-0.5"
            onClick={() =>
              handleCustomQuery(
                "고혈압 약 복용 중이고 오늘 혈압이 158mmHg입니다. 헌혈 가능한가요?"
              )
            }
          >
            <CardContent className="flex items-center gap-3 py-3">
              <Badge variant="secondary" className="shrink-0 text-xs">
                {t("demo.extra.badge")}
              </Badge>
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-800">{t("demo.extra.title")}</p>
                <p className="truncate text-xs text-gray-500">
                  {t("demo.extra.query_preview")}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}

// --- SSE Event Handlers ---

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
    case "tool_call": {
      const tcData = data as { step?: number; status?: string; tool?: string; args?: Record<string, string>; result?: string };
      if (tcData.status === "running") {
        state.addToolCall({
          tool: tcData.tool || "",
          args: tcData.args || {},
          status: "running",
        });
      } else if (tcData.status === "done") {
        const idx = (tcData.step || 1) - 1;
        state.updateToolCall(idx, {
          result: tcData.result,
          status: "done",
        });
      } else {
        state.addToolCall(tcData as unknown as ReturnType<typeof useAppState>["toolCalls"][0]);
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
      state.setJudgment(
        data as unknown as ReturnType<typeof useAppState>["judgment"]
      );
      break;
    case "text_delta":
    case "stream": {
      const chunk = (data as { text?: string }).text || "";
      state.appendStreamingText(chunk);
      break;
    }
    case "tool_plan": {
      state.appendToolPlan((data as { text?: string }).text || "");
      break;
    }
    case "content_delta": {
      state.appendStreamingText((data as { text?: string }).text || "");
      break;
    }
    case "thinking": {
      // ignore thinking events for now
      break;
    }
    case "citation": {
      // ignore citation events for now
      break;
    }
    case "answer":
      state.setAnswer((data as { text?: string }).text || "");
      break;
    case "timing":
      state.setTiming(data as ReturnType<typeof useAppState>["timing"]);
      break;
    case "tokens":
      state.setTokens(
        data as unknown as ReturnType<typeof useAppState>["tokens"]
      );
      break;
    case "done": {
      if (state.streamingText) {
        state.setAnswer(state.streamingText);
      }
      const doneData = data as { total_tokens?: unknown };
      if (doneData.total_tokens) {
        state.setTokens(doneData.total_tokens as ReturnType<typeof useAppState>["tokens"]);
      }
      state.setIsStreaming(false);
      break;
    }
  }
}

// --- Simulation Fallbacks (when backend is not available) ---

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function simulateDemo1(state: ReturnType<typeof useAppState>) {
  state.setClassification({ type: "단순", model: "Command A" });
  await sleep(500);

  state.addToolCall({
    tool: "search_guideline",
    args: { query: "아스피린 헌혈" },
    status: "running",
  });
  await sleep(1200);

  state.updateToolCall(0, {
    result:
      "[약학정보원] 아세틸살리실산(아스피린) 복용 시 전혈헌혈 3일 경과 후 가능. 성분헌혈(혈소판) 7일 경과 후 가능.",
    status: "done",
  });
  await sleep(800);

  state.setJudgment({
    status: "즉시가능",
    reason:
      "아스피린(아세틸살리실산) 복용 후 3일이 경과하여 전혈헌혈이 가능합니다.",
  });
  await sleep(500);

  const answerText =
    "아스피린을 3일 전에 복용하셨군요.\n\n약학정보원 가이드라인에 따르면, 아세틸살리실산(아스피린) 복용 후 **전혈헌혈은 3일 경과 후 가능**합니다.\n\n복용 후 3일이 경과하였으므로 **즉시 헌혈이 가능**합니다.\n\n단, 성분헌혈(혈소판)의 경우 7일 경과가 필요하므로 성분헌혈은 4일 후 가능합니다.";
  state.setAnswer(answerText);
  state.setStreamingText(answerText);

  state.setTokens({ input_tokens: 847, output_tokens: 234, search_units: 1 });
  state.setIsStreaming(false);
}

async function simulateDemo1b(state: ReturnType<typeof useAppState>) {
  state.setClassification({ type: "단순", model: "Command A" });
  await sleep(500);

  state.addToolCall({
    tool: "search_guideline",
    args: { query: "타투 문신 헌혈" },
    status: "running",
  });
  await sleep(1200);

  state.updateToolCall(0, {
    result:
      "[대한적십자사] 문신(타투)/피어싱 시술 후 6개월 경과해야 헌혈 가능. 의료기관 외 시술 시 적용.",
    status: "done",
  });
  await sleep(800);

  state.setJudgment({
    status: "조건부",
    reason:
      "문신(타투) 시술 후 6개월 미경과로 현재 헌혈 불가. 약 5개월 후 헌혈 가능합니다.",
    wait_days: 153,
  });
  await sleep(500);

  const answerText =
    "지난달에 타투를 하셨군요.\n\n대한적십자사 헌혈 가이드라인에 따르면, **문신(타투) 시술 후 6개월이 경과해야 헌혈이 가능**합니다.\n\n시술 후 약 1개월이 경과하였으므로, **약 153일(5개월) 후 헌혈이 가능**합니다.\n\n> 참고: 의료기관에서 시술받은 경우에도 동일한 기준이 적용됩니다.";
  state.setAnswer(answerText);
  state.setStreamingText(answerText);

  state.setTokens({ input_tokens: 823, output_tokens: 215, search_units: 1 });
  state.setIsStreaming(false);
}

async function simulateDemo2(state: ReturnType<typeof useAppState>) {
  await sleep(600);

  state.setCompareResult({
    command_a: {
      classification: { type: "복합", model: "Command A" },
      tool_calls: [
        {
          tool: "search_guideline",
          args: { query: "아스피린 헌혈" },
          result:
            "[약학정보원] 아세틸살리실산 복용 시 전혈 3일, 성분 7일 경과 후 가능",
          status: "done",
        },
        {
          tool: "check_malaria_risk",
          args: { country: "파푸아뉴기니" },
          result: "[질병관리청] 말라리아 위험등급 2급, 1년 헌혈 제한",
          status: "done",
        },
      ],
      judgment: {
        status: "불가",
        reason:
          "말라리아 위험 지역(파푸아뉴기니) 방문 후 1년 미경과로 헌혈 불가",
        wait_days: 344,
      },
      answer:
        "파푸아뉴기니는 말라리아 위험 지역(2급)으로 분류되어 귀국 후 1년간 헌혈이 제한됩니다. 현재 3주(약 21일)만 경과하여 약 344일 후 헌혈이 가능합니다.",
      tokens: { input_tokens: 1243, output_tokens: 312, search_units: 2 },
    },
    reasoning: {
      classification: {
        type: "복합",
        model: "A Reasoning",
        keywords: ["파푸아뉴기니", "아스피린", "말라리아"],
      },
      tool_calls: [
        {
          tool: "search_guideline",
          args: { query: "아스피린 복용 헌혈 제한" },
          result:
            "[약학정보원] 아세틸살리실산 복용 시 전혈 3일, 성분 7일 경과 후 가능",
          status: "done",
        },
        {
          tool: "check_malaria_risk",
          args: { country: "파푸아뉴기니" },
          result:
            "[질병관리청] 파푸아뉴기니 - 말라리아 위험등급 2급 (고위험), 귀국 후 1년 헌혈 제한",
          status: "done",
        },
        {
          tool: "search_guideline",
          args: { query: "말라리아 위험지역 헌혈 제한 기간" },
          result:
            "[대한적십자사] 말라리아 위험지역 방문자: 1급 - 6개월, 2급 - 1년, 3급 - 영구제한",
          status: "done",
        },
      ],
      judgment: {
        status: "불가",
        reason:
          "복합 조건 분석: ① 아스피린 → 3일 경과 (충족) ② 말라리아 위험지역 → 1년 미경과 (미충족). 가장 긴 제한 조건 적용",
        wait_days: 344,
        conditions: [
          "아스피린 복용: 3일 경과 ✓",
          "말라리아 위험지역(2급): 1년 미경과 ✗ → 344일 대기",
        ],
      },
      answer:
        "두 가지 조건을 분석한 결과입니다:\n\n**1. 아스피린 복용** - 5일 전 복용으로 전혈헌혈 기준 3일 경과를 충족합니다.\n\n**2. 파푸아뉴기니 방문** - 질병관리청 기준 말라리아 위험등급 2급(고위험)으로, 귀국 후 **1년간 헌혈이 제한**됩니다.\n\n두 조건 중 가장 긴 제한 기간이 적용되므로, **약 344일 후 헌혈이 가능**합니다.\n\n> 참고: 말라리아 검사 음성 확인서가 있는 경우 기간 단축이 가능할 수 있으니, 가까운 헌혈의집에 문의하시기 바랍니다.",
      tokens: { input_tokens: 2156, output_tokens: 587, search_units: 3 },
    },
  });

  state.setTokens({ input_tokens: 3399, output_tokens: 899, search_units: 5 });
  state.setIsStreaming(false);
}

async function simulateCustom(
  state: ReturnType<typeof useAppState>,
  query: string
) {
  state.setClassification({ type: "단순", model: "Command A" });
  await sleep(500);

  state.addToolCall({
    tool: "search_guideline",
    args: { query: query.slice(0, 20) },
    status: "running",
  });
  await sleep(1200);

  state.updateToolCall(0, {
    result: `[가이드라인 검색 결과] "${query.slice(0, 30)}..." 관련 헌혈 기준 조회 완료`,
    status: "done",
  });
  await sleep(800);

  state.setJudgment({
    status: "조건부",
    reason: "추가 확인이 필요한 조건입니다. 헌혈의집 방문 시 상담을 권장합니다.",
    wait_days: 7,
  });
  await sleep(500);

  const answerText = `"${query}"에 대한 분석 결과입니다.\n\n가이드라인 검색 결과를 바탕으로 판정하였습니다. 조건부 헌혈 가능으로, 약 7일 후 헌혈이 가능할 것으로 판단됩니다.\n\n정확한 판정을 위해 가까운 헌혈의집 방문 시 문진 의사와 상담하시기 바랍니다.`;
  state.setAnswer(answerText);
  state.setStreamingText(answerText);

  state.setTokens({ input_tokens: 956, output_tokens: 198, search_units: 1 });
  state.setIsStreaming(false);
}
