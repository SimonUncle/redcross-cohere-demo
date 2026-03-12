"use client";

import { Badge } from "@/components/ui/badge";
import { motion } from "framer-motion";
import { useLocale } from "@/lib/locale-context";

export function Header() {
  const { locale, setLocale, t } = useLocale();

  return (
    <header className="bg-navy text-white shadow-lg">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between px-6 py-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-4"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white/15 text-lg font-bold">
            +
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              {t("header.title")}
            </h1>
            <p className="text-sm text-white/70">
              Cohere Command A + Embed v4 + Rerank 4
            </p>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex items-center gap-3"
        >
          <div className="mr-2 hidden items-center gap-2 text-sm text-white/50 sm:flex">
            <span className="inline-block h-2 w-2 rounded-full bg-brand-green animate-pulse" />
            Backend Connected
          </div>

          {/* KO/EN Toggle */}
          <div className="flex items-center rounded-full bg-white/10 p-0.5">
            <button
              onClick={() => setLocale("ko")}
              className={`rounded-full px-2.5 py-1 text-xs font-bold transition-all ${
                locale === "ko"
                  ? "bg-white text-navy shadow-sm"
                  : "text-white/60 hover:text-white/90"
              }`}
            >
              KO
            </button>
            <button
              onClick={() => setLocale("en")}
              className={`rounded-full px-2.5 py-1 text-xs font-bold transition-all ${
                locale === "en"
                  ? "bg-white text-navy shadow-sm"
                  : "text-white/60 hover:text-white/90"
              }`}
            >
              EN
            </button>
          </div>

          <Badge className="border-brand-red/30 bg-brand-red px-3 py-1 text-xs font-bold tracking-wider text-white hover:bg-brand-red/90">
            LIVE DEMO
          </Badge>
        </motion.div>
      </div>
    </header>
  );
}
