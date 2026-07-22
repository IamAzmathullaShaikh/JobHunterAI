import React from "react";
import ScraperFleet from "./ScraperFleet.tsx";
import JobsTable from "./JobsTable.tsx";
import { JobListing, CandidateProfile } from "../types.ts";
import { Briefcase, Search } from "lucide-react";

interface Props {
  profile: CandidateProfile | null;
  jobs: JobListing[];
  onJobsDiscovered: (updatedJobs: JobListing[]) => void;
  onTrackJob: (jobId: number) => void;
  resumeText: string;
}

export default function JobDiscovery({ profile, jobs, onJobsDiscovered, onTrackJob, resumeText }: Props) {
  return (
    <div className="space-y-8 animate-fade-in">
      {/* Step-by-Step Guidance */}
      <div className="bg-indigo-600/10 border border-indigo-500/20 rounded-2xl p-4 flex items-center gap-4">
        <div className="bg-indigo-600 p-2 rounded-lg">
           <Search className="w-5 h-5 text-white" />
        </div>
        <div>
           <p className="text-sm font-bold text-white tracking-tight">Live Job Discovery Engine</p>
           <p className="text-xs text-slate-400">Search across 9+ platforms simultaneously using either your active resume context or specific designations.</p>
        </div>
      </div>

      <ScraperFleet
        profile={profile}
        onJobsDiscovered={onJobsDiscovered}
        resumeText={resumeText}
      />

      <div className="space-y-4">
        <div className="flex items-center gap-3 px-1">
          <Briefcase className="w-5 h-5 text-indigo-400" />
          <h2 className="text-lg font-black text-white uppercase tracking-tighter">Real-Time Listings</h2>
        </div>
        <JobsTable jobs={jobs} onTrackJob={onTrackJob} />
      </div>
    </div>
  );
}
