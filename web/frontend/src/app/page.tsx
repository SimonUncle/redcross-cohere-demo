"use client";

import { Header } from "@/components/header";
import { DemoCards } from "@/components/demo-cards";
import { ChatArea } from "@/components/chat-area";
import { ChatInput } from "@/components/chat-input";
import { ModelCompare } from "@/components/model-compare";
import { VisionPanel } from "@/components/vision-panel";
import { TranslatePipeline } from "@/components/translate-pipeline";
import { Sidebar } from "@/components/sidebar";
import { AppProvider } from "@/lib/provider";
import { LocaleProvider } from "@/lib/locale-context";
import { useAppState } from "@/lib/store";
import { useLocale } from "@/lib/locale-context";
import { Button } from "@/components/ui/button";
import { RotateCcw } from "lucide-react";

function MainContent() {
  const { mode, reset, setMode } = useAppState();
  const { t } = useLocale();

  const handleReset = () => {
    reset();
    setMode("idle");
  };

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <Header />

      <div className="flex-1 overflow-auto">
        <div className="mx-auto max-w-[1600px] px-4 py-6 lg:px-6">
          <div className="flex gap-6">
            {/* Main content area */}
            <div className="flex-1 min-w-0 space-y-6">
              {/* Demo cards - always visible */}
              <DemoCards />

              {/* Active demo area */}
              {mode !== "idle" && (
                <div className="space-y-4">
                  {/* Reset button */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-brand-green animate-pulse" />
                      <span className="text-xs font-medium text-gray-500">
                        {mode === "demo1" && t("page.demo1a")}
                        {mode === "demo1b" && t("page.demo1b")}
                        {mode === "demo2" && t("page.demo2")}
                        {mode === "demo3-vision" && t("page.demo3_vision")}
                        {mode === "demo3-translate" && t("page.demo3_translate")}
                        {mode === "custom" && t("page.custom")}
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleReset}
                      className="text-xs text-gray-400 hover:text-gray-600"
                    >
                      <RotateCcw className="mr-1 h-3 w-3" />
                      {t("page.reset")}
                    </Button>
                  </div>

                  {/* Chat/Compare/Vision/Translate content */}
                  {(mode === "demo1" || mode === "demo1b" || mode === "custom") && <ChatArea />}
                  {mode === "demo2" && <ModelCompare />}
                  {mode === "demo3-vision" && <VisionPanel />}
                  {mode === "demo3-translate" && <TranslatePipeline />}
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="hidden w-[300px] shrink-0 lg:block">
              <Sidebar />
            </div>
          </div>
        </div>
      </div>

      <ChatInput />
    </div>
  );
}

export default function Home() {
  return (
    <LocaleProvider>
      <AppProvider>
        <MainContent />
      </AppProvider>
    </LocaleProvider>
  );
}
