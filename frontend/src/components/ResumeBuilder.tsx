import React, { useState, useEffect, useCallback } from "react";
import {
  Layout, FileText, Download, Edit3, Eye, Plus, Trash2,
  Settings2, Copy, Save, Loader2, ChevronDown, ChevronUp,
  Mail, Phone, MapPin, Globe, Linkedin, Github, Briefcase,
  GraduationCap, FolderKanban, Award, Languages
} from "lucide-react";
import { CandidateProfile, Resume, ResumeContent, WorkHistoryItem, EducationItem, ProjectItem } from "../types.ts";
import debounce from "lodash/debounce";

interface ResumeBuilderProps {
  profile: CandidateProfile | null;
}

const DEFAULT_CONTENT: ResumeContent = {
  header: { name: "", title: "", email: "", phone: "", location: "" },
  summary: "",
  work_history: [],
  education: [],
  skills: [],
  projects: [],
  certifications: [],
  languages: [],
  interests: [],
  references: []
};

const moveItem = <T,>(list: T[], index: number, direction: 'up' | 'down'): T[] => {
  const newList = [...list];
  const targetIndex = direction === 'up' ? index - 1 : index + 1;
  if (targetIndex < 0 || targetIndex >= list.length) return list;
  [newList[index], newList[targetIndex]] = [newList[targetIndex], newList[index]];
  return newList;
};

export default function ResumeBuilder({ profile }: ResumeBuilderProps) {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [activeResume, setActiveResume] = useState<Resume | null>(null);
  const [viewMode, setViewMode] = useState<"edit" | "preview">("edit");
  const [isExporting, setIsExporting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [zoom, setZoom] = useState(1);

  const [config, setConfig] = useState({
    accent_color: "#4f46e5",
    font_family: "'Inter', sans-serif",
    font_size: "13px",
    line_height: "1.5",
    margin: "40px"
  });

  const [isTailoring, setIsTailoring] = useState(false);
  const [tailorComparison, setTailorComparison] = useState<{ original: string, optimized: string, index: number, itemIndex: number } | null>(null);

  // Fetch all resumes on mount
  useEffect(() => {
    async function loadResumes() {
      try {
        const response = await fetch("/api/resumes");
        const data = await response.json();
        // Filter out archived unless we are in a special view
        setResumes(data);
        if (data.length > 0) setActiveResume(data[0]);
      } catch (err) {
        console.error("Failed to load resumes:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadResumes();
  }, []);

  // Auto-save logic
  const debouncedSave = useCallback(
    debounce(async (resume: Resume, config: any) => {
      setIsSaving(true);
      try {
        await fetch(`/api/resumes/${resume.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: resume.name,
            template_id: resume.template_id,
            content: resume.content,
            // config is currently UI-only, but could be persisted to DB Resume model if needed
          })
        });
        setLastSaved(new Date());
      } catch (err) {
        console.error("Failed to auto-save:", err);
      } finally {
        setIsSaving(false);
      }
    }, 2000),
    []
  );

  const updateActiveResume = (updates: Partial<Resume>) => {
    if (!activeResume) return;
    const newResume = { ...activeResume, ...updates };
    setActiveResume(newResume);
    setResumes(prev => prev.map(r => r.id === newResume.id ? newResume : r));
    debouncedSave(newResume, config);
  };

  const updateContent = (updates: Partial<ResumeContent>) => {
    if (!activeResume) return;
    updateActiveResume({ content: { ...activeResume.content, ...updates } });
  };

  const createNewResume = async () => {
    const name = `Resume ${resumes.length + 1}`;
    // Seed with profile if available
    const content = profile ? {
      ...DEFAULT_CONTENT,
      header: { ...DEFAULT_CONTENT.header, name: profile.full_name, title: profile.recommended_search_queries[0] || "" },
      skills: profile.key_skills,
      work_history: profile.experience_highlights.map(h => ({
          company: "Company", title: profile.recommended_search_queries[0] || "Role",
          location: "Remote", start_date: "2020", end_date: "Present",
          bullets: [h]
      }))
    } : DEFAULT_CONTENT;

    try {
      const response = await fetch("/api/resumes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, content })
      });
      const data = await response.json();
      setResumes(prev => [data, ...prev]);
      setActiveResume(data);
    } catch (err) {
      console.error("Failed to create resume:", err);
    }
  };

  const duplicateResume = async (id: number) => {
    try {
      const response = await fetch(`/api/resumes/${id}/duplicate`, { method: "POST" });
      const data = await response.json();
      setResumes(prev => [data, ...prev]);
      setActiveResume(data);
    } catch (err) {
      console.error("Failed to duplicate:", err);
    }
  };

  const archiveResume = async (id: number) => {
    try {
      await fetch(`/api/resumes/${id}/archive`, { method: "PUT" });
      setResumes(prev => prev.map(r => r.id === id ? { ...r, is_archived: true } : r));
      if (activeResume?.id === id) setActiveResume(null);
    } catch (err) { console.error(err); }
  };

  const restoreResume = async (id: number) => {
    try {
      await fetch(`/api/resumes/${id}/restore`, { method: "PUT" });
      setResumes(prev => prev.map(r => r.id === id ? { ...r, is_archived: false } : r));
    } catch (err) { console.error(err); }
  };

  const handleTailorBullet = async (original: string, itemIdx: number, bulletIdx: number) => {
    setIsTailoring(true);
    try {
      const response = await fetch("/api/ats/optimize-bullet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bullet: original,
          jd: "Target Job Description Context" // Should ideally be passed in or selected from active job
        })
      });
      const data = await response.json();
      if (data.success && data.data.length > 0) {
        setTailorComparison({
          original,
          optimized: data.data[0],
          index: bulletIdx,
          itemIndex: itemIdx
        });
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsTailoring(false);
    }
  };

  const applyOptimization = () => {
    if (!tailorComparison || !activeResume) return;
    const { itemIndex, index, optimized } = tailorComparison;
    const newWorkHistory = [...activeResume.content.work_history];
    newWorkHistory[itemIndex].bullets[index] = optimized;
    updateContent({ work_history: newWorkHistory });
    setTailorComparison(null);
  };

  const exportResume = async (format: "pdf" | "docx" | "markdown") => {
    if (!activeResume) return;
    setIsExporting(true);
    try {
      const response = await fetch(`/api/resumes/export?resume_id=${activeResume.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ format, template_id: activeResume.template_id, config })
      });
      const data = await response.json();
      if (data.success) {
         if (format === "docx") {
            window.open(data.download_url, "_blank");
         } else if (format === "pdf") {
            window.open(data.download_url, "_blank");
         } else {
            // Handle raw data for markdown/html
            const blob = new Blob([data.data], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `resume.${format === 'markdown' ? 'md' : 'html'}`;
            a.click();
         }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-[600px] flex flex-col items-center justify-center space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Loading Resume Vault...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in relative">
      {/* Comparison Modal */}
      {tailorComparison && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-6">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 max-w-4xl w-full shadow-2xl animate-in zoom-in-95">
            <h2 className="text-xl font-black text-white uppercase italic mb-6">AI Bullet Optimization</h2>
            <div className="grid grid-cols-2 gap-8 mb-8">
              <div className="space-y-3">
                <label className="text-[10px] font-bold text-slate-500 uppercase">Original</label>
                <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs text-slate-400 leading-relaxed italic">{tailorComparison.original}</div>
              </div>
              <div className="space-y-3">
                <label className="text-[10px] font-bold text-indigo-400 uppercase">AI Optimized</label>
                <div className="bg-slate-950 border border-indigo-500/30 rounded-2xl p-4 text-xs text-slate-100 leading-relaxed font-medium">{tailorComparison.optimized}</div>
              </div>
            </div>
            <div className="flex justify-end gap-3">
              <button onClick={() => setTailorComparison(null)} className="px-6 py-2.5 rounded-xl text-xs font-bold text-slate-400 hover:bg-slate-800 transition-all uppercase">Discard</button>
              <button onClick={applyOptimization} className="px-6 py-2.5 rounded-xl text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-500 transition-all uppercase shadow-lg shadow-indigo-600/20">Apply Improvement</button>
            </div>
          </div>
        </div>
      )}

      {isTailoring && (
        <div className="fixed top-8 right-8 z-[110] bg-indigo-600 text-white px-4 py-3 rounded-2xl shadow-2xl flex items-center gap-3 animate-slide-in">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="text-xs font-bold uppercase tracking-widest">Tailoring with Llama 3.3...</span>
        </div>
      )}

      <div className="flex flex-col xl:flex-row gap-6">

        {/* Sidebar: Resume List & Templates */}
        <div className="xl:w-80 space-y-6 shrink-0">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <FileText className="w-4 h-4 text-indigo-400" />
                Your Resumes
              </h3>
              <button onClick={createNewResume} className="p-1.5 bg-indigo-600 rounded-lg text-white hover:bg-indigo-500 transition-colors">
                <Plus className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1 no-scrollbar">
              {resumes.filter(r => !r.is_archived).map(r => (
                <div key={r.id} className="group relative">
                  <button
                    onClick={() => setActiveResume(r)}
                    className={`w-full text-left p-3 rounded-xl border transition-all text-xs font-bold ${activeResume?.id === r.id ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-950/50 border-slate-800 text-slate-400 hover:border-slate-700'}`}
                  >
                    {r.name}
                  </button>
                  <div className="absolute right-2 top-2 hidden group-hover:flex items-center gap-1">
                    <button onClick={() => duplicateResume(r.id)} className="p-1 bg-slate-800 rounded hover:text-indigo-400" title="Duplicate"><Copy className="w-3 h-3" /></button>
                    <button onClick={() => archiveResume(r.id)} className="p-1 bg-slate-800 rounded hover:text-amber-400" title="Archive"><FolderKanban className="w-3 h-3" /></button>
                  </div>
                </div>
              ))}
              {resumes.length === 0 && (
                <p className="text-[10px] text-slate-600 italic text-center py-4">No resumes found. Create your first one!</p>
              )}
            </div>

            {resumes.some(r => r.is_archived) && (
              <div className="mt-4 pt-4 border-t border-slate-800">
                <h4 className="text-[9px] font-black text-slate-600 uppercase mb-2">Archived</h4>
                <div className="space-y-1 opacity-50">
                  {resumes.filter(r => r.is_archived).map(r => (
                    <div key={r.id} className="flex items-center justify-between p-2 bg-slate-950 rounded-lg border border-slate-900">
                      <span className="text-[10px] font-bold text-slate-500">{r.name}</span>
                      <button onClick={() => restoreResume(r.id)} className="text-indigo-400 hover:text-indigo-300 text-[9px] font-black uppercase">Restore</button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Layout className="w-4 h-4 text-indigo-400" />
              Templates
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: "classic_ats", name: "Classic" },
                { id: "modern_minimal", name: "Modern" },
                { id: "executive_elegant", name: "Executive" },
                { id: "tech_clean", name: "Tech" },
                { id: "compact", name: "Compact" },
                { id: "two_column", name: "2-Col" }
              ].map(tpl => (
                <button
                  key={tpl.id}
                  onClick={() => updateActiveResume({ template_id: tpl.id })}
                  className={`p-3 rounded-xl border text-[10px] font-black uppercase transition-all ${activeResume?.template_id === tpl.id ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-950/50 border-slate-800 text-slate-500 hover:border-slate-700'}`}
                >
                  {tpl.name}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
             <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
               <Settings2 className="w-4 h-4 text-indigo-400" />
               Customization
             </h3>
             <div className="space-y-4">
                <div className="space-y-1">
                   <label className="text-[9px] font-black text-slate-600 uppercase">Accent Color</label>
                   <div className="flex gap-2">
                      {["#4f46e5", "#0891b2", "#059669", "#dc2626", "#d97706"].map(c => (
                        <button key={c} onClick={() => setConfig(prev => ({ ...prev, accent_color: c }))} className={`w-6 h-6 rounded-full border-2 ${config.accent_color === c ? 'border-white' : 'border-transparent'}`} style={{ backgroundColor: c }} />
                      ))}
                   </div>
                </div>
                <div className="space-y-1">
                   <label className="text-[9px] font-black text-slate-600 uppercase">Font Size</label>
                   <div className="grid grid-cols-3 gap-2">
                      {["11px", "13px", "15px"].map(s => (
                        <button key={s} onClick={() => setConfig(prev => ({ ...prev, font_size: s }))} className={`py-1 rounded border text-[10px] ${config.font_size === s ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-950 border-slate-800 text-slate-500'}`}>{s}</button>
                      ))}
                   </div>
                </div>
                <div className="space-y-1">
                   <label className="text-[9px] font-black text-slate-600 uppercase">Line Spacing</label>
                   <select value={config.line_height} onChange={e => setConfig(prev => ({ ...prev, line_height: e.target.value }))} className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-[10px] text-white outline-none">
                      <option value="1.2">Compact (1.2)</option>
                      <option value="1.5">Normal (1.5)</option>
                      <option value="1.8">Relaxed (1.8)</option>
                   </select>
                </div>
                <div className="space-y-1">
                   <label className="text-[9px] font-black text-slate-600 uppercase">Page Margin</label>
                   <input type="range" min="10" max="80" step="5" value={parseInt(config.margin)} onChange={e => setConfig(prev => ({ ...prev, margin: `${e.target.value}px` }))} className="w-full accent-indigo-500" />
                </div>
             </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
             <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Export</h3>
             <div className="grid grid-cols-2 gap-3">
                <button onClick={() => exportResume("pdf")} disabled={isExporting || !activeResume} className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all text-[10px]">
                   <FileText className="w-4 h-4 text-rose-400" /> PDF
                </button>
                <button onClick={() => exportResume("docx")} disabled={isExporting || !activeResume} className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex flex-col items-center justify-center gap-1 transition-all text-[10px]">
                   <Download className="w-4 h-4 text-blue-400" /> DOCX
                </button>
                <button onClick={() => exportResume("markdown")} disabled={isExporting || !activeResume} className="col-span-2 bg-slate-800 hover:bg-slate-700 text-white font-bold py-2 rounded-2xl flex items-center justify-center gap-2 transition-all text-[10px]">
                   <FileText className="w-3.5 h-3.5 text-emerald-400" /> Download Markdown
                </button>
             </div>
          </div>
        </div>

        {/* Main Editor / Preview */}
        <div className="flex-1 bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden flex flex-col min-h-[800px]">
           <div className="bg-slate-950/50 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
              <div className="flex bg-slate-900 rounded-xl p-1">
                 <button onClick={() => setViewMode("edit")} className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${viewMode === "edit" ? "bg-slate-800 text-white shadow" : "text-slate-500 hover:text-slate-300"}`}><Edit3 className="w-3.5 h-3.5" /> Edit</button>
                 <button onClick={() => setViewMode("preview")} className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${viewMode === "preview" ? "bg-slate-800 text-white shadow" : "text-slate-500 hover:text-slate-300"}`}><Eye className="w-3.5 h-3.5" /> Preview</button>
              </div>

              {viewMode === "preview" && (
                <div className="flex items-center gap-2 bg-slate-900 rounded-lg p-1">
                   <button onClick={() => setZoom(Math.max(0.5, zoom - 0.1))} className="p-1 hover:text-white text-slate-500 text-xs">-</button>
                   <span className="text-[10px] font-bold text-slate-400 w-8 text-center">{Math.round(zoom * 100)}%</span>
                   <button onClick={() => setZoom(Math.min(1.5, zoom + 0.1))} className="p-1 hover:text-white text-slate-500 text-xs">+</button>
                </div>
              )}

              <div className="flex items-center gap-4">
                {isSaving && <div className="flex items-center gap-2 text-[10px] font-black text-indigo-400 uppercase tracking-widest"><Loader2 className="w-3 h-3 animate-spin" /> Saving...</div>}
                {!isSaving && lastSaved && <div className="flex items-center gap-2 text-[10px] font-black text-slate-600 uppercase tracking-widest"><Save className="w-3.5 h-3.5" /> Saved {lastSaved.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>}
                {!isSaving && !lastSaved && activeResume && <div className="flex items-center gap-2 text-[10px] font-black text-slate-600 uppercase tracking-widest"><Settings2 className="w-3.5 h-3.5" /> Auto-Save Active</div>}
              </div>
           </div>

           <div className="flex-1 overflow-y-auto bg-slate-950/30">
              {activeResume ? (
                viewMode === "edit" ? (
                  <ResumeEditor content={activeResume.content} onUpdate={updateContent} onTailor={handleTailorBullet} />
                ) : (
                  <ResumePreview content={activeResume.content} templateId={activeResume.template_id} config={config} zoom={zoom} />
                )
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center p-12 opacity-30 space-y-4">
                  <Layout className="w-16 h-16" />
                  <h2 className="text-xl font-black uppercase italic">No Resume Selected</h2>
                  <p className="text-xs font-bold max-w-xs uppercase">Create a new resume from the sidebar to begin crafting your professional identity.</p>
                </div>
              )}
           </div>
        </div>
      </div>
    </div>
  );
}

function ResumeEditor({ content, onUpdate, onTailor }: { content: ResumeContent, onUpdate: (u: Partial<ResumeContent>) => void, onTailor: (original: string, itemIdx: number, bulletIdx: number) => void }) {
  const [expandedSection, setExpandedSection] = useState<string | null>("header");

  const toggle = (s: string) => setExpandedSection(expandedSection === s ? null : s);

  return (
    <div className="max-w-4xl mx-auto p-8 space-y-6">
      {/* Header Section */}
      <CollapsibleSection title="Master Identity" icon={Mail} isOpen={expandedSection === "header"} onToggle={() => toggle("header")}>
        <div className="grid grid-cols-2 gap-4">
          <Input label="Full Name" value={content.header.name} onChange={v => onUpdate({ header: { ...content.header, name: v } })} />
          <Input label="Professional Title" value={content.header.title} onChange={v => onUpdate({ header: { ...content.header, title: v } })} />
          <Input label="Email" value={content.header.email} onChange={v => onUpdate({ header: { ...content.header, email: v } })} />
          <Input label="Phone" value={content.header.phone} onChange={v => onUpdate({ header: { ...content.header, phone: v } })} />
          <Input label="Location" value={content.header.location} onChange={v => onUpdate({ header: { ...content.header, location: v } })} />
          <Input label="LinkedIn" value={content.header.linkedin || ""} onChange={v => onUpdate({ header: { ...content.header, linkedin: v } })} />
        </div>
      </CollapsibleSection>

      {/* Summary */}
      <CollapsibleSection title="Professional Summary" icon={Edit3} isOpen={expandedSection === "summary"} onToggle={() => toggle("summary")}>
        <textarea
          value={content.summary}
          onChange={e => onUpdate({ summary: e.target.value })}
          className="w-full bg-slate-900 border border-slate-800 rounded-xl p-4 text-sm text-slate-300 min-h-[120px] outline-none focus:border-indigo-500"
          placeholder="Write a brief overview of your professional background..."
        />
      </CollapsibleSection>

      {/* Experience */}
      <CollapsibleSection title="Work History" icon={Briefcase} isOpen={expandedSection === "work"} onToggle={() => toggle("work")}>
        <div className="space-y-4">
          {content.work_history.map((item, i) => (
            <div key={i} className="p-4 bg-slate-900/50 rounded-2xl border border-slate-800 space-y-4 relative group">
              <div className="absolute top-4 right-4 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all">
                <button onClick={() => onUpdate({ work_history: moveItem(content.work_history, i, 'up') })} className="p-1 hover:text-indigo-400"><ChevronUp className="w-3.5 h-3.5" /></button>
                <button onClick={() => onUpdate({ work_history: moveItem(content.work_history, i, 'down') })} className="p-1 hover:text-indigo-400"><ChevronDown className="w-3.5 h-3.5" /></button>
                <button
                  onClick={() => onUpdate({ work_history: content.work_history.filter((_, idx) => idx !== i) })}
                  className="p-1 text-rose-500 hover:text-rose-400"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Input label="Company" value={item.company} onChange={v => {
                  const newList = [...content.work_history];
                  newList[i] = { ...item, company: v };
                  onUpdate({ work_history: newList });
                }} />
                <Input label="Role" value={item.title} onChange={v => {
                  const newList = [...content.work_history];
                  newList[i] = { ...item, title: v };
                  onUpdate({ work_history: newList });
                }} />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Key Contributions</label>
                {item.bullets.map((b, bi) => (
                  <div key={bi} className="flex items-center gap-2 group/bullet">
                    <input
                      value={b}
                      onChange={e => {
                        const newList = [...content.work_history];
                        newList[i].bullets[bi] = e.target.value;
                        onUpdate({ work_history: newList });
                      }}
                      className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 outline-none focus:border-indigo-500"
                    />
                    <button onClick={() => onTailor(b, i, bi)} className="p-1.5 bg-slate-800 rounded-lg text-indigo-400 opacity-0 group-hover/bullet:opacity-100 transition-all hover:bg-indigo-600 hover:text-white" title="Optimize with AI"><Plus className="w-3 h-3 rotate-45" /></button>
                    <button onClick={() => {
                      const newList = [...content.work_history];
                      newList[i].bullets = newList[i].bullets.filter((_, idx) => idx !== bi);
                      onUpdate({ work_history: newList });
                    }} className="p-1 text-slate-600 hover:text-rose-400"><Trash2 className="w-3 h-3" /></button>
                  </div>
                ))}
                <button
                  onClick={() => {
                    const newList = [...content.work_history];
                    newList[i].bullets.push("");
                    onUpdate({ work_history: newList });
                  }}
                  className="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 mt-2"
                >
                  <Plus className="w-3 h-3" /> Add Contribution
                </button>
              </div>
            </div>
          ))}
          <button
            onClick={() => onUpdate({ work_history: [...content.work_history, { company: "", title: "", location: "", start_date: "", end_date: "", bullets: [] }] })}
            className="w-full py-3 border-2 border-dashed border-slate-800 rounded-2xl text-slate-500 hover:text-indigo-400 hover:border-indigo-400/50 transition-all flex items-center justify-center gap-2 font-bold text-xs"
          >
            <Plus className="w-4 h-4" /> Add Experience Item
          </button>
        </div>
      </CollapsibleSection>

      {/* Projects */}
      <CollapsibleSection title="Projects" icon={FolderKanban} isOpen={expandedSection === "projects"} onToggle={() => toggle("projects")}>
        <div className="space-y-4">
          {content.projects.map((item, i) => (
            <div key={i} className="p-4 bg-slate-900/50 rounded-2xl border border-slate-800 space-y-4 relative group">
              <div className="absolute top-4 right-4 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all">
                <button
                  onClick={() => onUpdate({ projects: content.projects.filter((_, idx) => idx !== i) })}
                  className="p-1 text-rose-500 hover:text-rose-400"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Input label="Project Name" value={item.name} onChange={v => {
                  const newList = [...content.projects];
                  newList[i] = { ...item, name: v };
                  onUpdate({ projects: newList });
                }} />
                <Input label="Role/Context" value={item.role} onChange={v => {
                  const newList = [...content.projects];
                  newList[i] = { ...item, role: v };
                  onUpdate({ projects: newList });
                }} />
              </div>
            </div>
          ))}
          <button
            onClick={() => onUpdate({ projects: [...content.projects, { name: "", role: "", date: "", bullets: [] }] })}
            className="w-full py-3 border-2 border-dashed border-slate-800 rounded-2xl text-slate-500 hover:text-indigo-400 transition-all flex items-center justify-center gap-2 font-bold text-xs"
          >
            <Plus className="w-4 h-4" /> Add Project
          </button>
        </div>
      </CollapsibleSection>

      {/* Education */}
      <CollapsibleSection title="Education" icon={GraduationCap} isOpen={expandedSection === "edu"} onToggle={() => toggle("edu")}>
        <div className="space-y-4">
          {content.education.map((item, i) => (
            <div key={i} className="p-4 bg-slate-900/50 rounded-2xl border border-slate-800 space-y-4 relative group">
              <div className="absolute top-4 right-4 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all">
                <button
                  onClick={() => onUpdate({ education: content.education.filter((_, idx) => idx !== i) })}
                  className="p-1 text-rose-500 hover:text-rose-400"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Input label="Institution" value={item.school} onChange={v => {
                  const newList = [...content.education];
                  newList[i] = { ...item, school: v };
                  onUpdate({ education: newList });
                }} />
                <Input label="Degree" value={item.degree} onChange={v => {
                  const newList = [...content.education];
                  newList[i] = { ...item, degree: v };
                  onUpdate({ education: newList });
                }} />
              </div>
            </div>
          ))}
          <button
            onClick={() => onUpdate({ education: [...content.education, { school: "", degree: "", location: "", date: "" }] })}
            className="w-full py-3 border-2 border-dashed border-slate-800 rounded-2xl text-slate-500 hover:text-indigo-400 transition-all flex items-center justify-center gap-2 font-bold text-xs"
          >
            <Plus className="w-4 h-4" /> Add Education
          </button>
        </div>
      </CollapsibleSection>

      {/* Certifications & Awards */}
      <CollapsibleSection title="Certifications & Awards" icon={Award} isOpen={expandedSection === "awards"} onToggle={() => toggle("awards")}>
        <div className="space-y-4">
          {content.certifications.map((item, i) => (
            <div key={i} className="flex items-center gap-2">
                <Input label="Title" value={item.name} onChange={v => {
                  const newList = [...content.certifications];
                  newList[i] = { ...item, name: v };
                  onUpdate({ certifications: newList });
                }} />
                <button onClick={() => onUpdate({ certifications: content.certifications.filter((_, idx) => idx !== i) })} className="mt-5 p-2 text-rose-500"><Trash2 className="w-4 h-4" /></button>
            </div>
          ))}
          <button onClick={() => onUpdate({ certifications: [...content.certifications, { name: "", issuer: "", date: "" }] })} className="text-[10px] font-bold text-indigo-400">+ Add Certification</button>
        </div>
      </CollapsibleSection>

      {/* Languages */}
      <CollapsibleSection title="Languages" icon={Languages} isOpen={expandedSection === "languages"} onToggle={() => toggle("languages")}>
         <div className="grid grid-cols-3 gap-3">
            {content.languages.map((item, i) => (
              <div key={i} className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex justify-between items-center">
                 <div className="text-xs font-bold text-white">{item.name} <span className="text-[10px] text-slate-500 font-normal">({item.level})</span></div>
                 <button onClick={() => onUpdate({ languages: content.languages.filter((_, idx) => idx !== i) })} className="text-rose-500"><Trash2 className="w-3 h-3" /></button>
              </div>
            ))}
            <button onClick={() => onUpdate({ languages: [...content.languages, { name: "English", level: "Native" }] })} className="p-3 border-2 border-dashed border-slate-800 rounded-xl text-slate-600 hover:text-indigo-400">+</button>
         </div>
      </CollapsibleSection>

      {/* Skills */}
      <CollapsibleSection title="Skills & Competencies" icon={Settings2} isOpen={expandedSection === "skills"} onToggle={() => toggle("skills")}>
         <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {content.skills.map((s, i) => (
                <span key={i} className="bg-slate-800 text-indigo-300 px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-2 border border-slate-700">
                  {s}
                  <button onClick={() => onUpdate({ skills: content.skills.filter((_, idx) => idx !== i) })}><XIcon /></button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
               <input
                 onKeyDown={e => {
                   if (e.key === 'Enter') {
                     const val = (e.target as HTMLInputElement).value;
                     if (val) {
                       onUpdate({ skills: [...content.skills, val] });
                       (e.target as HTMLInputElement).value = "";
                     }
                   }
                 }}
                 className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white outline-none focus:border-indigo-500"
                 placeholder="Add skill (press Enter)..."
               />
            </div>
         </div>
      </CollapsibleSection>
    </div>
  );
}

function ResumePreview({ content, templateId, config, zoom }: { content: ResumeContent, templateId: string, config: any, zoom: number }) {
  const [html, setHtml] = useState("");

  useEffect(() => {
    async function fetchPreview() {
      try {
        const response = await fetch("/api/resumes/export", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ format: "html", template_id: templateId, content, config }) // Passing content directly for instant preview
        });
        const data = await response.json();
        setHtml(data.data);
      } catch (err) {
        console.error(err);
      }
    }
    fetchPreview();
  }, [content, templateId, config]);

  return (
    <div className="bg-slate-800 p-8 h-full min-h-[1000px] flex justify-center overflow-auto">
       <div
         className="bg-white shadow-2xl origin-top transition-transform duration-200"
         style={{
           width: "210mm",
           minHeight: "297mm",
           transform: `scale(${zoom})`,
           marginBottom: `calc(297mm * ${zoom - 1})`
         }}
       >
          <iframe title="preview" srcDoc={html} className="w-full h-full border-none" style={{ minHeight: "297mm" }} />
       </div>
    </div>
  );
}

// Helpers

function CollapsibleSection({ title, icon: Icon, children, isOpen, onToggle }: any) {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden transition-all">
      <button onClick={onToggle} className="w-full flex items-center justify-between px-6 py-4 hover:bg-slate-800/50 transition-colors">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-slate-950 rounded-xl text-indigo-400 border border-slate-800"><Icon className="w-4 h-4" /></div>
          <span className="text-xs font-black text-white uppercase tracking-widest">{title}</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-slate-600" /> : <ChevronDown className="w-4 h-4 text-slate-600" />}
      </button>
      {isOpen && <div className="px-6 pb-6 pt-2 border-t border-slate-800/50 animate-fade-in">{children}</div>}
    </div>
  );
}

function Input({ label, value, onChange, placeholder }: { label: string, value: string, onChange: (v: string) => void, placeholder?: string }) {
  return (
    <div className="space-y-1">
      <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">{label}</label>
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white focus:border-indigo-500 outline-none transition-all"
      />
    </div>
  );
}

function XIcon() {
  return (
    <svg className="w-3 h-3 text-slate-500 hover:text-rose-400 cursor-pointer" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}
