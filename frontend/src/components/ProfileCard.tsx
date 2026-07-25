import React from 'react';
import { User, GraduationCap, Code, Edit2, Download } from 'lucide-react';
import { CandidateProfile } from '../types';

interface ProfileCardProps {
  profile: CandidateProfile;
  onEdit?: () => void;
  onReparse?: () => void;
  onExport?: () => void;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({ profile, onEdit, onReparse, onExport }) => {
  const getInitials = (name: string) => name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();

  return (
    <div className="bg-panel rounded-xl shadow-soft border border-slate-800 overflow-hidden">
      <div className="bg-gradient-to-r from-primary-dark to-primary h-16"></div>
      <div className="px-6 pb-6 relative">
        <div className="flex justify-between items-end -mt-8 mb-4">
          <div className="w-16 h-16 rounded-xl bg-surface border-4 border-panel flex items-center justify-center text-xl font-bold text-white shadow-lg">
            {profile.full_name ? getInitials(profile.full_name) : <User className="text-muted" />}
          </div>
          <div className="flex gap-2">
            <button onClick={onEdit} className="p-1.5 text-slate-400 hover:text-white bg-surface rounded-md transition-colors" aria-label="Edit Profile">
              <Edit2 className="w-4 h-4" />
            </button>
            <button onClick={onExport} className="p-1.5 text-slate-400 hover:text-white bg-surface rounded-md transition-colors" aria-label="Export Profile">
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <h2 className="text-xl font-bold text-white tracking-tight">{profile.full_name || 'Anonymous User'}</h2>
        <p className="text-sm text-accent font-medium mt-1">{profile.total_experience_years} Years Experience</p>

        <div className="mt-6 space-y-4">
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <GraduationCap className="w-3.5 h-3.5" /> Education
            </h3>
            <ul className="text-sm text-slate-300 space-y-1">
              {profile.education?.map((ed, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="w-1 h-1 bg-primary rounded-full mt-2 flex-shrink-0"></span>
                  <span className="leading-tight">{ed}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <Code className="w-3.5 h-3.5" /> Key Skills
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {profile.key_skills?.slice(0, 10).map((skill, i) => (
                <span key={i} className="bg-surface text-slate-300 text-[11px] px-2 py-1 rounded-md border border-slate-700/50">
                  {skill}
                </span>
              ))}
              {profile.key_skills?.length > 10 && (
                <span className="bg-surface text-slate-500 text-[11px] px-2 py-1 rounded-md border border-slate-700/50">
                  +{profile.key_skills.length - 10}
                </span>
              )}
            </div>
          </div>
        </div>
        
        {onReparse && (
          <button 
            onClick={onReparse}
            className="w-full mt-6 py-2 bg-surface hover:bg-slate-800 text-xs text-slate-300 font-medium rounded-lg transition-colors border border-slate-700"
          >
            Re-parse Resume
          </button>
        )}
      </div>
    </div>
  );
};
