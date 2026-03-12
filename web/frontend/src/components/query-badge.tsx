"use client";

import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";
import type { ClassificationResult } from "@/lib/api";
import { Zap, Brain } from "lucide-react";
import { useLocale } from "@/lib/locale-context";

interface QueryBadgeProps {
  classification: ClassificationResult;
}

export function QueryBadge({ classification }: QueryBadgeProps) {
  const { t } = useLocale();
  const classType = classification.type || classification.complexity || "단순";
  const isSimple = classType === "단순";
  const keywords = classification.keywords || classification.matched_keywords || [];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex items-center gap-2"
    >
      <Badge
        className={
          isSimple
            ? "bg-brand-green/10 text-brand-green border-brand-green/20 hover:bg-brand-green/15"
            : "bg-brand-blue/10 text-brand-blue border-brand-blue/20 hover:bg-brand-blue/15"
        }
      >
        {isSimple ? (
          <Zap className="mr-1 h-3 w-3" />
        ) : (
          <Brain className="mr-1 h-3 w-3" />
        )}
        {isSimple ? t("classification.simple") : t("classification.complex")}
      </Badge>
      <span className="text-xs text-gray-500">→</span>
      <Badge variant="outline" className="text-xs font-mono">
        {classification.model}
      </Badge>
      {keywords.length > 0 && (
        <div className="flex gap-1">
          {keywords.map((kw, i) => (
            <Badge
              key={i}
              variant="secondary"
              className="text-[10px] px-1.5 py-0"
            >
              {kw}
            </Badge>
          ))}
        </div>
      )}
    </motion.div>
  );
}
