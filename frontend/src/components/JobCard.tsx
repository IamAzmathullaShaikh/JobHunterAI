import React from 'react';
import { ExternalLink, MapPin, Briefcase, Building } from 'lucide-react';
import { JobListing } from '../types';

interface JobCardProps {
  job: JobListing;
}

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const linkToOpen = job.canonical_url || job.url || job.raw_url || '';

  const matchScore = job.ai_analysis?.match_score ?? 0;
  let scoreColor = 'bg-slate-800 text-slate-300';
  if (matchScore >= 80) scoreColor = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  else if (matchScore >= 60) scoreColor = 'bg-amber-500/20 text-amber-400 border-amber-500/30';
  else if (matchScore > 0) scoreColor = 'bg-rose-500/20 text-rose-400 border-rose-500/30';

  return (
    <div className="bg-panel rounded-xl p-5 border border-slate-800 hover:border-slate-600 transition-colors shadow-soft flex flex-col gap-3 group">
      <div className="flex justify-between items-start gap-4">
        <div>
          <h3 className="text-base font-semibold text-white group-hover:text-primary transition-colors line-clamp-2">
            {job.title}
          </h3>
          <div className="flex items-center gap-2 text-sm text-slate-400 mt-1">
            <Building className="w-3.5 h-3.5" />
            <span className="font-medium">{job.company_name}</span>
          </div>
        </div>
        {matchScore > 0 && (
          <div className={`px-2 py-1 rounded border text-xs font-bold flex-shrink-0 ${scoreColor}`} aria-label={`Match score: ${matchScore}%`}>
            {matchScore}%
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2 text-xs text-muted mt-1">
        <span className="flex items-center gap-1 bg-surface px-2 py-1 rounded">
          <MapPin className="w-3 h-3" />
          {job.location} ({job.work_place_type})
        </span>
        <span className="flex items-center gap-1 bg-surface px-2 py-1 rounded">
          <Briefcase className="w-3 h-3" />
          {job.job_type}
        </span>
        <span className="flex items-center gap-1 bg-surface px-2 py-1 rounded">
          {job.source}
        </span>
      </div>

      <p className="text-sm text-slate-400 mt-2 line-clamp-3 leading-relaxed">
        {job.description_clean || job.description_raw}
      </p>

      <div className="mt-auto pt-4 flex items-center justify-between">
        <span className="text-xs text-slate-500 font-medium">
          {job.date_scraped ? new Date(job.date_scraped).toLocaleDateString() : 'Recent'}
        </span>
        {linkToOpen ? (
          <a
            href={linkToOpen}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-accent hover:text-white transition-colors"
            aria-label={`Open job: ${job.title}`}
          >
            Open Job
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        ) : (
          <button
            disabled
            title="Link unavailable"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 cursor-not-allowed"
            aria-label="Job link unavailable"
          >
            Link unavailable
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        )}
      </div>
    </div>
  );
};
