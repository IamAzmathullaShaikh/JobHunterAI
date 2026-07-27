import React, { useState, useEffect, useCallback } from "react";
import {
  FileText, Sparkles, Loader2, Save, Trash2, Copy,
  ChevronRight, Layout, Edit3, Eye, Plus, Send,
  Briefcase, Building2, Wand2
} from "lucide-react";
import { Resume, JobListing, CoverLetter, CoverLetterContent, CandidateProfile } from "../types.ts";
import debounce from "lodash/debounce";

interface Props {
  resumes: Resume[];
  jobs: JobListing[];
  profile: CandidateProfile | null;
}

export default function CoverLetterBuilder({ resumes, jobs, profile }: Props) {
  const [coverLetters, setCoverLetters] = useState<CoverLetter[]>([]);
  const [activeCL, setActiveCL] = useState<CoverLetter | null>(null);
  const [viewMode, setViewMode] = useState<"edit" | "preview">("edit");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const [comparisonModal, setComparisonModal] = useState<{ sectionId: string, original: string, optimized: string } | null>(null);

  // Form states for generation
  const [selectedResumeId, setSelectedResumeId] = useState<number | "">("");
  const [selectedJobId, setSelectedJobId] = useState<number | "">("");
  const [customJD, setCustomJD] = useState("");
  const [style, setStyle] = useState("Professional");

  useEffect(() => {
    async function loadCLs() {
      try {
        const res = await fetch("/api/cover-letter");
        const data = await res.json();
        setCoverLetters(data);
        if (data.length > 0) setActiveCL(data[0]);
      } catch (err) { console.error(err); }
    }
    loadCLs();
  }, []);

  const debouncedSave = useCallback(
    debounce(async (cl: CoverLetter) => {
      setIsSaving(true);
      try {
        await fetch(`/api/cover-letter/${cl.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: cl.name,
            content: cl.content,
            writing_style: cl.writing_style
          })
        });
      } catch (err) { console.error(err); }
      finally { setIsSaving(false); }
    }, 2000),
    []
  );

  const handleUpdate = (updates: Partial<CoverLetter>) => {
    if (!activeCL) return;
    const newCL = { ...activeCL, ...updates };
    setActiveCL(newCL);
    setCoverLetters(prev => prev.map(c => c.id === newCL.id ? newCL : c));
    debouncedSave(newCL);
  };

  const handleContentUpdate = (updates: Partial<CoverLetterContent>) => {
    if (!activeCL) return;
    handleUpdate({ content: { ...activeCL.content, ...updates } });
  };

  const regenerateSection = async (sectionId: string) => {
    if (!activeCL || !activeCL.resume_id) return;
    setIsGenerating(true);
    try {
      const jd = customJD || jobs.find(j => j.id === selectedJobId)?.description_raw || "";
      const original = (activeCL.content as any)[sectionId];
      const response = await fetch("/api/cover-letter/regenerate-section", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          section_id: sectionId,
          current_content: original,
          resume_id: activeCL.resume_id,
          job_description: jd,
          writing_style: activeCL.writing_style
        })
      });
      const result = await response.json();
      if (result.success) {
        setComparisonModal({
          sectionId,
          original,
          optimized: result.data
        });
      }
    } catch (err) { console.error(err); }
    finally { setIsGenerating(false); }
  };

  const applySectionImprovement = () => {
    if (!comparisonModal) return;
    handleContentUpdate({ [comparisonModal.sectionId]: comparisonModal.optimized });
    setComparisonModal(null);
  };

  const generateNewCL = async () => {
    if (!selectedResumeId) return;
    setIsGenerating(true);
    try {
      const jd = customJD || jobs.find(j => j.id === selectedJobId)?.description_raw || "";
      const company = jobs.find(j => j.id === selectedJobId)?.company_name || "Target Company";

      const response = await fetch("/api/cover-letter/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_id: selectedResumeId,
          job_description: jd,
          company_name: company,
          writing_style: style
        })
      });
      const result = await response.json();

      if (result.success) {
        // Create in DB
        const createRes = await fetch("/api/cover-letter", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: `Letter for ${company}`,
            content: {
              ...result.data,
              header: {
                name: profile?.full_name || "",
                email: profile?.email || "",
                phone: profile?.phone || "",
                location: profile?.location || ""
              }
            },
            resume_id: selectedResumeId,
            writing_style: style
          })
        });
        const newCL = await createRes.json();
        if (newCL && newCL.id) {
            setCoverLetters(prev => [newCL, ...prev]);
            setActiveCL(newCL);
            setViewMode("edit");
        }
      }
    } catch (err) { console.error(err); }
    finally { setIsGenerating(false); }
  };

  const exportCL = async (format: "pdf" | "html" | "markdown") => {
    if (!activeCL) return;
    setIsExporting(true);
    try {
      const response = await fetch("/api/cover-letter/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          format,
          content: activeCL.content,
          template_id: activeCL.template_id || "cover_letter_standard"
        })
      });
      const data = await response.json();
      if (data.success) {
        if (format === "pdf") window.open(data.download_url, "_blank");
        else {
           const blob = new Blob([data.data], { type: 'text/plain' });
           const url = window.URL.createObjectURL(blob);
           const a = document.createElement('a');
           a.href = url;
           a.download = `cover_letter.${format === 'markdown' ? 'md' : 'html'}`;
           a.click();
        }
      }
    } catch (err) { console.error(err); }
    finally { setIsExporting(false); }
  };

  return (
    <div className="space-y-6 animate-fade-in relative">
      {/* Comparison Modal */}
      {comparisonModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-6">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 max-w-4xl w-full shadow-2xl animate-in zoom-in-95">
            <h2 className="text-xl font-black text-white uppercase italic mb-6">Section Optimization</h2>
            <div className="grid grid-cols-2 gap-8 mb-8">
              <div className="space-y-3">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Original</label>
                <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs text-slate-400 leading-relaxed italic h-[300px] overflow-y-auto">{comparisonModal.original}</div>
              </div>
              <div className="space-y-3">
                <label className="text-[10px] font-bold text-indigo-400 uppercase">AI Optimized</label>
                <div className="bg-slate-950 border border-indigo-500/30 rounded-2xl p-4 text-xs text-slate-100 leading-relaxed font-medium h-[300px] overflow-y-auto">{comparisonModal.optimized}</div>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <button onClick={() => setComparisonModal(null)} className="px-6 py-2.5 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-800 transition-all uppercase">Discard</button>
              <button onClick={applySectionImprovement} className="px-6 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-500 transition-all uppercase shadow-lg shadow-indigo-600/20">Apply Change</button>
            </div>
          </div>
        </div>
      )}

      {isGenerating && (
        <div className="fixed top-8 right-8 z-[110] bg-indigo-600 text-white px-4 py-3 rounded-2xl shadow-2xl flex items-center gap-3 animate-slide-in">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="text-xs font-bold uppercase tracking-widest">AI Context Engine active...</span>
        </div>
      )}

      <div className="flex flex-col xl:flex-row gap-6">

        {/* Sidebar: Library & Styles */}
        <div className="xl:w-80 space-y-6 shrink-0">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              Your Letters
            </h3>
            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1 no-scrollbar">
              {coverLetters.map(cl => (
                <button
                  key={cl.id}
                  onClick={() => setActiveCL(cl)}
                  className={`w-full text-left p-3 rounded-xl border transition-all text-xs font-bold ${activeCL?.id === cl.id ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-950/50 border-slate-800 text-slate-400 hover:border-slate-700'}`}
                >
                  {cl.name}
                </button>
              ))}
              <button
                onClick={() => setActiveCL(null)}
                className="w-full p-3 rounded-xl border-2 border-dashed border-slate-800 text-slate-500 hover:text-indigo-400 hover:border-indigo-500/50 transition-all text-xs font-bold flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" /> New Letter
              </button>
            </div>
          </div>

          {activeCL && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
               <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Writing Style</h3>
               <select
                 value={activeCL.writing_style}
                 onChange={e => handleUpdate({ writing_style: e.target.value })}
                 className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none focus:border-indigo-500"
               >
                 {["Professional", "Technical", "Executive", "Startup", "Corporate", "Creative", "Friendly"].map(s => (
                   <option key={s} value={s}>{s}</option>
                 ))}
               </select>
            </div>
          )}

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
             <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Export</h3>
             <div className="grid grid-cols-2 gap-3">
                <button onClick={() => exportCL("pdf")} disabled={isExporting || !activeCL} className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all text-[10px]">
                   <FileText className="w-4 h-4 text-rose-400" /> PDF
                </button>
                <button onClick={() => exportCL("html")} disabled={isExporting || !activeCL} className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all text-[10px]">
                   <Layout className="w-4 h-4 text-blue-400" /> HTML
                </button>
                <button onClick={() => exportCL("markdown")} disabled={isExporting || !activeCL} className="col-span-2 bg-slate-800 hover:bg-slate-700 text-white font-bold py-2 rounded-2xl flex items-center justify-center gap-2 transition-all text-[10px]">
                   <FileText className="w-3.5 h-3.5 text-emerald-400" /> Download Markdown
                </button>
             </div>
          </div>
        </div>

        {/* Main Workspace */}
        <div className="flex-1 bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden flex flex-col min-h-[800px]">
           {activeCL ? (
             <>
               <div className="bg-slate-950/50 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
                  <div className="flex bg-slate-900 rounded-xl p-1">
                     <button onClick={() => setViewMode("edit")} className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${viewMode === "edit" ? "bg-slate-800 text-white shadow" : "text-slate-500 hover:text-slate-300"}`}><Edit3 className="w-3.5 h-3.5" /> Edit</button>
                     <button onClick={() => setViewMode("preview")} className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${viewMode === "preview" ? "bg-slate-800 text-white shadow" : "text-slate-500 hover:text-slate-300"}`}><Eye className="w-3.5 h-3.5" /> Preview</button>
                  </div>
                  <div className="flex items-center gap-2 text-[10px] font-black text-slate-600 uppercase tracking-widest">
                    {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Save className="w-3.5 h-3.5" />}
                    {isSaving ? "Saving..." : "Auto-Save Active"}
                  </div>
               </div>

               <div className="flex-1 overflow-y-auto p-8 bg-slate-950/30">
                  {viewMode === "edit" ? (
                    <div className="max-w-3xl mx-auto space-y-8">
                       <Section label="Salutation" value={activeCL.content.salutation} onChange={v => handleContentUpdate({ salutation: v })} />
                       <Section label="Opening Paragraph" value={activeCL.content.opening} onChange={v => handleContentUpdate({ opening: v })} multiline onRegenerate={() => regenerateSection('opening')} />
                       <Section label="Why this company?" value={activeCL.content.why_us} onChange={v => handleContentUpdate({ why_us: v })} multiline onRegenerate={() => regenerateSection('why_us')} />
                       <Section label="Relevant Experience" value={activeCL.content.experience_highlight} onChange={v => handleContentUpdate({ experience_highlight: v })} multiline onRegenerate={() => regenerateSection('experience_highlight')} />
                       <Section label="Closing Statement" value={activeCL.content.closing} onChange={v => handleContentUpdate({ closing: v })} multiline onRegenerate={() => regenerateSection('closing')} />
                       <Section label="Sign-off" value={activeCL.content.sign_off} onChange={v => handleContentUpdate({ sign_off: v })} />
                    </div>
                  ) : (
                    <CLPreview content={activeCL.content} />
                  )}
               </div>
             </>
           ) : (
             <div className="h-full flex flex-col items-center justify-center p-12 text-center space-y-8">
                <div className="space-y-4">
                  <FileText className="w-16 h-16 text-indigo-500 mx-auto opacity-20" />
                  <h2 className="text-2xl font-black text-white uppercase italic">Hyper-Tailored Cover Letters</h2>
                  <p className="text-slate-400 text-sm max-w-md mx-auto">Generate a professional cover letter grounded in your resume and specifically tailored to a target job description.</p>
                </div>

                <div className="w-full max-w-xl bg-slate-950/50 border border-slate-800 rounded-3xl p-8 space-y-6">
                   <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1 text-left">
                        <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Select Resume Context</label>
                        <select
                          value={selectedResumeId}
                          onChange={e => setSelectedResumeId(Number(e.target.value))}
                          className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none"
                        >
                          <option value="">Choose a resume...</option>
                          {resumes.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                        </select>
                      </div>
                      <div className="space-y-1 text-left">
                        <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Select Tracked Job</label>
                        <select
                          value={selectedJobId}
                          onChange={e => setSelectedJobId(Number(e.target.value))}
                          className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none"
                        >
                          <option value="">Optional: Use job from board...</option>
                          {jobs.map(j => <option key={j.id} value={j.id}>{j.title} at {j.company_name}</option>)}
                        </select>
                      </div>
                   </div>

                   <div className="space-y-1 text-left">
                      <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Or Paste Job Description</label>
                      <textarea
                        value={customJD}
                        onChange={e => setCustomJD(e.target.value)}
                        placeholder="Paste the target JD here..."
                        className="w-full h-32 bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs text-slate-300 outline-none focus:border-indigo-500"
                      />
                   </div>

                   <button
                     onClick={generateNewCL}
                     disabled={isGenerating || !selectedResumeId || (!selectedJobId && !customJD)}
                     className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-black py-4 rounded-2xl flex items-center justify-center gap-3 shadow-lg shadow-indigo-600/20 transition-all uppercase tracking-widest text-sm"
                   >
                     {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Wand2 className="w-5 h-5" />}
                     {isGenerating ? "Analyzing Context..." : "Generate Production Draft"}
                   </button>
                </div>
             </div>
           )}
        </div>
      </div>
    </div>
  );
}

function Section({ label, value, onChange, multiline, onRegenerate }: { label: string, value: string, onChange: (v: string) => void, multiline?: boolean, onRegenerate?: () => void }) {
  return (
    <div className="space-y-2 group">
      <div className="flex items-center justify-between px-1">
        <label className="text-[10px] font-bold text-slate-500 uppercase">{label}</label>
        {onRegenerate && (
          <button
            onClick={onRegenerate}
            className="opacity-0 group-hover:opacity-100 text-indigo-400 hover:text-indigo-300 transition-all flex items-center gap-1 text-[9px] font-black uppercase"
          >
            <Wand2 className="w-3 h-3" /> Regenerate
          </button>
        )}
      </div>
      {multiline ? (
        <textarea
          value={value}
          onChange={e => onChange(e.target.value)}
          className="w-full h-32 bg-slate-900 border border-slate-800 rounded-2xl p-4 text-sm text-slate-300 outline-none focus:border-indigo-500 resize-none"
        />
      ) : (
        <input
          value={value}
          onChange={e => onChange(e.target.value)}
          className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm text-white outline-none focus:border-indigo-500"
        />
      )}
    </div>
  );
}

function CLPreview({ content }: { content: CoverLetterContent }) {
  const [html, setHtml] = useState("");

  useEffect(() => {
    async function fetchPreview() {
      try {
        const response = await fetch("/api/cover-letter/export", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            format: "html",
            content,
            template_id: "cover_letter_standard"
          })
        });
        const data = await response.json();
        setHtml(data.data);
      } catch (err) { console.error(err); }
    }
    fetchPreview();
  }, [content]);

  return (
    <div className="bg-slate-800 p-8 h-full min-h-[1000px] flex justify-center overflow-auto">
       <div className="bg-white shadow-2xl w-[210mm] min-h-[297mm]">
          <iframe title="cl-preview" srcDoc={html} className="w-full h-full border-none" style={{ minHeight: "297mm" }} />
       </div>
    </div>
  );
}
