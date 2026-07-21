import React, { useState } from "react";
import { FileSignature, Sparkles, Loader2, ChevronRight, Check, Copy } from "lucide-react";
import EngineStatusChip from "./EngineStatusChip.tsx";

export default function ResumeWriter({ resumeText }: { resumeText: string }) {
  const [jobDescription, setJobDescription] = useState("");
  const [isTailoring, setIsTailoring] = useState(false);
  const [optimizedBullets, setOptimizedBullets] = useState<string[]>([]);
  const [meta, setMeta] = useState<any>(null);

  const tailorBullets = async () => {
    if (!resumeText || !jobDescription) return;
    setIsTailoring(true);
    try {
      // Split resume text into bullets (simple heuristic)
      const bullets = resumeText.split("\n").filter(l => l.trim().startsWith("-") || l.trim().startsWith("•"));

      const response = await fetch("/api/resumes/tailor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bullets, job_description: jobDescription })
      });
      const data = await response.json();
      setOptimizedBullets(data.data);
      setMeta(data.meta);
    } catch (err) {
      console.error(err);
    } finally {
      setIsTailoring(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <FileSignature className="w-6 h-6 text-indigo-400" />
            <h2 className="text-xl font-black text-white uppercase tracking-tight">AI Resume Bullet Tailoring</h2>
          </div>
          {meta && <EngineStatusChip source={meta.source} latency={meta.latency} />}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          <div className="space-y-4">
             <div className="flex items-center justify-between px-1">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Target Job Description</label>
                <span className="text-[10px] font-bold text-slate-600 bg-slate-800 px-2 py-0.5 rounded">Context limit: 4k chars</span>
             </div>
             <textarea
               value={jobDescription}
               onChange={(e) => setJobDescription(e.target.value)}
               placeholder="Paste the job description here..."
               className="w-full h-[400px] bg-slate-950 border border-slate-800 rounded-2xl p-6 text-sm text-slate-300 focus:border-indigo-500 outline-none transition-all resize-none font-sans leading-relaxed"
             />
             <button
               onClick={tailorBullets}
               disabled={isTailoring || !resumeText}
               className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-black py-4 rounded-2xl flex items-center justify-center gap-3 shadow-lg shadow-indigo-600/20 transition-all uppercase tracking-widest text-sm"
             >
               {isTailoring ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
               Tailor Bullet Points
             </button>
          </div>

          <div className="space-y-4 flex flex-col">
             <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-widest px-1">Optimized Experience Bullets</h3>
             <div className="flex-1 bg-slate-950/50 border border-slate-800 rounded-3xl p-6 overflow-y-auto max-h-[500px]">
                {optimizedBullets.length > 0 ? (
                  <div className="space-y-4">
                    {optimizedBullets.map((bullet, i) => (
                      <div key={i} className="flex gap-3 group">
                        <div className="mt-1.5"><ChevronRight className="w-3.5 h-3.5 text-indigo-500" /></div>
                        <div className="text-sm text-slate-300 leading-relaxed py-1 px-2 rounded-lg hover:bg-slate-900 transition-colors flex-1">{bullet}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-30">
                    <FileSignature className="w-12 h-12" />
                    <p className="text-xs font-bold uppercase tracking-tighter max-w-[200px]">Optimized bullets will appear here after analysis</p>
                  </div>
                )}
             </div>
             {optimizedBullets.length > 0 && (
               <button className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex items-center justify-center gap-2 transition-all">
                  <Copy className="w-4 h-4" />
                  Copy All Optimized Bullets
               </button>
             )}
          </div>
        </div>
      </div>
    </div>
  );
}
