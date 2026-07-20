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
} from "lucide-react";
import { CandidateProfile, JobListing, ApplicationStatus } from "./types.ts";
import ResumeIngestion from "./components/ResumeIngestion.tsx";
import ScraperFleet from "./components/ScraperFleet.tsx";
import JobsTable from "./components/JobsTable.tsx";
import AnalysisMatrix from "./components/AnalysisMatrix.tsx";
import KanbanBoard from "./components/KanbanBoard.tsx";
import ContactFinder from "./components/ContactFinder.tsx";

export default function App() {
  const [activeTab, setActiveTab] = useState<"cockpit" | "jobs" | "ai" | "kanban">("cockpit");
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [jobs, setJobs] = useState<JobListing[]>([]);
  const [resumeText, setResumeText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [excelFilter, setExcelFilter] = useState("All");
  const [isPurging, setIsPurging] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Fetch initial profile and jobs
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const pRes = await fetch("/api/profile");
        const pData = await pRes.json();
        if (pData.profile) {
          setProfile(pData.profile);
        }

        const jRes = await fetch("/api/jobs");
        const jData = await jRes.json();
        setJobs(jData.jobs || []);
      } catch (err) {
        console.error("Error loading application states:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  const handleProfileParsed = (newProfile: CandidateProfile) => {
    setProfile(newProfile);
    showToast("Candidate Profile Successfully Mapped!");
  };

  const handleJobsDiscovered = (updatedJobs: JobListing[]) => {
    setJobs(updatedJobs);
    showToast("Scraper Pipeline run complete! Database updated.");
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
        // Update local jobs list
        setJobs((prev) =>
          prev.map((j) => (j.id === jobId ? { ...j, application: resData.job.application } : j))
        );
        showToast("Role moved into tracked pipeline board!");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateApplicationCard = async (
    appId: number,
    status: ApplicationStatus,
    notes: string
  ) => {
    try {
      const response = await fetch(`/api/applications/${appId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status, notes }),
      });
      if (response.ok) {
        const resData = await response.json();
        // Update local jobs list
        setJobs((prev) =>
          prev.map((j) => (j.id === resData.job.id ? { ...j, application: resData.job.application } : j))
        );
        showToast("Application tracking status updated.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const purgeDatabase = async () => {
    setIsPurging(true);
    try {
      const response = await fetch("/api/jobs/purge", { method: "POST" });
      if (response.ok) {
        const data = await response.json();
        setJobs(data.jobs);
        showToast(`Cleaned database! Purged ${data.purged_count} duplicate listings.`);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsPurging(false);
    }
  };

  const downloadExcel = () => {
    window.open(`/api/export?status_filter=${encodeURIComponent(excelFilter)}`, "_blank");
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Filter tracked roles for cockpit summary board
  const trackedRoles = jobs.filter((j) => j.application);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed top-5 right-5 z-50 bg-slate-800 border-l-4 border-emerald-400 text-slate-100 px-4 py-3 rounded-lg shadow-xl flex items-center gap-2.5 max-w-sm animate-fade-in font-sans text-sm">
          <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Header Panel */}
      <header className="bg-slate-950 border-b border-slate-800/80 px-6 py-4 sticky top-0 z-30 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl">⚡</span>
              <h1 className="text-lg font-bold text-slate-100 tracking-tight">
                JobHunterAI Dashboard
              </h1>
            </div>
            <p className="text-xs text-slate-400 mt-0.5 font-medium">
              Your personal AI job search assistant
            </p>
          </div>

          {/* Nav Tabs */}
          <nav className="flex bg-slate-900 rounded-lg p-1 text-xs font-semibold select-none border border-slate-800/60 self-start md:self-center">
            <button
              onClick={() => setActiveTab("cockpit")}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md transition-all cursor-pointer ${
                activeTab === "cockpit"
                  ? "bg-indigo-600 text-slate-100 shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              ⚡ Dashboard
            </button>
            <button
              onClick={() => setActiveTab("jobs")}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md transition-all cursor-pointer ${
                activeTab === "jobs"
                  ? "bg-indigo-600 text-slate-100 shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Briefcase className="w-3.5 h-3.5" />
              Discovered Jobs
              {jobs.length > 0 && (
                <span className="bg-slate-850 text-indigo-300 border border-indigo-500/10 text-[10px] px-1 rounded-sm">
                  {jobs.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab("ai")}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md transition-all cursor-pointer ${
                activeTab === "ai"
                  ? "bg-indigo-600 text-slate-100 shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Brain className="w-3.5 h-3.5" />
              AI Matrix
            </button>
            <button
              onClick={() => setActiveTab("kanban")}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-md transition-all cursor-pointer ${
                activeTab === "kanban"
                  ? "bg-indigo-600 text-slate-100 shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <ClipboardList className="w-3.5 h-3.5" />
              Kanban Tracker
              {trackedRoles.length > 0 && (
                <span className="bg-slate-850 text-emerald-400 border border-emerald-500/10 text-[10px] px-1 rounded-sm">
                  {trackedRoles.length}
                </span>
              )}
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-8">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center text-center py-24 space-y-3">
            <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-sm text-slate-400 font-medium">Loading your job search dashboard...</p>
          </div>
        ) : (
          <>
            {activeTab === "cockpit" && (
              <div className="space-y-8 animate-fade-in">
                {/* Row 1: Resume Parser + Fleet configurations */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                  <ResumeIngestion
                    profile={profile}
                    onProfileParsed={handleProfileParsed}
                    resumeText={resumeText}
                    setResumeText={setResumeText}
                  />
                  <ScraperFleet
                    profile={profile}
                    onJobsDiscovered={handleJobsDiscovered}
                    resumeText={resumeText}
                  />
                </div>

                {/* Row 2: Recruiter Contact Finder */}
                <ContactFinder defaultSearchQuery={profile?.recommended_search_queries?.[0] || ""} />

                {/* Row 3: Maintenance / Status tracker */}
                <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/80 shadow-md">
                  <div className="flex items-center justify-between border-b border-slate-700/80 pb-4 mb-5">
                    <div>
                      <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                        <ClipboardList className="w-5 h-5 text-indigo-400" />
                        📊 Track your applications in one place
                      </h3>
                      <p className="text-xs text-slate-400">
                        Step 5: Review tracked jobs, clean up records, and download Excel reports (Step 6).
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
                    {/* Database maintenance & exports */}
                    <div className="space-y-6">
                      <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800/80 space-y-4">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          ⚙️ Controls & Exports
                        </h4>
                        <div>
                          <label className="text-xs text-slate-400 block mb-1">
                            Filter Listings by Status
                          </label>
                          <select
                            value={excelFilter}
                            onChange={(e) => setExcelFilter(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-700 rounded py-1.5 px-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                          >
                            <option value="All">All</option>
                            <option value="Identified">Identified</option>
                            <option value="AI Ready">AI Ready</option>
                            <option value="Applied">Applied</option>
                            <option value="Interviewing">Interviewing</option>
                            <option value="Offer">Offer</option>
                            <option value="Rejected">Rejected</option>
                          </select>
                        </div>

                        <button
                          onClick={downloadExcel}
                          className="w-full bg-indigo-600 hover:bg-indigo-500 text-slate-100 font-bold text-xs py-2 px-3 rounded flex items-center justify-center gap-1.5 transition-colors cursor-pointer shadow"
                        >
                          <Download className="w-4.5 h-4.5" />
                          Download Excel report
                        </button>
                      </div>

                      <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800/80 space-y-3">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                          🧹 Cleanup
                        </h4>
                        <button
                          onClick={purgeDatabase}
                          disabled={isPurging}
                          className="w-full bg-slate-800 hover:bg-slate-750 text-slate-300 font-bold text-xs py-2 px-3 rounded flex items-center justify-center gap-1.5 transition-colors cursor-pointer border border-slate-700"
                        >
                          <Trash2 className="w-4.5 h-4.5 text-rose-400" />
                          🧼 Clean up duplicates
                        </button>
                      </div>
                    </div>

                    {/* Active compatibility tracks display */}
                    <div className="lg:col-span-2 bg-slate-900/40 rounded-xl p-4 border border-slate-800/80 min-h-[220px]">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
                        📋 Tracked Jobs & Match Scores
                      </h4>

                      {trackedRoles.length === 0 ? (
                        <div className="text-center py-12 text-slate-500 text-xs">
                          <HelpCircle className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                          No jobs tracked yet. Go to 'Discovered Jobs' to add some.
                        </div>
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="w-full text-left text-xs border-collapse">
                            <thead>
                              <tr className="text-slate-500 border-b border-slate-850 pb-2">
                                <th className="pb-2 font-bold uppercase">Job / Company</th>
                                <th className="pb-2 font-bold uppercase">Status</th>
                                <th className="pb-2 font-bold uppercase text-right">Fit Score</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-850">
                              {trackedRoles.map((j) => (
                                <tr key={j.id} className="hover:bg-slate-900/10">
                                  <td className="py-2.5 pr-2">
                                    <div className="font-semibold text-slate-200">{j.title}</div>
                                    <div className="text-[10px] text-slate-400 mt-0.5">{j.company_name}</div>
                                  </td>
                                  <td className="py-2.5">
                                    <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded font-bold font-sans">
                                      {j.application!.status}
                                    </span>
                                  </td>
                                  <td className="py-2.5 text-right font-mono font-bold text-emerald-400">
                                    {j.ai_analysis ? `${Math.round(j.ai_analysis.match_score)}%` : "N/A"}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "jobs" && (
              <div className="animate-fade-in">
                <JobsTable jobs={jobs} onTrackJob={handleTrackJob} />
              </div>
            )}

            {activeTab === "ai" && (
              <div className="animate-fade-in">
                <AnalysisMatrix
                  jobs={jobs}
                  resumeText={resumeText}
                  onAnalysisComplete={(updatedJobs) => setJobs(updatedJobs)}
                />
              </div>
            )}

            {activeTab === "kanban" && (
              <div className="animate-fade-in">
                <KanbanBoard
                  jobs={jobs}
                  onUpdateCard={handleUpdateApplicationCard}
                  onTrackJob={async (jobId) => {
                    await handleTrackJob(jobId);
                  }}
                />
              </div>
            )}
          </>
        )}
      </main>

      <footer className="bg-slate-950 border-t border-slate-900 py-6 px-6 mt-12 text-center text-xs text-slate-500">
        <p>© 2026 JobHunterAI. Fully Migrated to Server-Side TypeScript.</p>
      </footer>
    </div>
  );
}
