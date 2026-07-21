import React from "react";
import { X, FileText, Upload } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  resumeText: string;
  onTextChange: (text: string) => void;
}

export default function ResumeDrawer({ isOpen, onClose, resumeText, onTextChange }: Props) {
  return (
    <div className={`fixed inset-y-0 right-0 w-full md:w-96 bg-slate-900 border-l border-slate-800 shadow-2xl z-50 transform transition-transform duration-300 ${isOpen ? "translate-x-0" : "translate-x-full"}`}>
      <div className="h-full flex flex-col p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            <h2 className="font-bold text-slate-100 tracking-tight">Global Resume Storage</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-slate-800 rounded-md transition-colors">
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        <div className="flex-1 flex flex-col space-y-4 overflow-hidden">
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-500 uppercase">Resume Content (Markdown/Text)</label>
            <textarea
              value={resumeText}
              onChange={(e) => onTextChange(e.target.value)}
              placeholder="Paste your resume here... It will be shared across all tabs."
              className="w-full flex-1 min-h-[300px] bg-slate-950 border border-slate-800 rounded-lg p-4 text-sm text-slate-300 focus:outline-none focus:border-indigo-500 transition-all font-mono"
            />
          </div>

          <div className="bg-indigo-600/10 border border-indigo-500/20 rounded-lg p-4">
             <div className="flex items-center gap-3">
               <Upload className="w-5 h-5 text-indigo-400" />
               <div className="text-xs">
                 <p className="text-slate-200 font-bold">Fast Upload</p>
                 <p className="text-slate-400">PDFs are processed locally to remove PII before AI analysis.</p>
               </div>
             </div>
          </div>
        </div>

        <button onClick={onClose} className="w-full bg-slate-800 hover:bg-slate-750 text-slate-100 py-2 rounded-lg text-sm font-bold transition-all">
          Save & Close
        </button>
      </div>
    </div>
  );
}
