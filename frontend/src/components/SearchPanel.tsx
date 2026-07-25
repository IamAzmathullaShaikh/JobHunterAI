import React from 'react';
import { Search, MapPin, Briefcase } from 'lucide-react';

interface SearchFields {
  query: string;
  location: string;
  jobType: string;
}

interface SearchPanelProps {
  fields: SearchFields;
  onChange: (fields: SearchFields) => void;
  onSearch: () => void;
  suggestions?: string[];
}

export const SearchPanel: React.FC<SearchPanelProps> = ({ fields, onChange, onSearch, suggestions = [] }) => {
  return (
    <div className="bg-panel rounded-xl shadow-soft border border-slate-800 p-6">
      <h2 className="text-lg font-semibold mb-4 text-white">Find Jobs</h2>
      
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Job Title, Keywords, or Company"
            className="w-full bg-surface border border-slate-700 rounded-lg py-2 pl-9 pr-3 text-sm text-white placeholder-slate-500 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
            value={fields.query}
            onChange={(e) => onChange({ ...fields, query: e.target.value })}
            aria-label="Job search query"
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="relative">
            <MapPin className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
            <input
              type="text"
              placeholder="Location (e.g. Remote)"
              className="w-full bg-surface border border-slate-700 rounded-lg py-2 pl-9 pr-3 text-sm text-white placeholder-slate-500 focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-colors"
              value={fields.location}
              onChange={(e) => onChange({ ...fields, location: e.target.value })}
              aria-label="Location"
            />
          </div>
          <div className="relative">
            <Briefcase className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
            <select
              className="w-full bg-surface border border-slate-700 rounded-lg py-2 pl-9 pr-3 text-sm text-white focus:border-primary focus:ring-1 focus:ring-primary outline-none appearance-none transition-colors"
              value={fields.jobType}
              onChange={(e) => onChange({ ...fields, jobType: e.target.value })}
              aria-label="Job type"
            >
              <option value="Full-Time">Full-Time</option>
              <option value="Contract">Contract</option>
              <option value="Internship">Internship</option>
              <option value="Freelance">Freelance</option>
            </select>
          </div>
        </div>

        <button 
          onClick={onSearch}
          className="w-full bg-primary hover:bg-primary-dark text-white font-medium py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 mt-2 shadow-lg shadow-primary/20"
        >
          <Search className="w-4 h-4" />
          Search AI Network
        </button>
      </div>

      {suggestions.length > 0 && (
        <div className="mt-5 pt-4 border-t border-slate-800">
          <p className="text-xs text-slate-500 mb-2 font-medium">Suggested Searches</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => onChange({ ...fields, query: s })}
                className="bg-surface hover:bg-slate-800 border border-slate-700 text-slate-300 text-[11px] px-2.5 py-1 rounded-full transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
