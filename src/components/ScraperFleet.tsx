import React, { useState, useEffect } from "react";
import { Terminal, Shield, Play, Loader2, Database, AlertCircle } from "lucide-react";
import { CandidateProfile, JobListing } from "../types.ts";

interface ScraperFleetProps {
  profile: CandidateProfile | null;
  onJobsDiscovered: (jobs: JobListing[]) => void;
  resumeText: string;
}

export default function ScraperFleet({
  profile,
  onJobsDiscovered,
  resumeText,
}: ScraperFleetProps) {
  const [searchQuery, setSearchQuery] = useState("Territory Sales Executive");
  const [location, setLocation] = useState("Andhra Pradesh, India");
  const [jobType, setJobType] = useState("Full-Time");
  const [isRunning, setIsRunning] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Set default search query when candidate profile is uploaded
  useEffect(() => {
    if (profile && profile.recommended_search_queries?.length > 0) {
      setSearchQuery(profile.recommended_search_queries[0]);
    }
  }, [profile]);

  const runIngestionPipeline = async () => {
    if (!searchQuery.trim() || !location.trim()) {
      setError("Please fill in both target search keyword and target location.");
      return;
    }

    setIsRunning(true);
    setError(null);
    setLogs([]);

    const addLog = (msg: string, delay: number) => {
      return new Promise<void>((resolve) => {
        setTimeout(() => {
          setLogs((prev) => [...prev, msg]);
          resolve();
        }, delay);
      });
    };

    try {
      await addLog("⚡ Starting job search engines...", 100);
      await addLog("📡 Connecting to job boards...", 400);
      await addLog("🕷️ LinkedIn: searching for jobs...", 500);
      await addLog("🕷️ Indeed & Glassdoor: extracting job info...", 400);
      await addLog("🕷️ Naukri & Foundit: collecting matches...", 400);
      await addLog("🕷️ YC Jobs & Internshala: looking for tech/internships...", 400);
      await addLog("📦 Cleaning up duplicate jobs...", 350);

      // Construct candidate context
      let candidate_context = resumeText;
      if (profile) {
        candidate_context = `Candidate: ${profile.full_name}
Skills: ${profile.key_skills.join(", ")}
Education: ${profile.education.join(", ")}
Experience: ${profile.total_experience_years} years
Highlights: ${profile.experience_highlights.join("; ")}`;
      }

      // Hit API
      const response = await fetch("/api/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          search_query: searchQuery,
          location,
          job_type: jobType,
          candidate_context,
        }),
      });

      if (!response.ok) {
        throw new Error("Scrape execution pipeline failed.");
      }

      const data = await response.json();

      await addLog("🤖 Analyzing jobs with AI...", 500);
      await addLog("⚖️ Checking how well you match...", 400);
      await addLog(`✅ Search complete.`, 300);
      await addLog(`📊 Discovered ${data.scraped_count} matching jobs.`, 200);
      await addLog(`🆕 Appended ${data.new_count} new jobs to your list.`, 100);

      onJobsDiscovered(data.jobs);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "An error occurred during the search.");
      setLogs((prev) => [...prev, "❌ Job search stopped due to an error."]);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Search parameters panel */}
      <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/80 shadow-md">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2 mb-1">
          <Database className="w-5 h-5 text-indigo-400" />
          🎛️ Choose keywords and location
        </h3>
        <p className="text-xs text-slate-400 mb-5">
          Step 2: Tell us what kind of job and where you want to work.
        </p>

        {error && (
          <div className="bg-rose-500/15 border border-rose-500/30 text-rose-300 rounded-lg p-3 text-sm mb-4 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">
              Job Title or Keyword
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg py-2 px-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="e.g. Sales Executive, Software Engineer"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">
              Location
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg py-2 px-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="e.g. Andhra Pradesh, India or Remote"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">
              Job Type
            </label>
            <select
              value={jobType}
              onChange={(e) => setJobType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700/80 rounded-lg py-2 px-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="Full-Time">Full-Time</option>
              <option value="Internship">Internship</option>
              <option value="Apprenticeship">Apprenticeship</option>
            </select>
          </div>
        </div>
      </div>

      {/* Fleet Telemetry panel */}
      <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/80 shadow-md flex flex-col justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2 mb-1">
            <Terminal className="w-5 h-5 text-indigo-400" />
            🖥️ Search across 9 job boards at once
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Step 3: We will search LinkedIn, Indeed, Naukri, Glassdoor, and more to find the best jobs.
          </p>

          <div className="bg-slate-950 rounded-lg p-4 border border-slate-800 font-mono text-xs text-indigo-300 min-h-[140px] max-h-[180px] overflow-y-auto space-y-1">
            {logs.length === 0 ? (
              <span className="text-slate-500">Ready to search. Click the button below when you are ready.</span>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="leading-relaxed">
                  {log}
                </div>
              ))
            )}
            {isRunning && (
              <div className="flex items-center gap-2 text-indigo-400 mt-2 italic animate-pulse">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                Processing data...
              </div>
            )}
          </div>
        </div>

        <div className="mt-4">
          <button
            onClick={runIngestionPipeline}
            disabled={isRunning}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-slate-100 font-medium text-sm py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-md cursor-pointer"
          >
            {isRunning ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Searching for jobs...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Find Jobs Now
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
