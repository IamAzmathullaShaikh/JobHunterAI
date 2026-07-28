import React, { useState } from "react";
import { ApplicationStatus, JobListing, Resume } from "../types.ts";
import {
  ClipboardList,
  CheckCircle2,
  ChevronRight,
  MessageSquare,
  Loader2,
  Target,
  Calendar,
  DollarSign,
  FileText,
  Clock,
  ArrowRight,
  Plus
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";
import { cn } from "../lib/utils";
import ApplicationDetailModal from "./ApplicationDetailModal";

interface KanbanBoardProps {
  jobs: JobListing[];
  resumes: Resume[];
  onUpdateCard: (appId: number, data: any) => Promise<void>;
  onTrackJob: (jobId: number) => Promise<void>;
}

export default function KanbanBoard({
  jobs,
  resumes,
  onUpdateCard,
  onTrackJob,
}: KanbanBoardProps) {
  const [viewMode, setViewMode] = useState<"kanban" | "intake">("kanban");
  const [selectedJob, setSelectedJob] = useState<JobListing | null>(null);

  const trackedJobs = jobs.filter((j) => j.application);
  const untrackedJobs = jobs.filter((j) => !j.application);

  const handleUpdate = async (appId: number, data: any) => {
      await onUpdateCard(appId, data);
  };

  const handleDelete = async (appId: number) => {
      // Future: add delete implementation
      console.log("Delete application", appId);
  };

  const columns = [
    { title: "Wishlist", statuses: [ApplicationStatus.WISHLIST], color: "text-indigo-400", bg: "bg-indigo-400/5" },
    { title: "Applied", statuses: [ApplicationStatus.APPLIED], color: "text-sky-400", bg: "bg-sky-400/5" },
    { title: "Interviewing", statuses: [ApplicationStatus.INTERVIEWING], color: "text-amber-400", bg: "bg-amber-400/5" },
    { title: "Outcomes", statuses: [ApplicationStatus.OFFERED, ApplicationStatus.REJECTED, ApplicationStatus.ARCHIVED], color: "text-emerald-400", bg: "bg-emerald-400/5" },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-black tracking-tight text-white flex items-center gap-3">
            <ClipboardList className="w-8 h-8 text-indigo-500" />
            Application <span className="text-indigo-400 italic">Pipeline</span>
          </h2>
          <p className="text-slate-500 text-sm mt-1 font-medium italic">Manage your active pursuits with enterprise precision.</p>
        </div>

        <div className="flex bg-slate-900/50 rounded-2xl p-1 border border-slate-800">
           <button
             onClick={() => setViewMode("kanban")}
             className={cn(
               "px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all",
               viewMode === "kanban" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20" : "text-slate-500 hover:text-slate-300"
             )}
           >
             Board
           </button>
           <button
             onClick={() => setViewMode("intake")}
             className={cn(
               "px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all flex items-center gap-2",
               viewMode === "intake" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20" : "text-slate-500 hover:text-slate-300"
             )}
           >
             Intake Queue
             {untrackedJobs.length > 0 && <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />}
           </button>
        </div>
      </div>

      {viewMode === "kanban" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 items-start">
           {columns.map((col, idx) => {
              const colJobs = trackedJobs.filter(j => col.statuses.includes(j.application!.status));
              return (
                <div key={idx} className={cn("rounded-[32px] p-2 border border-slate-800/50 min-h-[600px] flex flex-col", col.bg)}>
                   <div className="p-4 flex items-center justify-between">
                      <span className={cn("text-[10px] font-black uppercase tracking-[0.2em]", col.color)}>{col.title}</span>
                      <span className="bg-black/40 px-2.5 py-0.5 rounded-full border border-slate-800/50 text-[10px] font-bold text-slate-400">{colJobs.length}</span>
                   </div>

                   <div className="flex-1 p-2 space-y-4 overflow-y-auto no-scrollbar">
                      {colJobs.map(job => (
                        <Card
                          key={job.id}
                          className="p-1 hover:border-indigo-500/40 cursor-pointer active:scale-[0.98] transition-all group border-slate-800"
                          onClick={() => setSelectedJob(job)}
                        >
                           <div className="bg-black/40 rounded-[22px] p-5 border border-transparent group-hover:border-indigo-500/10">
                              <div className="text-xs font-bold text-white mb-1 leading-snug group-hover:text-indigo-400 transition-colors">{job.title}</div>
                              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{job.company_name}</div>

                              <div className="mt-4 flex flex-wrap gap-2">
                                 {job.application?.interview_date && (
                                   <div className="flex items-center gap-1.5 bg-amber-500/10 text-amber-500 px-2 py-1 rounded-lg border border-amber-500/20 text-[9px] font-black uppercase tracking-widest">
                                      <Clock className="w-2.5 h-2.5" /> {new Date(job.application.interview_date).toLocaleDateString()}
                                   </div>
                                 )}
                                 {job.application?.resume_id && (
                                   <div className="flex items-center gap-1.5 bg-indigo-500/10 text-indigo-400 px-2 py-1 rounded-lg border border-indigo-500/20 text-[9px] font-black uppercase tracking-widest">
                                      <FileText className="w-2.5 h-2.5" /> V{job.application.resume_id}
                                   </div>
                                 )}
                                 {job.application?.salary_offered && (
                                   <div className="flex items-center gap-1.5 bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded-lg border border-emerald-500/20 text-[9px] font-black uppercase tracking-widest">
                                      <DollarSign className="w-2.5 h-2.5" /> {job.application.salary_offered.toLocaleString()}
                                   </div>
                                 )}
                              </div>
                           </div>
                        </Card>
                      ))}
                      {colJobs.length === 0 && (
                        <div className="h-32 flex items-center justify-center border border-dashed border-slate-800/50 rounded-3xl">
                           <span className="text-[10px] font-bold text-slate-700 uppercase tracking-widest italic">No {col.title}</span>
                        </div>
                      )}
                   </div>
                </div>
              )
           })}
        </div>
      ) : (
        /* Intake Queue */
        <Card className="rounded-[40px] overflow-hidden">
           <div className="p-8 border-b border-slate-800 flex items-center justify-between">
              <h3 className="text-xl font-black text-white italic underline decoration-indigo-500 underline-offset-8">Intake <span className="text-slate-500 not-italic">Queue</span></h3>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{untrackedJobs.length} Discovered roles pending triage</p>
           </div>

           <div className="divide-y divide-slate-800/50">
              {untrackedJobs.map(job => (
                <div key={job.id} className="p-6 flex items-center justify-between hover:bg-white/[0.02] transition-colors group">
                   <div className="flex items-center gap-6">
                      <div className="w-12 h-12 rounded-2xl bg-black border border-slate-800 flex items-center justify-center text-sm font-black text-slate-500 group-hover:border-indigo-500/50 transition-colors">
                         {job.company_name.charAt(0)}
                      </div>
                      <div>
                         <div className="text-sm font-bold text-white group-hover:text-indigo-400 transition-colors">{job.title}</div>
                         <div className="flex items-center gap-3 mt-1">
                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{job.company_name}</span>
                            <span className="text-slate-800 text-[10px]">•</span>
                            <span className="text-[10px] text-slate-600 font-medium italic">{job.location}</span>
                         </div>
                      </div>
                   </div>

                   <div className="flex items-center gap-8">
                      <div className="hidden lg:flex flex-col items-end gap-1">
                         <span className="text-[10px] font-black text-slate-700 uppercase tracking-widest">Source</span>
                         <span className="text-[10px] font-bold text-indigo-400/70">{job.source}</span>
                      </div>
                      <Button variant="secondary" size="md" onClick={() => onTrackJob(job.id)} className="rounded-2xl border-slate-700">
                         Track Role <Plus className="w-3.5 h-3.5 ml-2" />
                      </Button>
                   </div>
                </div>
              ))}
              {untrackedJobs.length === 0 && (
                <div className="p-32 text-center space-y-6 bg-slate-900/10">
                   <div className="inline-flex p-6 rounded-[40px] bg-indigo-500/5 border border-indigo-500/10">
                      <CheckCircle2 className="w-12 h-12 text-indigo-500" />
                   </div>
                   <div>
                      <p className="text-white font-black uppercase tracking-tighter text-lg">Intake Complete</p>
                      <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mt-1">No new job postings discovered. Run the scraper fleet to find more.</p>
                   </div>
                </div>
              )}
           </div>
        </Card>
      )}

      {/* Detail Modal */}
      {selectedJob && (
        <ApplicationDetailModal
          job={selectedJob}
          resumes={resumes}
          onClose={() => setSelectedJob(null)}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
        />
      )}
    </div>
  );
}
