import React, { useState } from "react";
import { ApplicationStatus, JobListing } from "../types.ts";
import { ClipboardList, CheckCircle2, ChevronRight, MessageSquare, Loader2, Award, Ban } from "lucide-react";

interface KanbanBoardProps {
  jobs: JobListing[];
  onUpdateCard: (appId: number, status: ApplicationStatus, notes: string) => Promise<void>;
  onTrackJob: (jobId: number) => Promise<void>;
}

export default function KanbanBoard({
  jobs,
  onUpdateCard,
  onTrackJob,
}: KanbanBoardProps) {
  const [viewMode, setViewMode] = useState<"kanban" | "intake">("kanban");
  const [updatingCardId, setUpdatingCardId] = useState<number | null>(null);
  const [cardStates, setCardStates] = useState<Record<number, { status: ApplicationStatus; notes: string }>>({});

  const trackedJobs = jobs.filter((j) => j.application);
  const untrackedJobs = jobs.filter((j) => !j.application);

  const initCardState = (appId: number, currentStatus: ApplicationStatus, currentNotes: string) => {
    if (!cardStates[appId]) {
      setCardStates((prev) => ({
        ...prev,
        [appId]: { status: currentStatus, notes: currentNotes || "" },
      }));
    }
  };

  const handleStateChange = (appId: number, field: "status" | "notes", value: any) => {
    setCardStates((prev) => ({
      ...prev,
      [appId]: {
        ...prev[appId],
        [field]: value,
      },
    }));
  };

  const handleUpdateClick = async (appId: number) => {
    const card = cardStates[appId];
    if (!card) return;
    setUpdatingCardId(appId);
    try {
      await onUpdateCard(appId, card.status, card.notes);
    } catch (err) {
      console.error(err);
    } finally {
      setUpdatingCardId(null);
    }
  };

  // Define Kanban Columns
  const columns = [
    {
      title: "📥 Identified & Ready",
      statuses: [ApplicationStatus.IDENTIFIED, ApplicationStatus.AI_READY],
      color: "border-indigo-500/45 text-indigo-300",
      bg: "bg-indigo-950/10",
    },
    {
      title: "🚀 Applied",
      statuses: [ApplicationStatus.APPLIED],
      color: "border-sky-500/45 text-sky-300",
      bg: "bg-sky-950/10",
    },
    {
      title: "📅 Interviewing",
      statuses: [ApplicationStatus.INTERVIEWING],
      color: "border-amber-500/45 text-amber-300",
      bg: "bg-amber-950/10",
    },
    {
      title: "🏆 Outcomes",
      statuses: [ApplicationStatus.OFFER, ApplicationStatus.REJECTED, ApplicationStatus.ARCHIVED],
      color: "border-emerald-500/45 text-emerald-300",
      bg: "bg-emerald-950/10",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Selector */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <ClipboardList className="w-5 h-5 text-indigo-400" />
            📊 Job Tracker Funnel
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Keep track of interview requests, outcomes, and progress comments.
          </p>
        </div>
        <div className="flex bg-slate-900 rounded-lg p-1 text-xs">
          <button
            onClick={() => setViewMode("kanban")}
            className={`px-4 py-2 rounded-md font-semibold transition-all ${
              viewMode === "kanban"
                ? "bg-indigo-600 text-slate-100 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            📊 Kanban Board
          </button>
          <button
            onClick={() => setViewMode("intake")}
            className={`px-4 py-2 rounded-md font-semibold transition-all flex items-center gap-1.5 ${
              viewMode === "intake"
                ? "bg-indigo-600 text-slate-100 shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            📥 Intake Queue
            {untrackedJobs.length > 0 && (
              <span className="bg-rose-500 text-white text-[10px] w-4 h-4 flex items-center justify-center rounded-full">
                {untrackedJobs.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {viewMode === "kanban" ? (
        trackedJobs.length === 0 ? (
          <div className="p-16 border border-dashed border-slate-700 bg-slate-900/20 rounded-xl text-center">
            <ClipboardList className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <h4 className="text-sm font-semibold text-slate-300">No active applications tracked</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Head over to the "Intake Queue" sub-tab to move crawled job postings into the active funnel tracking board.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            {columns.map((col, cIdx) => {
              const colJobs = trackedJobs.filter((j) => col.statuses.includes(j.application!.status));

              return (
                <div key={cIdx} className={`rounded-xl p-4 border border-slate-800 ${col.bg} flex flex-col gap-4 min-h-[500px]`}>
                  <div className={`text-sm font-bold flex items-center justify-between pb-2 border-b border-slate-800 ${col.color}`}>
                    <span>{col.title}</span>
                    <span className="bg-slate-900 px-2 py-0.5 rounded text-xs font-mono">
                      {colJobs.length}
                    </span>
                  </div>

                  <div className="flex-1 space-y-4 overflow-y-auto max-h-[600px] pr-1">
                    {colJobs.map((job) => {
                      const app = job.application!;
                      initCardState(app.id, app.status, app.notes || "");
                      const localState = cardStates[app.id] || { status: app.status, notes: app.notes || "" };

                      // Determine card status badges/styling
                      const hasOffer = app.status === ApplicationStatus.OFFER;
                      const hasRej = app.status === ApplicationStatus.REJECTED;

                      return (
                        <div
                          key={job.id}
                          className={`bg-slate-900 rounded-lg p-4 border transition-all ${
                            hasOffer
                              ? "border-emerald-500/30"
                              : hasRej
                              ? "border-rose-500/20"
                              : "border-slate-800 hover:border-slate-750"
                          }`}
                        >
                          <div className="font-bold text-slate-100 text-sm leading-tight">
                            {job.title}
                          </div>
                          <div className="text-xs text-slate-400 mt-1 font-medium truncate">
                            {job.company_name} • <span className="text-slate-500">{job.location}</span>
                          </div>

                          <div className="flex items-center gap-1.5 mt-2">
                            <span className="bg-slate-950 text-indigo-400 text-[10px] font-semibold px-2 py-0.5 rounded uppercase font-mono">
                              {job.source}
                            </span>
                            {job.ai_analysis && (
                              <span className="bg-slate-950 text-emerald-400 text-[10px] font-semibold px-2 py-0.5 rounded font-mono">
                                🎯 {Math.round(job.ai_analysis.match_score)}%
                              </span>
                            )}
                          </div>

                          {/* Quick controls inside cards */}
                          <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-3">
                            <div>
                              <label className="text-[10px] font-semibold text-slate-500 block mb-0.5">
                                Move Stage
                              </label>
                              <select
                                value={localState.status}
                                onChange={(e) => handleStateChange(app.id, "status", e.target.value as ApplicationStatus)}
                                className="w-full bg-slate-950 border border-slate-800 rounded py-1 px-2 text-xs text-slate-300 focus:outline-none"
                              >
                                {Object.values(ApplicationStatus).map((st) => (
                                  <option key={st} value={st}>
                                    {st}
                                  </option>
                                ))}
                              </select>
                            </div>

                            <div>
                              <label className="text-[10px] font-semibold text-slate-500 block mb-0.5 flex items-center gap-1">
                                <MessageSquare className="w-3 h-3" /> Notes
                              </label>
                              <input
                                type="text"
                                value={localState.notes}
                                onChange={(e) => handleStateChange(app.id, "notes", e.target.value)}
                                className="w-full bg-slate-950 border border-slate-800 rounded py-1 px-2 text-xs text-slate-300 focus:outline-none"
                                placeholder="Add note..."
                              />
                            </div>

                            <button
                              onClick={() => handleUpdateClick(app.id)}
                              disabled={updatingCardId === app.id}
                              className="w-full bg-slate-800 hover:bg-slate-750 text-slate-200 text-xs font-semibold py-1 px-2 rounded flex items-center justify-center gap-1.5 transition-colors cursor-pointer border border-slate-700/50"
                            >
                              {updatingCardId === app.id ? (
                                <Loader2 className="w-3 h-3 animate-spin" />
                              ) : (
                                "Update Card"
                              )}
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        )
      ) : (
        <div className="bg-slate-800/60 rounded-xl p-5 border border-slate-700/80 shadow-md">
          <h4 className="text-sm font-semibold text-slate-200 mb-1">Discovered Job Intake Funnel</h4>
          <p className="text-xs text-slate-400 mb-4">
            Instantly index newly crawled web listings directly into your workflow columns.
          </p>

          {untrackedJobs.length === 0 ? (
            <div className="p-12 text-center text-slate-400 border border-dashed border-slate-700 rounded-lg bg-slate-900/20">
              <CheckCircle2 className="w-10 h-12 text-emerald-500 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-300">Intake queue is empty!</p>
              <p className="text-xs text-slate-500 mt-1">
                Excellent! Every single crawled job has been pulled safely into your active tracking pipelines.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-800 space-y-4">
              {untrackedJobs.map((job) => (
                <div key={job.id} className="pt-4 first:pt-0 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <div className="font-semibold text-slate-100 text-sm flex items-center gap-2">
                      📦 {job.title} at <span className="text-indigo-300 font-medium">{job.company_name}</span>
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">
                      Source: <code className="bg-slate-900/80 text-indigo-400 px-1 py-0.5 rounded font-mono text-[11px] border border-slate-800">{job.source}</code>
                      {job.ai_analysis && (
                        <>
                          {" • Match Fit: "}
                          <strong className="text-emerald-400">{Math.round(job.ai_analysis.match_score)}%</strong>
                        </>
                      )}
                      {" • "}
                      <span className="text-slate-500 italic font-sans">{job.location}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => onTrackJob(job.id)}
                    className="bg-indigo-600 hover:bg-indigo-500 text-slate-100 font-bold text-xs py-1.5 px-4 rounded-lg flex items-center gap-1.5 transition-all shadow shrink-0 self-start sm:self-center cursor-pointer"
                  >
                    Track Job
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
