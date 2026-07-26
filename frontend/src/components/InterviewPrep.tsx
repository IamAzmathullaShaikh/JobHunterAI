import React, { useState } from "react";
import { Brain, Loader2, Sparkles, MessageSquare, Target, ChevronRight, Copy, Check } from "lucide-react";

export default function InterviewPrep() {
  const [jobDescription, setJobDescription] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [prepGuide, setPrepGuide] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const generatePrep = async () => {
    if (!jobDescription) return;
    setIsGenerating(true);
    setPrepGuide(null);
    try {
      const response = await fetch("/api/interview/prep", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: jobDescription })
      });
      const data = await response.json();
      if (data.success) {
        setPrepGuide(data.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = () => {
    if (prepGuide) {
      navigator.clipboard.writeText(prepGuide);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8">
        <div className="flex items-center gap-4 mb-8">
          <Brain className="w-8 h-8 text-purple-400" />
          <div>
            <h2 className="text-xl font-black text-white uppercase tracking-tight">Interview Prep Studio</h2>
            <p className="text-xs text-slate-500 font-bold uppercase tracking-widest mt-1">Tiered AI Coaching Flow</p>
          </div>
        </div>

        {!prepGuide ? (
          <div className="max-w-2xl space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Target Job Description</label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description you're interviewing for..."
                className="w-full h-48 bg-slate-950 border border-slate-800 rounded-2xl p-6 text-sm text-slate-300 focus:border-indigo-500 outline-none transition-all resize-none"
              />
            </div>
            <button
              onClick={generatePrep}
              disabled={isGenerating || !jobDescription}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-black py-4 px-8 rounded-2xl flex items-center justify-center gap-3 shadow-lg shadow-indigo-600/20 transition-all uppercase tracking-widest text-sm"
            >
              {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
              Generate Prep Guide
            </button>
          </div>
        ) : (
          <div className="space-y-6 animate-slide-in">
            <div className="flex items-center justify-between">
               <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-widest">AI Generated Interview Guide</h3>
               <div className="flex gap-2">
                 <button
                   onClick={() => setPrepGuide(null)}
                   className="text-[10px] font-bold bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-xl transition-all"
                 >
                   Start Over
                 </button>
                 <button
                   onClick={copyToClipboard}
                   className="text-[10px] font-bold bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl flex items-center gap-2 transition-all"
                 >
                   {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                   {copied ? "Copied!" : "Copy Guide"}
                 </button>
               </div>
            </div>

            <div className="bg-slate-950 border border-slate-800 rounded-3xl p-8 text-sm text-slate-300 leading-relaxed font-sans whitespace-pre-wrap max-h-[600px] overflow-y-auto">
              {prepGuide}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-800/50 rounded-2xl border border-slate-700/50">
                <Target className="w-4 h-4 text-emerald-400 mb-2" />
                <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Tech Radar</p>
                <p className="text-xs text-white">Focus on concurrency and distributed systems questions.</p>
              </div>
              <div className="p-4 bg-slate-800/50 rounded-2xl border border-slate-700/50">
                <MessageSquare className="w-4 h-4 text-indigo-400 mb-2" />
                <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Soft Skills</p>
                <p className="text-xs text-white">Be prepared to explain why you want to move from IC to Lead.</p>
              </div>
              <div className="p-4 bg-slate-800/50 rounded-2xl border border-slate-700/50">
                <ChevronRight className="w-4 h-4 text-amber-400 mb-2" />
                <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Next Step</p>
                <p className="text-xs text-white">Try the STAR Method Master for behavioral practice.</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
