"use client";

import { motion } from "framer-motion";
import type { JudgmentResult } from "@/lib/api";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { useLocale } from "@/lib/locale-context";

interface JudgmentCardProps {
  judgment: JudgmentResult;
}

const variants = {
  즉시가능: {
    bg: "bg-[#F0FFF4]",
    border: "border-l-brand-green",
    icon: CheckCircle2,
    iconColor: "text-brand-green",
    labelKey: "judgment.eligible" as const,
    labelBg: "bg-brand-green/10 text-brand-green",
  },
  조건부: {
    bg: "bg-[#FFFAF0]",
    border: "border-l-brand-orange",
    icon: AlertTriangle,
    iconColor: "text-brand-orange",
    labelKey: "judgment.conditional" as const,
    labelBg: "bg-brand-orange/10 text-brand-orange",
  },
  불가: {
    bg: "bg-[#FFF5F5]",
    border: "border-l-brand-red",
    icon: XCircle,
    iconColor: "text-brand-red",
    labelKey: "judgment.ineligible" as const,
    labelBg: "bg-brand-red/10 text-brand-red",
  },
};

export function JudgmentCard({ judgment }: JudgmentCardProps) {
  const { t } = useLocale();
  // Backend sends "condition" field, simulation sends "status"
  const key = judgment.status || judgment.condition || "조건부";
  const v = variants[key as keyof typeof variants] || variants["조건부"];
  const Icon = v.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className={`rounded-lg border-l-4 ${v.border} ${v.bg} p-4`}
    >
      <div className="flex items-start gap-3">
        <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${v.iconColor}`} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span
              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold ${v.labelBg}`}
            >
              {t(v.labelKey)}
            </span>
            {judgment.wait_days !== undefined && judgment.wait_days > 0 && (
              <span className="text-xs text-gray-500">
                {t("judgment.wait_days", { days: judgment.wait_days })}
              </span>
            )}
          </div>
          <p className="text-sm text-gray-700 leading-relaxed">
            {judgment.reason}
          </p>
          {judgment.conditions && judgment.conditions.length > 0 && (
            <ul className="mt-2 space-y-1">
              {judgment.conditions.map((c, i) => (
                <li key={i} className="text-xs text-gray-600 flex items-start gap-1.5">
                  <span className="mt-0.5 text-gray-400">&#x2022;</span>
                  {c}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </motion.div>
  );
}
