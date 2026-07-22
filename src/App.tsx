import React, { useState, useEffect } from "react";
import {
  Sparkles,
  Briefcase,
  Brain,
  ClipboardList,
  RefreshCw,
  Download,
  Trash2,
  CheckCircle,
  HelpCircle,
  Users,
  FileText,
  X,
  Upload,
  ShieldCheck,
  Target,
  FileSignature,
  MessageSquare,
  ListTodo,
  Settings,
  BarChart3,
  Layout
} from "lucide-react";
import { CandidateProfile, JobListing, ApplicationStatus } from "./types.ts";
import ResumeDrawer from "./components/ResumeDrawer.tsx";
import EngineStatusChip from "./components/EngineStatusChip.tsx";
import ResumeIngestion from "./components/ResumeIngestion.tsx";
import ScraperFleet from "./components/ScraperFleet.tsx";
import JobsTable from "./components/JobsTable.tsx";
import AnalysisMatrix from "./components/AnalysisMatrix.tsx";
import KanbanBoard from "./components/KanbanBoard.tsx";
import ContactFinder from "./components/ContactFinder.tsx";
import ErrorBoundary from "./components/ErrorBoundary.tsx";

import ResumeWriter from "./components/ResumeWriter.tsx";
import ResumeBuilder from "./components/ResumeBuilder.tsx";
import RecruiterFinder from "./components/RecruiterFinder.tsx";
import AnalyticsDashboard from "./components/AnalyticsDashboard.tsx";
import JobDiscovery from "./components/JobDiscovery.tsx";

export default function App() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  );
}

function Dashboard() {
  const [activeTab, setActiveTab] = useState<"ats" | "writer" | "builder" | "cover" | "prep" | "recruiters" | "jobs" | "kanban" | "analytics">("ats");
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [jobs, setJobs] = useState<JobListing[]>([]);
  const [resumeText, setResumeText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isPrivacyMode, setIsPrivacyMode] = useState(false);
  const [telemetry, setTelemetry] = useState<any>(null);

  // Fetch initial profile, jobs, and telemetry
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const responses = await Promise.allSettled([
          fetch("/api/profile/"),
          fetch("/api/jobs/"),
          fetch("/api/system/telemetry/")
        ]);

        const [pRes, jRes, tRes] = responses;

        if (pRes.status === "fulfilled" && pRes.value.ok) {
          const pData = await pRes.value.json();
          if (pData.profile) setProfile(pData.profile);
        }

        if (jRes.status === "fulfilled" && jRes.value.ok) {
          const jData = await jRes.value.json();
          setJobs(jData.jobs || []);
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

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-5 right-5 z-[100] bg-slate-800 border-l-4 border-emerald-400 text-slate-100 px-4 py-3 rounded-lg shadow-2xl flex items-center gap-2.5 max-w-sm animate-slide-in">
          <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
          <span className="text-sm font-medium">{toastMessage}</span>
        </div>
      )}

      {/* Global Shared Resume Drawer */}
      <ResumeDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        resumeText={resumeText}
        onTextChange={setResumeText}
      />

      {/* Modern Header Navigation */}
      <header className="bg-slate-900/50 backdrop-blur-xl border-b border-slate-800/80 px-6 py-4 sticky top-0 z-40">
        <div className="max-w-[1440px] mx-auto flex flex-col xl:flex-row xl:items-center justify-between gap-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-indigo-600 p-2 rounded-xl shadow-lg shadow-indigo-600/20">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-black tracking-tight text-white uppercase italic">JobHunter<span className="text-indigo-400">AI</span></h1>
                <div className="flex items-center gap-2 mt-0.5">
                  <EngineStatusChip source="groq_ai" latency={telemetry?.circuit_breakers?.groq?.latency} />
                  <div className={`w-1.5 h-1.5 rounded-full ${telemetry?.keys?.groq ? "bg-emerald-500 animate-pulse" : "bg-slate-600"}`} />
                </div>
              </div>
            </div>

            <div className="xl:hidden">
               <button onClick={() => setIsDrawerOpen(true)} className="bg-slate-800 p-2 rounded-lg">
                 <FileText className="w-5 h-5" />
               </button>
            </div>
          </div>

          <nav className="flex items-center gap-1 bg-slate-950/50 p-1.5 rounded-2xl border border-slate-800/50 overflow-x-auto no-scrollbar max-w-full">
            {[
              { id: "ats", label: "ATS Matcher", icon: Target },
              { id: "writer", label: "Resume Writer", icon: FileSignature },
              { id: "builder", label: "Resume Builder", icon: Layout },
              { id: "cover", label: "Cover Letter", icon: FileText },
              { id: "prep", label: "Prep Studio", icon: Brain },
              { id: "recruiters", label: "Recruiter Finder", icon: Users },
              { id: "jobs", label: "Job Board", icon: Briefcase },
              { id: "kanban", label: "Tracker CRM", icon: ClipboardList },
              { id: "analytics", label: "Analytics", icon: BarChart3 },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20"
                    : "text-slate-400 hover:text-slate-100 hover:bg-slate-800"
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-slate-800/40 px-3 py-1.5 rounded-xl border border-slate-700/50">
               <ShieldCheck className={`w-4 h-4 ${isPrivacyMode ? "text-emerald-400" : "text-slate-500"}`} />
               <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Privacy</span>
               <button
                 onClick={() => setIsPrivacyMode(!isPrivacyMode)}
                 className={`w-8 h-4 rounded-full relative transition-colors ${isPrivacyMode ? "bg-emerald-500" : "bg-slate-700"}`}
               >
                 <div className={`absolute top-0.5 w-3 h-3 bg-white rounded-full transition-all ${isPrivacyMode ? "left-4.5" : "left-0.5"}`} />
               </button>
            </div>

            <button
              onClick={() => setIsDrawerOpen(true)}
              className="hidden xl:flex items-center gap-2 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 px-4 py-2 rounded-xl text-sm font-bold border border-indigo-500/20 transition-all"
            >
              <FileText className="w-4 h-4" />
              Shared Resume
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-[1440px] w-full mx-auto p-6">
        {isLoading ? (
          <div className="h-full flex flex-col items-center justify-center space-y-4">
            <RefreshCw className="w-10 h-10 text-indigo-500 animate-spin" />
            <p className="text-slate-400 font-bold animate-pulse uppercase tracking-tighter">Initializing AI Engines...</p>
          </div>
        ) : (
          <div className="space-y-6 animate-fade-in">
             {/* Tab Content Mapping */}
             {activeTab === "ats" && (
               <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  <ResumeIngestion profile={profile} onProfileParsed={handleProfileParsed} resumeText={resumeText} setResumeText={setResumeText} />
                  <AnalysisMatrix jobs={jobs} resumeText={resumeText} onAnalysisComplete={setJobs} />
               </div>
             )}

             {activeTab === "writer" && <ResumeWriter resumeText={resumeText} />}

             {activeTab === "builder" && <ResumeBuilder />}

             {activeTab === "jobs" && (
               <JobDiscovery
                 profile={profile}
                 jobs={jobs}
                 onJobsDiscovered={handleJobsDiscovered}
                 onTrackJob={handleTrackJob}
                 resumeText={resumeText}
               />
             )}

             {activeTab === "cover" && (
               <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 text-center">
                  <FileSignature className="w-12 h-12 text-indigo-400 mx-auto mb-4" />
                  <h2 className="text-xl font-black text-white mb-2">Tiered Cover Letter Engine</h2>
                  <p className="text-slate-400 mb-6 max-w-md mx-auto">Generate hyper-tailored cover letters using Llama 3.3 with local Markdown formatting fallbacks.</p>
                  <button className="bg-indigo-600 px-8 py-3 rounded-2xl font-black text-white hover:scale-105 transition-transform">Create New Draft</button>
               </div>
             )}

             {activeTab === "prep" && (
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8">
                   <div className="flex items-center gap-4 mb-8">
                      <Brain className="w-8 h-8 text-purple-400" />
                      <h2 className="text-xl font-black text-white">Interview Prep Studio</h2>
                   </div>
                   <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
                      <div className="p-6 bg-slate-800/50 rounded-2xl border border-slate-700/50 hover:border-indigo-500/50 transition-all cursor-pointer">
                         <h3 className="font-bold text-indigo-400 mb-2 uppercase tracking-widest text-[10px]">Behavioral</h3>
                         <p className="text-sm text-white font-bold mb-2">STAR Method Master</p>
                         <p className="text-xs text-slate-400">Practice common culture-fit questions with AI feedback.</p>
                      </div>
                      <div className="p-6 bg-slate-800/50 rounded-2xl border border-slate-700/50 hover:border-emerald-500/50 transition-all cursor-pointer">
                         <h3 className="font-bold text-emerald-400 mb-2 uppercase tracking-widest text-[10px]">Technical</h3>
                         <p className="text-sm text-white font-bold mb-2">System Design & DSA</p>
                         <p className="text-xs text-slate-400">Deep dives into stack-specific concepts and coding challenges.</p>
                      </div>
                      <div className="p-6 bg-slate-800/50 rounded-2xl border border-slate-700/50 hover:border-amber-500/50 transition-all cursor-pointer group">
                         <h3 className="font-bold text-amber-400 mb-2 uppercase tracking-widest text-[10px]">Interactive</h3>
                         <p className="text-sm text-white font-bold mb-2">Voice Mock Studio</p>
                         <p className="text-xs text-slate-400 italic opacity-50">Local Speech-to-Text integration coming soon.</p>
                      </div>
                   </div>
                </div>
             )}

             {activeTab === "recruiters" && <RecruiterFinder />}

             {activeTab === "kanban" && (
                <KanbanBoard
                  jobs={jobs}
                  onUpdateCard={handleUpdateApplicationCard}
                  onTrackJob={handleTrackJob}
                />
             )}

             {activeTab === "analytics" && <AnalyticsDashboard />}
          </div>
        )}
      </main>

      <footer className="px-6 py-8 text-center">
         <div className="flex items-center justify-center gap-6 text-[10px] font-black text-slate-600 uppercase tracking-widest border-t border-slate-900 pt-8">
            <span className="flex items-center gap-1.5"><ShieldCheck className="w-3 h-3" /> Zero-Trust PII</span>
            <span className="flex items-center gap-1.5"><ListTodo className="w-3 h-3" /> Offline First</span>
            <span className="flex items-center gap-1.5"><Settings className="w-3 h-3" /> Local v3.0.0</span>
         </div>
      </footer>
    </div>
  );
}
