import React, { useState } from "react";
import { Brain, Sparkles, Check, AlertTriangle, Loader2, Play } from "lucide-react";
import { JobListing, AIAnalysis } from "../types.ts";

interface AnalysisMatrixProps {
  jobs: JobListing[];
  resumeText: string;
  onAnalysisComplete: (jobs: JobListing[]) => void;
}

export default function AnalysisMatrix({
  jobs,
  resumeText,
  onAnalysisComplete,
}: AnalysisMatrixProps) {
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isEvaluatingAll, setIsEvaluatingAll] = useState(false);
  const [evaluationError, setEvaluationError] = useState<string | null>(null);

  const evaluatedJobs = jobs.filter((j) => j.ai_analysis);
  const unevaluatedJobs = jobs.filter((j) => !j.ai_analysis);

  // Set default selected job if none is selected
  const activeJobId = selectedJobId ?? (evaluatedJobs.length > 0 ? evaluatedJobs[0].id : null);
  const activeJob = jobs.find((j) => j.id === Number(activeJobId));

  const triggerEvaluation = async (jobId: number) => {
    if (!resumeText.trim()) {
      setEvaluationError("A parsed resume profile is required. Please upload or paste your resume in the Home tab first.");
      return;
    }

    setIsEvaluating(true);
    setEvaluationError(null);
    try {
      const response = await fetch("/api/jobs/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: jobId, resume_text: resumeText }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Failed to analyze job listing.");
      }

      // Reload jobs
      const jobsRes = await fetch("/api/jobs/");
      const jobsData = await jobsRes.json();
      onAnalysisComplete(jobsData.jobs);
      setSelectedJobId(jobId);
    } catch (err: any) {
      console.error(err);
      setEvaluationError(err.message || "Could not check job match.");
    } finally {
      setIsEvaluating(false);
    }
  };

  const triggerBatchEvaluation = async () => {
    if (!resumeText.trim()) {
      setEvaluationError("A parsed resume profile is required. Please upload or paste your resume in the Home tab first.");
      return;
    }

    setIsEvaluatingAll(true);
    setEvaluationError(null);
    try {
      const response = await fetch("/api/jobs/analyze-pending", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume_text: resumeText }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Batch evaluate failed.");
      }

      // Reload jobs
      const jobsRes = await fetch("/api/jobs/");
      const jobsData = await jobsRes.json();
      onAnalysisComplete(jobsData.jobs);
    } catch (err: any) {
      console.error(err);
      setEvaluationError(err.message || "Could not check all jobs.");
    } finally {
      setIsEvaluatingAll(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/80 shadow-md">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-5">
          <div>
            <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <Brain className="w-5 h-5 text-indigo-400" />
              🧠 Check how well you match with jobs
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              See how well your resume matches these jobs and what you can improve.
            </p>
          </div>

          {unevaluatedJobs.length > 0 && (
            <button
              onClick={triggerBatchEvaluation}
              disabled={isEvaluatingAll || isEvaluating || !resumeText.trim()}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-slate-100 text-xs font-semibold py-2 px-4 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
            >
              {isEvaluatingAll ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Checking Jobs...
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  Check match for {Math.min(unevaluatedJobs.length, 5)} jobs
                </>
              )}
            </button>
          )}
        </div>

        {evaluationError && (
          <div className="bg-rose-500/15 border border-rose-500/30 text-rose-300 rounded-lg p-3.5 text-sm mb-5 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            {evaluationError}
          </div>
        )}

        {evaluatedJobs.length === 0 ? (
          <div className="p-8 border border-dashed border-slate-700 bg-slate-900/40 rounded-lg text-center">
            <Brain className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h4 className="text-sm font-semibold text-slate-300">No job matches checked yet</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Upload your resume and find some jobs first. Then you can check how well you match.
            </p>

            {unevaluatedJobs.length > 0 && (
              <div className="mt-5 max-w-sm mx-auto space-y-3">
                <span className="text-xs font-semibold text-slate-400 block">Select a job to check:</span>
                <select
                  onChange={(e) => triggerEvaluation(Number(e.target.value))}
                  defaultValue=""
                  disabled={isEvaluating || !resumeText.trim()}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-xs text-slate-200 focus:outline-none"
                >
                  <option value="" disabled>Select job to evaluate...</option>
                  {unevaluatedJobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.title} at {j.company_name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <label className="text-xs font-semibold text-slate-400 block mb-1">
                Select a checked job to see details:
              </label>
              <select
                value={activeJobId ?? ""}
                onChange={(e) => setSelectedJobId(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2.5 px-3.5 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                {evaluatedJobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    [{Math.round(j.ai_analysis!.match_score)}%] {j.title} at {j.company_name}
                  </option>
                ))}
              </select>
            </div>

            {activeJob && activeJob.ai_analysis && (
              <div className="border-t border-slate-700/60 pt-5 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-start">
                  <div className="bg-slate-900 rounded-xl p-5 border border-slate-850 flex flex-col items-center justify-center text-center">
                    <span className="text-xs font-semibold text-slate-400">Match Fit Score</span>
                    <div className="text-4xl font-bold font-mono text-emerald-400 mt-2">
                      {Math.round(activeJob.ai_analysis.match_score)}%
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2 mt-4 overflow-hidden">
                      <div
                        className="bg-emerald-400 h-2 rounded-full"
                        style={{ width: `${activeJob.ai_analysis.match_score}%` }}
                      />
                    </div>
                  </div>

                  <div className="md:col-span-3 bg-slate-900/40 rounded-xl p-5 border border-slate-800">
                    <span className="text-xs font-semibold text-slate-400 block mb-1">
                      Summary:
                    </span>
                    <p className="text-sm text-slate-300 leading-relaxed font-sans">
                      {activeJob.ai_analysis.fit_summary}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Matched skills */}
                  <div className="bg-slate-900/40 rounded-xl p-5 border border-slate-800/80">
                    <h4 className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5 mb-3 uppercase tracking-wider">
                      <Check className="w-4 h-4" />
                      ✨ Matched Profile Keywords / Skills
                    </h4>
                    {activeJob.ai_analysis.keywords_matched.length === 0 ? (
                      <p className="text-xs text-slate-500 italic">No overlapping keyword signatures explicitly mapped out.</p>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {activeJob.ai_analysis.keywords_matched.map((kw, idx) => (
                          <span
                            key={idx}
                            className="bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 px-2 py-0.5 rounded text-xs font-mono"
                          >
                            {kw}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Missing skills */}
                  <div className="bg-slate-900/40 rounded-xl p-5 border border-slate-800/80">
                    <h4 className="text-xs font-semibold text-rose-400 flex items-center gap-1.5 mb-3 uppercase tracking-wider">
                      <AlertTriangle className="w-4 h-4" />
                      ⚠️ Identified Missing Structural Gaps / Keywords
                    </h4>
                    {activeJob.ai_analysis.keywords_missing.length === 0 ? (
                      <p className="text-xs text-emerald-500/85 font-medium">Excellent! Zero matching requirement gaps caught by parsing engine.</p>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {activeJob.ai_analysis.keywords_missing.map((kw, idx) => (
                          <span
                            key={idx}
                            className="bg-rose-500/10 text-rose-300 border border-rose-500/20 px-2 py-0.5 rounded text-xs font-mono"
                          >
                            {kw}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {unevaluatedJobs.length > 0 && evaluatedJobs.length > 0 && (
        <div className="bg-slate-800/40 rounded-xl p-5 border border-slate-800">
          <h4 className="text-xs font-bold text-slate-300 mb-3">Pending Alignment Audits</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {unevaluatedJobs.slice(0, 4).map((j) => (
              <div
                key={j.id}
                className="bg-slate-900/50 p-3 rounded-lg border border-slate-800 flex items-center justify-between gap-3 text-xs"
              >
                <div className="truncate">
                  <div className="font-semibold text-slate-200 truncate">{j.title}</div>
                  <div className="text-slate-400 truncate">{j.company_name}</div>
                </div>
                <button
                  onClick={() => triggerEvaluation(j.id)}
                  disabled={isEvaluating}
                  className="bg-indigo-600/15 hover:bg-indigo-600/30 text-indigo-300 font-semibold py-1 px-3.5 rounded border border-indigo-500/10 cursor-pointer shrink-0 transition-colors inline-flex items-center gap-1"
                >
                  {isEvaluating && selectedJobId === j.id ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <Play className="w-2.5 h-2.5 fill-current" />
                  )}
                  Align
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
