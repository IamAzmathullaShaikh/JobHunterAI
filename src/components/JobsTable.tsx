import React, { useState } from "react";
import { Search, ExternalLink, Bookmark, CheckCircle, Briefcase, MapPin, DollarSign } from "lucide-react";
import { JobListing } from "../types.ts";

interface JobsTableProps {
  jobs: JobListing[];
  onTrackJob: (jobId: number) => void;
}

export default function JobsTable({ jobs, onTrackJob }: JobsTableProps) {
  // Debug logging
  React.useEffect(() => {
    if (jobs.length > 0) {
      console.log("[JobsTable] Rendered jobs:", jobs.map(j => ({ id: j.id, url: j.url, title: j.title })));
    }
  }, [jobs]);
  const [searchTerm, setSearchTerm] = useState("");

  const filteredJobs = jobs.filter(
    (j) =>
      j.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      j.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      j.location.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-slate-800/60 rounded-xl border border-slate-700/80 shadow-md overflow-hidden">
      <div className="p-5 border-b border-slate-700/80 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-indigo-400" />
            🔍 Jobs Found
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            View and filter all the jobs we found for you.
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by title, company..."
            className="w-full bg-slate-900 border border-slate-700/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 placeholder-slate-500"
          />
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
        </div>
      </div>

      {filteredJobs.length === 0 ? (
        <div className="p-12 text-center text-slate-400">
          <Briefcase className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-300">No job listings found.</p>
          <p className="text-xs text-slate-500 mt-1">
            Go to the Dashboard to search for jobs.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/50 text-slate-400 text-xs font-semibold border-b border-slate-800">
                <th className="py-3 px-4">Role details</th>
                <th className="py-3 px-4">Source</th>
                <th className="py-3 px-4">Workplace</th>
                <th className="py-3 px-4">Compensation</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-sm">
              {filteredJobs.map((job) => (
                <tr key={job.id} className="hover:bg-slate-900/20 transition-colors">
                  <td className="py-3.5 px-4 max-w-[320px]">
                    <div className="font-semibold text-slate-200 truncate">{job.title}</div>
                    <div className="text-xs text-slate-400 font-medium truncate">
                      {job.company_name}
                    </div>
                    <div className="text-[11px] text-slate-500 flex items-center gap-1 mt-1 truncate">
                      <MapPin className="w-3 h-3 text-slate-600" />
                      {job.location}
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-xs font-mono">
                    <span className="bg-slate-900 text-indigo-300 px-2.5 py-0.5 rounded border border-slate-800">
                      {job.source}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-xs">
                    <div className="text-slate-300">{job.work_place_type || "Onsite"}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">{job.job_type}</div>
                  </td>
                  <td className="py-3.5 px-4 text-xs">
                    {job.salary_raw ? (
                      <div className="text-slate-300 flex items-center gap-0.5 font-medium">
                        <DollarSign className="w-3.5 h-3.5 text-emerald-500/80" />
                        {job.salary_raw}
                      </div>
                    ) : (
                      <span className="text-slate-500 text-[11px] italic">Not specified</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-2.5">
                      {(!job.url || job.url === '#' || job.url.trim() === '') ? (
                        <div className="flex flex-col items-end">
                          <span className="text-rose-400 text-[10px] leading-tight text-right max-w-[140px]">
                            This job may have expired. <a href={`https://www.google.com/search?q=${encodeURIComponent(job.title + " " + job.company_name + " jobs")}`} target="_blank" rel="noreferrer" className="underline hover:text-indigo-300 transition-colors">Click here to search again on {job.source}</a>.
                          </span>
                        </div>
                      ) : (
                        <a
                          href={job.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-slate-400 hover:text-slate-200 transition-colors inline-flex items-center gap-1 text-xs"
                        >
                          View Job
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {job.application ? (
                        <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-md text-xs font-semibold flex items-center gap-1">
                          <CheckCircle className="w-3.5 h-3.5" />
                          {job.application.status}
                        </span>
                      ) : (
                        <button
                          onClick={() => onTrackJob(job.id)}
                          className="bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold text-xs py-1 px-3 rounded-lg flex items-center gap-1 transition-all cursor-pointer"
                        >
                          <Bookmark className="w-3 h-3" />
                          Track
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
