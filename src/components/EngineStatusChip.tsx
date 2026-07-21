import React from "react";

type EngineSource = "groq_ai" | "gemini_ai" | "local_engine";

interface Props {
  source?: EngineSource;
  latency?: number;
  quotaSafe?: boolean;
}

export default function EngineStatusChip({ source, latency, quotaSafe = true }: Props) {
  if (!source) return null;

  const config = {
    groq_ai: { label: "Groq Llama 3.3", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20", icon: "⚡" },
    gemini_ai: { label: "Google Gemini", color: "bg-purple-500/10 text-purple-400 border-purple-500/20", icon: "🧠" },
    local_engine: { label: "Local Engine", color: "bg-slate-500/10 text-slate-400 border-slate-500/20", icon: "💻" }
  };

  const { label, color, icon } = config[source] || config.local_engine;

  return (
    <div className="flex items-center gap-2">
      <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold border ${color}`}>
        <span>{icon}</span>
        <span>{label}</span>
        {latency !== undefined && (
          <span className="opacity-60 ml-1 border-l border-current pl-1.5 font-mono">{latency}ms</span>
        )}
      </div>
      {!quotaSafe && (
        <span className="text-[9px] bg-rose-500/10 text-rose-400 border border-rose-500/20 px-1.5 rounded uppercase font-black tracking-tighter animate-pulse">
          ⚠️ Quota Reached
        </span>
      )}
    </div>
  );
}
