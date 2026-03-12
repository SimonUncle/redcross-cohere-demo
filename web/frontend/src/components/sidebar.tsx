"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { motion, AnimatePresence } from "framer-motion";
import { useAppState } from "@/lib/store";
import { useLocale } from "@/lib/locale-context";
import {
  Cpu,
  Database,
  Search,
  ArrowUpDown,
  Zap,
  Activity,
  ChevronDown,
} from "lucide-react";

export function Sidebar() {
  const { tokens, mode } = useAppState();
  const { t } = useLocale();
  const [showMetrics, setShowMetrics] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="space-y-4"
    >
      {/* Product Stack */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2 text-sm font-semibold text-navy">
            <Database className="h-4 w-4" />
            Cohere Product Stack
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2.5">
          <ProductItem
            icon={<Zap className="h-3.5 w-3.5" />}
            name="Command A"
            desc={t("sidebar.simple_query")}
            color="text-brand-green"
            bgColor="bg-brand-green/10"
          />
          <ProductItem
            icon={<Cpu className="h-3.5 w-3.5" />}
            name="Command A Reasoning"
            desc={t("sidebar.complex_analysis")}
            color="text-brand-blue"
            bgColor="bg-brand-blue/10"
          />
          <ProductItem
            icon={<Search className="h-3.5 w-3.5" />}
            name="Embed v4"
            desc={t("sidebar.vector_search")}
            color="text-brand-orange"
            bgColor="bg-brand-orange/10"
          />
          <ProductItem
            icon={<ArrowUpDown className="h-3.5 w-3.5" />}
            name="Rerank 4"
            desc={t("sidebar.reranking")}
            color="text-navy"
            bgColor="bg-navy/10"
          />
        </CardContent>
      </Card>

      {/* Developer Metrics Toggle */}
      <button
        onClick={() => setShowMetrics((v) => !v)}
        className="flex w-full items-center justify-between rounded-md px-3 py-1.5 text-xs text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors"
      >
        <span>{t("sidebar.dev_metrics")}</span>
        <ChevronDown
          className={`h-3.5 w-3.5 transition-transform duration-200 ${
            showMetrics ? "rotate-180" : ""
          }`}
        />
      </button>

      <AnimatePresence>
        {showMetrics && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="space-y-4 overflow-hidden"
          >
            {/* Token Usage */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-sm font-semibold text-navy">
                  <Activity className="h-4 w-4" />
                  {t("sidebar.token_usage")}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {tokens ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="space-y-2.5"
                  >
                    <TokenBar
                      label="Input"
                      value={tokens.input_tokens}
                      max={4000}
                      color="bg-brand-blue"
                    />
                    <TokenBar
                      label="Output"
                      value={tokens.output_tokens}
                      max={2000}
                      color="bg-brand-green"
                    />
                    {tokens.search_units !== undefined && (
                      <TokenBar
                        label="Search"
                        value={tokens.search_units}
                        max={10}
                        color="bg-brand-orange"
                        unit="units"
                      />
                    )}
                    <Separator />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Total</span>
                      <span className="font-mono font-medium text-gray-700">
                        {(tokens.input_tokens + tokens.output_tokens).toLocaleString()}{" "}
                        tokens
                      </span>
                    </div>
                  </motion.div>
                ) : (
                  <div className="py-4 text-center text-xs text-gray-400">
                    {t("sidebar.placeholder")}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Rate Limits */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-navy">
                  Rate Limits
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">API Calls</span>
                    <Badge variant="outline" className="text-[10px] font-mono">
                      {mode !== "idle" ? "2" : "0"} / 100 per min
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">Tokens</span>
                    <Badge variant="outline" className="text-[10px] font-mono">
                      {tokens
                        ? (
                            tokens.input_tokens + tokens.output_tokens
                          ).toLocaleString()
                        : "0"}{" "}
                      / 100K per min
                    </Badge>
                  </div>
                  <div className="h-1.5 w-full rounded-full bg-gray-100 overflow-hidden">
                    <motion.div
                      className="h-full rounded-full bg-brand-green"
                      initial={{ width: 0 }}
                      animate={{
                        width: tokens
                          ? `${Math.min(
                              ((tokens.input_tokens + tokens.output_tokens) /
                                100000) *
                                100,
                              100
                            )}%`
                          : "0%",
                      }}
                      transition={{ duration: 0.8, ease: "easeOut" }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function ProductItem({
  icon,
  name,
  desc,
  color,
  bgColor,
}: {
  icon: React.ReactNode;
  name: string;
  desc: string;
  color: string;
  bgColor: string;
}) {
  return (
    <div className="flex items-center gap-2.5">
      <div
        className={`flex h-7 w-7 items-center justify-center rounded-md ${bgColor} ${color}`}
      >
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-xs font-semibold text-gray-800">{name}</p>
        <p className="text-[10px] text-gray-500">{desc}</p>
      </div>
    </div>
  );
}

function TokenBar({
  label,
  value,
  max,
  color,
  unit = "tokens",
}: {
  label: string;
  value: number;
  max: number;
  color: string;
  unit?: string;
}) {
  const pct = Math.min((value / max) * 100, 100);

  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-gray-500">{label}</span>
        <span className="font-mono text-[10px] text-gray-700">
          {value.toLocaleString()} {unit}
        </span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-gray-100 overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}
