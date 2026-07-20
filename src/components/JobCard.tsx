import React, { useState } from 'react';
import { ExternalLink, MapPin, Briefcase, Building, AlertCircle } from 'lucide-react';
import { JobListing } from '../types'; // assuming types exist from earlier context

interface JobCardProps {
  job: JobListing;
}

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const [checking, setChecking] = useState(false);
  
  // Requirement: use job.canonical_url fallback to job.raw_url
  const linkToOpen = job.canonical_url || job.raw_url || job.url;
  
  console.log('RENDER_JOB', job);
  
  const handleOpenJob = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (!linkToOpen || linkToOpen === '#' || linkToOpen.includes('mock')) {
       window.open(`https://www.google.com/search?q=${encodeURIComponent(job.title + " " + job.company_name + " jobs")}`, '_blank');
       return;
    }
    
    setChecking(true);
    try {
      // Best-effort HEAD check
      const res = await fetch(linkToOpen, { method: 'HEAD', mode: 'no-cors' });
      // If it doesn't throw, we assume it's reachable or we are blocked by CORS (opaque response). 
      // Opaque response is fine, we just open it.
      window.open(linkToOpen, '_blank');
    } catch (err) {
      console.warn('Job link check failed, opening fallback search', err);
      // Fallback to search
      window.open(`https://www.google.com/search?q=${encodeURIComponent(job.title + " " + job.company_name + " jobs")}`, '_blank');
    } finally {
      setChecking(false);
    }
  };

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
        <button 
          onClick={handleOpenJob}
          disabled={checking}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-accent hover:text-white transition-colors"
          aria-label={`Open job: ${job.title}`}
        >
          {checking ? 'Checking...' : 'Open Job'}
          <ExternalLink className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
