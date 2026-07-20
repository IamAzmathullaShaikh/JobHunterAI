import React, { useState } from "react";
import { Upload, FileText, CheckCircle, Loader2, Sparkles } from "lucide-react";
import { CandidateProfile } from "../types.ts";

interface ResumeIngestionProps {
  profile: CandidateProfile | null;
  onProfileParsed: (profile: CandidateProfile) => void;
  resumeText: string;
  setResumeText: (text: string) => void;
}

export default function ResumeIngestion({
  profile,
  onProfileParsed,
  resumeText,
  setResumeText,
}: ResumeIngestionProps) {
  const [isParsing, setIsParsing] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadMode, setUploadMode] = useState<"upload" | "paste">("upload");
  const [error, setError] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const parseResumeData = async (payload: { text?: string; fileBase64?: string; fileType?: string; fileName?: string }) => {
    setIsParsing(true);
    setError(null);
    try {
      const response = await fetch("/api/profile/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || "Failed to parse resume.");
      }
      const data = await response.json();
      onProfileParsed(data.profile);
      if (payload.text) {
        setResumeText(payload.text);
      } else {
        setResumeText(`Candidate Name: ${data.profile.full_name}\nSkills: ${data.profile.key_skills.join(", ")}`);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Something went wrong during parsing.");
    } finally {
      setIsParsing(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      await handleFileSelection(file);
    }
  };

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      await handleFileSelection(file);
    }
  };

  const handleFileSelection = async (file: File) => {
    setError(null);
    if (file.type === "application/pdf") {
      const reader = new FileReader();
      reader.onload = async () => {
        const base64 = reader.result as string;
        await parseResumeData({ fileBase64: base64, fileType: file.type, fileName: file.name });
      };
      reader.onerror = () => setError("Error reading file.");
      reader.readAsDataURL(file);
    } else {
      // For txt or simple files, read text
      const reader = new FileReader();
      reader.onload = async () => {
        const text = reader.result as string;
        await parseResumeData({ text });
      };
      reader.onerror = () => setError("Error reading file.");
      reader.readAsText(file);
    }
  };

  const handlePasteSubmit = async () => {
    if (!resumeText.trim()) {
      setError("Please paste your resume text first.");
      return;
    }
    await parseResumeData({ text: resumeText });
  };

  return (
    <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/80 shadow-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            📄 Candidate Resume Ingestion
          </h3>
          <p className="text-xs text-slate-400">
            Parse profile metrics to automatically extract skill vectors.
          </p>
        </div>
        <div className="flex bg-slate-900 rounded-lg p-1 text-xs">
          <button
            onClick={() => setUploadMode("upload")}
            className={`px-3 py-1.5 rounded-md transition-all ${
              uploadMode === "upload"
                ? "bg-slate-700 text-slate-100 font-medium"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            File Upload
          </button>
          <button
            onClick={() => setUploadMode("paste")}
            className={`px-3 py-1.5 rounded-md transition-all ${
              uploadMode === "paste"
                ? "bg-slate-700 text-slate-100 font-medium"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Paste Text
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/15 border border-rose-500/30 text-rose-300 rounded-lg p-3 text-sm mb-4">
          ⚠️ {error}
        </div>
      )}

      {uploadMode === "upload" ? (
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center transition-colors cursor-pointer ${
            dragActive
              ? "border-indigo-400 bg-indigo-500/5"
              : "border-slate-700 hover:border-slate-600 bg-slate-900/40"
          }`}
        >
          <input
            id="resume-file-input"
            type="file"
            className="hidden"
            accept=".pdf,.txt,.docx"
            onChange={handleFileInput}
          />
          <label htmlFor="resume-file-input" className="flex flex-col items-center cursor-pointer">
            <div className="p-3 bg-slate-800 rounded-full mb-3 text-slate-400 group-hover:text-slate-300">
              {isParsing ? (
                <Loader2 className="w-8 h-8 animate-spin text-indigo-400" />
              ) : (
                <Upload className="w-8 h-8" />
              )}
            </div>
            <p className="text-sm font-medium text-slate-200 text-center">
              {isParsing ? "Analyzing skill vectors..." : "Drag & Drop or click to upload PDF/TXT"}
            </p>
            <p className="text-xs text-slate-400 mt-1">Supports PDF or plain text</p>
          </label>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          <textarea
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            rows={5}
            className="w-full bg-slate-900 border border-slate-700/80 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500/80 font-sans resize-none"
            placeholder="Paste raw resume text here..."
          />
          <button
            onClick={handlePasteSubmit}
            disabled={isParsing}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-slate-100 font-medium text-sm py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-sm cursor-pointer"
          >
            {isParsing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Parsing Candidate Resume...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Extract Profile Capabilities
              </>
            )}
          </button>
        </div>
      )}

      {profile && (
        <div className="mt-6 border-t border-slate-700/60 pt-5">
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-200 mb-3">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            👤 Active Candidate Profile
          </div>
          <div className="bg-slate-900/60 rounded-lg p-4 border border-slate-800 space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-y-2 gap-x-4">
              <div>
                <span className="text-xs text-slate-400 block">Candidate Name</span>
                <span className="font-medium text-slate-200">{profile.full_name}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Experience</span>
                <span className="font-medium text-slate-200">
                  ~{profile.total_experience_years} Years
                </span>
              </div>
              <div className="col-span-2">
                <span className="text-xs text-slate-400 block">Education</span>
                <span className="font-medium text-slate-200">
                  {profile.education?.join(", ") || "N/A"}
                </span>
              </div>
            </div>

            <div>
              <span className="text-xs text-slate-400 block mb-1">Identified Core Skills</span>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {profile.key_skills?.map((skill, i) => (
                  <span
                    key={i}
                    className="bg-slate-800 text-indigo-300 border border-indigo-500/20 px-2 py-0.5 rounded text-xs font-mono"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {profile.recommended_search_queries?.length > 0 && (
              <div>
                <span className="text-xs text-slate-400 block mb-1">Suggested Search Vectors</span>
                <div className="flex flex-wrap gap-1.5">
                  {profile.recommended_search_queries.map((q, i) => (
                    <code
                      key={i}
                      className="bg-slate-950 text-emerald-400 border border-emerald-500/10 px-2 py-1 rounded text-[11px] font-mono"
                    >
                      {q}
                    </code>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
