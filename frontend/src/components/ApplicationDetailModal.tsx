import React, { useState } from "react";
import {
  X,
  Calendar,
  DollarSign,
  FileText,
  Link as LinkIcon,
  MessageSquare,
  Trash2,
  Save,
  CheckCircle,
  ExternalLink
} from "lucide-react";
import { ApplicationStatus, JobListing, Resume } from "../types";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";
import { cn } from "../lib/utils";

interface ApplicationDetailModalProps {
  job: JobListing;
  resumes: Resume[];
  onClose: () => void;
  onUpdate: (appId: number, data: any) => Promise<void>;
  onDelete: (appId: number) => Promise<void>;
}

export default function ApplicationDetailModal({
  job,
  resumes,
  onClose,
  onUpdate,
  onDelete
}: ApplicationDetailModalProps) {
  const app = job.application!;
  const [status, setStatus] = useState<ApplicationStatus>(app.status);
  const [notes, setNotes] = useState(app.notes || "");
  const [salary, setSalary] = useState(app.salary_offered?.toString() || "");
  const [interviewDate, setInterviewDate] = useState(app.interview_date ? new Date(app.interview_date).toISOString().slice(0, 16) : "");
  const [selectedResumeId, setSelectedResumeId] = useState<number | "">(app.resume_id || "");
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    await onUpdate(app.id, {
      status,
      notes,
      salary_offered: salary ? parseFloat(salary) : null,
      interview_date: interviewDate ? new Date(interviewDate).toISOString() : null,
      resume_id: selectedResumeId || null
    });
    setIsSaving(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl border-slate-700/50">
        <CardHeader className="flex flex-row items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-4">
             <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-black">
                {job.company_name.charAt(0)}
             </div>
             <div>
                <CardTitle className="text-xl">{job.title}</CardTitle>
                <div className="text-xs text-slate-500 font-bold uppercase tracking-wider">{job.company_name}</div>
             </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-500">
            <X className="w-5 h-5" />
          </button>
        </CardHeader>

        <CardContent className="flex-1 overflow-y-auto p-8 space-y-8 no-scrollbar">
           {/* Primary Controls */}
           <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-2">
                 <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                   <Target className="w-3 h-3" /> Application Stage
                 </label>
                 <select
                   value={status}
                   onChange={(e) => setStatus(e.target.value as ApplicationStatus)}
                   className="w-full bg-black border border-slate-800 rounded-xl p-3 text-xs font-bold text-white outline-none focus:border-indigo-500 transition-all"
                 >
                    {Object.values(ApplicationStatus).map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                 </select>
              </div>

              <div className="space-y-2">
                 <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                   <Calendar className="w-3 h-3" /> Interview Date
                 </label>
                 <input
                   type="datetime-local"
                   value={interviewDate}
                   onChange={(e) => setInterviewDate(e.target.value)}
                   className="w-full bg-black border border-slate-800 rounded-xl p-3 text-xs font-bold text-white outline-none focus:border-indigo-500 transition-all"
                 />
              </div>
           </div>

           {/* Secondary Controls */}
           <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div className="space-y-2">
                 <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                   <DollarSign className="w-3 h-3" /> Salary Offered
                 </label>
                 <div className="relative">
                    <input
                      type="number"
                      placeholder="e.g. 125000"
                      value={salary}
                      onChange={(e) => setSalary(e.target.value)}
                      className="w-full bg-black border border-slate-800 rounded-xl p-3 pl-8 text-xs font-bold text-white outline-none focus:border-indigo-500 transition-all"
                    />
                    <DollarSign className="absolute left-3 top-3.5 w-3.5 h-3.5 text-slate-600" />
                 </div>
              </div>

              <div className="space-y-2">
                 <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                   <FileText className="w-3 h-3" /> Linked Resume
                 </label>
                 <select
                   value={selectedResumeId}
                   onChange={(e) => setSelectedResumeId(e.target.value ? Number(e.target.value) : "")}
                   className="w-full bg-black border border-slate-800 rounded-xl p-3 text-xs font-bold text-white outline-none focus:border-indigo-500 transition-all"
                 >
                    <option value="">No resume linked</option>
                    {resumes.map(r => (
                      <option key={r.id} value={r.id}>{r.name}</option>
                    ))}
                 </select>
              </div>
           </div>

           {/* Notes */}
           <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <MessageSquare className="w-3 h-3" /> Internal Notes
              </label>
              <textarea
                placeholder="Log thoughts, feedback, or next steps..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
                className="w-full bg-black border border-slate-800 rounded-2xl p-4 text-xs font-medium text-slate-300 outline-none focus:border-indigo-500 transition-all resize-none"
              />
           </div>

           {/* Quick Actions */}
           <div className="pt-4 flex items-center gap-4">
              <a
                href={job.url}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 text-[10px] font-black text-indigo-400 uppercase tracking-widest hover:text-indigo-300 transition-colors"
              >
                View Original Listing <ExternalLink className="w-3 h-3" />
              </a>
           </div>
        </CardContent>

        <footer className="p-6 border-t border-slate-800 bg-slate-950/50 flex items-center justify-between">
           <Button variant="danger" size="sm" onClick={() => onDelete(app.id)}>
              <Trash2 className="w-3.5 h-3.5 mr-2" /> Delete
           </Button>
           <div className="flex items-center gap-3">
              <Button variant="secondary" size="md" onClick={onClose}>Cancel</Button>
              <Button variant="primary" size="md" onClick={handleSave} disabled={isSaving}>
                 {isSaving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <><Save className="w-4 h-4 mr-2" /> Save Changes</>}
              </Button>
           </div>
        </footer>
      </Card>
    </div>
  );
}

function Target(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="6" />
      <circle cx="12" cy="12" r="2" />
    </svg>
  )
}

function RefreshCw(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
      <path d="M3 3v5h5" />
      <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
      <path d="M16 16h5v5" />
    </svg>
  )
}
