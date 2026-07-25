import React, { useState } from 'react';
import { UploadCloud, FileText } from 'lucide-react';

export interface UploadCardProps {
  onFileUpload: (file: File) => void;
  onPasteText: (text: string) => void;
}

export const UploadCard: React.FC<UploadCardProps> = ({ onFileUpload, onPasteText }) => {
  const [dragActive, setDragActive] = useState(false);
  const [textMode, setTextMode] = useState(false);
  const [text, setText] = useState('');

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileUpload(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="bg-panel rounded-xl shadow-soft p-6 border border-slate-800">
      <h2 className="text-lg font-semibold mb-4 text-white">Upload Resume</h2>
      
      {!textMode ? (
        <div 
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
            dragActive ? 'border-primary bg-primary/10' : 'border-slate-700 hover:border-slate-500'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-upload')?.click()}
          role="button"
          tabIndex={0}
          aria-label="Upload resume file"
        >
          <input 
            id="file-upload" 
            type="file" 
            className="hidden" 
            accept=".pdf,.doc,.docx"
            onChange={(e) => {
              if (e.target.files?.[0]) onFileUpload(e.target.files[0]);
            }}
          />
          <UploadCloud className="w-10 h-10 mx-auto text-muted mb-3" />
          <p className="text-sm text-slate-300">Drag & drop your resume here, or click to browse</p>
          <p className="text-xs text-muted mt-2">Supports PDF, DOCX</p>
          
          <div className="mt-6 pt-4 border-t border-slate-800">
            <button 
              onClick={(e) => { e.stopPropagation(); setTextMode(true); }}
              className="text-xs text-primary hover:text-primary-dark font-medium transition-colors"
            >
              Paste text instead
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          <textarea
            className="w-full bg-surface border border-slate-700 rounded-lg p-3 text-sm min-h-[120px] focus:border-primary focus:ring-1 focus:ring-primary outline-none"
            placeholder="Paste your resume text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            aria-label="Paste resume text"
          />
          <div className="flex justify-between items-center">
            <button 
              onClick={() => setTextMode(false)}
              className="text-xs text-muted hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button 
              onClick={() => onPasteText(text)}
              className="bg-primary hover:bg-primary-dark text-white text-xs font-medium py-1.5 px-4 rounded-md transition-colors"
            >
              Process Text
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
