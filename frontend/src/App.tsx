import React, { useState, useEffect } from "react";
import {
  RefreshCw,
  CheckCircle,
  FileText,
  ShieldCheck,
  Search,
  Bell,
  User,
  Settings as SettingsIcon,
  Menu
} from "lucide-react";
import { CandidateProfile, JobListing, Resume } from "./types.ts";
import Sidebar from "./components/Sidebar.tsx";
import MissionControl from "./components/MissionControl.tsx";
import ResumeDrawer from "./components/ResumeDrawer.tsx";
import ResumeIngestion from "./components/ResumeIngestion.tsx";
import JobsTable from "./components/JobsTable.tsx";
import AnalysisMatrix from "./components/AnalysisMatrix.tsx";
import KanbanBoard from "./components/KanbanBoard.tsx";
import ErrorBoundary from "./components/ErrorBoundary.tsx";
import ResumeWriter from "./components/ResumeWriter.tsx";
import ResumeBuilder from "./components/ResumeBuilder.tsx";
import RecruiterFinder from "./components/RecruiterFinder.tsx";
import AnalyticsDashboard from "./components/AnalyticsDashboard.tsx";
import JobDiscovery from "./components/JobDiscovery.tsx";
import InterviewPrepStudio from "./components/InterviewPrepStudio.tsx";
import CoverLetterBuilder from "./components/CoverLetterBuilder.tsx";
import { cn } from "./lib/utils.ts";

export default function App() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  );
}

function Dashboard() {
  const [activeTab, setActiveTab] = useState<"home" | "ats" | "writer" | "builder" | "cover" | "prep" | "recruiters" | "jobs" | "kanban" | "analytics">("home");
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [jobs, setJobs] = useState<JobListing[]>([]);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [resumeText, setResumeText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isPrivacyMode, setIsPrivacyMode] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [telemetry, setTelemetry] = useState<any>(null);

  // Fetch initial data
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const responses = await Promise.allSettled([
          fetch("/api/profile"),
          fetch("/api/jobs?mode=all"),
          fetch("/api/resumes"),
          fetch("/api/system/telemetry")
        ]);

        const [pRes, jRes, rRes, tRes] = responses;

        if (pRes.status === "fulfilled" && pRes.value.ok) {
          const pData = await pRes.value.json();
          if (pData.profile) setProfile(pData.profile);
        }

        if (jRes.status === "fulfilled" && jRes.value.ok) {
          const jData = await jRes.value.json();
          setJobs(jData.jobs || []);
        }

        if (rRes.status === "fulfilled" && rRes.value.ok) {
          const rData = await rRes.value.json();
          setResumes(rData || []);
        }

        if (tRes.status === "fulfilled" && tRes.value.ok) {
          const tData = await tRes.value.json();
          setTelemetry(tData);
        }
      } catch (err) {
        console.error("Critical error during data ingestion:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleProfileParsed = (newProfile: CandidateProfile) => {
    setProfile(newProfile);
    showToast("Profile Successfully Mapped!");
  };

  const handleJobsDiscovered = (updatedJobs: JobListing[]) => {
    setJobs(updatedJobs);
    showToast("Scraper Pipeline run complete!");
  };

  const handleTrackJob = async (jobId: number) => {
    try {
      const response = await fetch("/api/jobs/track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: jobId }),
      });
      if (response.ok) {
        const resData = await response.json();
        setJobs((prev) => prev.map((j) => (j.id === jobId ? { ...j, application: resData.job.application } : j)));
        showToast("Role moved into tracked pipeline!");
      }
    } catch (err) { console.error(err); }
  };

  const handleUpdateApplicationCard = async (applicationId: number, data: any) => {
    try {
      const response = await fetch("/api/tracker/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ application_id: applicationId, ...data }),
      });
      if (response.ok) {
        const jRes = await fetch("/api/jobs?mode=all");
        if (jRes.ok) {
          const jData = await jRes.json();
          setJobs(jData.jobs || []);
        }
        showToast("Application updated!");
      }
    } catch (err) { console.error(err); }
  };

  return (
    <div className="flex h-screen bg-black text-slate-100 overflow-hidden font-sans selection:bg-indigo-500/30">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
        telemetry={telemetry}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {/* Unified Header */}
        <header className="h-16 border-b border-slate-900 bg-black/50 backdrop-blur-md flex items-center justify-between px-8 shrink-0 z-40">
           <div className="flex items-center gap-4">
              <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-2">
                 <span>JobHunterAI</span>
                 <span className="text-slate-800">/</span>
                 <span className="text-slate-200">{activeTab.toUpperCase()}</span>
              </div>
           </div>

           <div className="flex items-center gap-6">
              <div className="hidden md:flex items-center gap-2 bg-slate-900/50 px-3 py-1.5 rounded-xl border border-slate-800">
                <Search className="w-3.5 h-3.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Command + K"
                  className="bg-transparent border-none outline-none text-[10px] font-bold text-slate-400 w-24"
                />
              </div>

              <div className="flex items-center gap-4">
                 <button onClick={() => setIsPrivacyMode(!isPrivacyMode)} className={cn(
                   "p-2 rounded-lg transition-colors",
                   isPrivacyMode ? "bg-emerald-500/10 text-emerald-500" : "text-slate-500 hover:bg-slate-900"
                 )}>
                    <ShieldCheck className="w-4 h-4" />
                 </button>
                 <button className="text-slate-500 hover:text-slate-200"><Bell className="w-4 h-4" /></button>
                 <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 border border-slate-800 flex items-center justify-center text-[10px] font-black">
                    {profile?.full_name?.charAt(0) || "U"}
                 </div>
              </div>
           </div>
        </header>

        {/* Content Wrapper */}
        <main className="flex-1 overflow-y-auto p-8 no-scrollbar">
          {isLoading ? (
             <div className="h-full flex flex-col items-center justify-center space-y-6">
                <div className="relative">
                   <RefreshCw className="w-12 h-12 text-indigo-500 animate-spin" />
                   <div className="absolute inset-0 blur-xl bg-indigo-500/20 animate-pulse" />
                </div>
                <div className="text-center">
                   <p className="text-sm font-black text-white uppercase tracking-tighter">Synchronizing Career Fleet</p>
                   <p className="text-[10px] text-slate-500 font-bold uppercase mt-1">Initializing Secure AI Context...</p>
                </div>
             </div>
          ) : (
            <div className="max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
               {activeTab === "home" && (
                 <MissionControl jobs={jobs} profile={profile} onNavigate={setActiveTab} />
               )}

               {activeTab === "ats" && (
                 <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                    <ResumeIngestion profile={profile} onProfileParsed={handleProfileParsed} resumeText={resumeText} setResumeText={setResumeText} />
                    <AnalysisMatrix jobs={jobs} resumeText={resumeText} onAnalysisComplete={setJobs} />
                 </div>
               )}

               {activeTab === "writer" && <ResumeWriter resumeText={resumeText} />}
               {activeTab === "builder" && <ResumeBuilder profile={profile} />}
               {activeTab === "jobs" && <JobDiscovery profile={profile} jobs={jobs} onJobsDiscovered={handleJobsDiscovered} onTrackJob={handleTrackJob} resumeText={resumeText} />}
               {activeTab === "cover" && <CoverLetterBuilder resumes={resumes} jobs={jobs} profile={profile} />}
               {activeTab === "prep" && <InterviewPrepStudio resumes={resumes} jobs={jobs} />}
               {activeTab === "recruiters" && <RecruiterFinder resumeText={resumeText} profile={profile} resumes={resumes} />}
               {activeTab === "kanban" && <KanbanBoard jobs={jobs} resumes={resumes} onUpdateCard={handleUpdateApplicationCard} onTrackJob={handleTrackJob} />}
               {activeTab === "analytics" && <AnalyticsDashboard />}
            </div>
          )}
        </main>

        {/* Global Shared Resume Drawer */}
        <ResumeDrawer
          isOpen={isDrawerOpen}
          onClose={() => setIsDrawerOpen(false)}
          resumeText={resumeText}
          onTextChange={setResumeText}
        />

        {/* Floating Toggle for Resume Drawer on small screens */}
        <button
          onClick={() => setIsDrawerOpen(true)}
          className="fixed bottom-8 left-8 bg-indigo-600 p-3 rounded-2xl shadow-2xl text-white md:hidden"
        >
          <FileText className="w-5 h-5" />
        </button>
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-8 right-8 z-[100] bg-slate-900 border border-slate-800 text-slate-100 px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-4 animate-in slide-in-from-right-full duration-300">
          <div className="bg-emerald-500/10 p-2 rounded-lg">
            <CheckCircle className="w-4 h-4 text-emerald-500" />
          </div>
          <span className="text-xs font-bold">{toastMessage}</span>
        </div>
      )}
    </div>
  );
}
