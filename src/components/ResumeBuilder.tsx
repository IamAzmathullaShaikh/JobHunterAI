import React, { useState } from "react";
import { Layout, FileText, Download, Edit3, Eye, Plus, Trash2, Settings2 } from "lucide-react";

export default function ResumeBuilder() {
  const [activeTemplate, setActiveTab] = useState("classic_ats");
  const [viewMode, setViewMode] = useState<"edit" | "preview">("edit");

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col xl:flex-row gap-6">
        {/* Sidebar: Template Selection */}
        <div className="xl:w-80 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <Layout className="w-4 h-4 text-indigo-400" />
              Templates
            </h3>
            <div className="space-y-3">
              {[
                { id: "classic_ats", name: "Classic ATS", desc: "Maximum parseability" },
                { id: "modern_minimal", name: "Modern Minimal", desc: "Clean & breathable" },
                { id: "executive_elegant", name: "Executive Elegant", desc: "High-impact layout" },
                { id: "tech_clean", name: "Tech Clean", desc: "Skill-density optimized" }
              ].map(tpl => (
                <button
                  key={tpl.id}
                  onClick={() => setActiveTab(tpl.id)}
                  className={`w-full text-left p-4 rounded-2xl border transition-all ${activeTemplate === tpl.id ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg' : 'bg-slate-950/50 border-slate-800 text-slate-400 hover:border-slate-700'}`}
                >
                  <div className="font-bold text-sm">{tpl.name}</div>
                  <div className={`text-[10px] ${activeTemplate === tpl.id ? 'text-indigo-100' : 'text-slate-600'}`}>{tpl.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
             <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Export Options</h3>
             <div className="space-y-3">
                <button className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex items-center justify-center gap-2 transition-all text-xs">
                   <FileText className="w-4 h-4 text-rose-400" />
                   Generate PDF
                </button>
                <button className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex items-center justify-center gap-2 transition-all text-xs">
                   <Download className="w-4 h-4 text-blue-400" />
                   Download .DOCX
                </button>
             </div>
          </div>
        </div>

        {/* Main Editor / Preview */}
        <div className="flex-1 bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden flex flex-col min-h-[800px]">
           <div className="bg-slate-950/50 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
              <div className="flex bg-slate-900 rounded-xl p-1">
                 <button
                   onClick={() => setViewMode("edit")}
                   className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${viewMode === "edit" ? "bg-slate-800 text-white shadow" : "text-slate-500 hover:text-slate-300"}`}
                 >
                   <Edit3 className="w-3.5 h-3.5" /> Edit
                 </button>
                 <button
                   onClick={() => setViewMode("preview")}
                   className={`px-4 py-2 rounded-lg text-xs font-bold flex items-center gap-2 transition-all ${viewMode === "preview" ? "bg-slate-800 text-white shadow" : "text-slate-500 hover:text-slate-300"}`}
                 >
                   <Eye className="w-3.5 h-3.5" /> Preview
                 </button>
              </div>
              <div className="flex items-center gap-2 text-[10px] font-black text-slate-600 uppercase tracking-widest">
                 <Settings2 className="w-3.5 h-3.5" /> Auto-Save Active
              </div>
           </div>

           <div className="flex-1 p-8 overflow-y-auto bg-slate-950/30">
              {viewMode === "edit" ? (
                <div className="max-w-3xl mx-auto space-y-12">
                   {/* Personal Info */}
                   <section className="space-y-6">
                      <h4 className="text-xs font-black text-indigo-400 uppercase tracking-[0.2em] border-b border-slate-800 pb-2">Master Identity</h4>
                      <div className="grid grid-cols-2 gap-6">
                         <div className="space-y-1">
                            <label className="text-[10px] font-bold text-slate-600 uppercase">Full Name</label>
                            <input className="w-full bg-transparent border-b border-slate-800 focus:border-indigo-500 py-1 text-white outline-none transition-all" defaultValue="Alex Developer" />
                         </div>
                         <div className="space-y-1">
                            <label className="text-[10px] font-bold text-slate-600 uppercase">Professional Title</label>
                            <input className="w-full bg-transparent border-b border-slate-800 focus:border-indigo-500 py-1 text-white outline-none transition-all" defaultValue="Senior Full-Stack Engineer" />
                         </div>
                      </div>
                   </section>

                   {/* Experience */}
                   <section className="space-y-6">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                         <h4 className="text-xs font-black text-indigo-400 uppercase tracking-[0.2em]">Work History</h4>
                         <button className="text-indigo-400 hover:text-indigo-300 p-1 transition-colors"><Plus className="w-4 h-4" /></button>
                      </div>
                      <div className="space-y-8">
                         {[1].map(i => (
                           <div key={i} className="group relative p-6 bg-slate-900/50 rounded-2xl border border-slate-800 hover:border-slate-700 transition-all">
                              <button className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 p-2 text-rose-500 hover:bg-rose-500/10 rounded-lg transition-all"><Trash2 className="w-4 h-4" /></button>
                              <div className="grid grid-cols-2 gap-4 mb-4">
                                 <input className="bg-transparent border-b border-slate-800 focus:border-indigo-500 py-1 text-white font-bold outline-none" placeholder="Company Name" defaultValue="TechCorp" />
                                 <input className="bg-transparent border-b border-slate-800 focus:border-indigo-500 py-1 text-white outline-none" placeholder="Location" defaultValue="San Francisco, CA" />
                                 <input className="bg-transparent border-b border-slate-800 focus:border-indigo-500 py-1 text-white outline-none" placeholder="Role" defaultValue="Lead Developer" />
                                 <input className="bg-transparent border-b border-slate-800 focus:border-indigo-500 py-1 text-white outline-none" placeholder="Dates" defaultValue="2021 - Present" />
                              </div>
                              <textarea className="w-full bg-slate-950/50 border border-slate-800 rounded-xl p-4 text-xs text-slate-400 min-h-[100px] outline-none focus:border-indigo-500" defaultValue="- Led architectural migration to microservices... \n- Optimized database queries resulting in 40% latency reduction..." />
                           </div>
                         ))}
                      </div>
                   </section>
                </div>
              ) : (
                <div className="bg-white text-black w-full min-h-[1000px] shadow-2xl p-12 max-w-[800px] mx-auto font-serif">
                   {/* Realistic Resume Preview Mockup */}
                   <header className="text-center mb-8 border-b-2 border-black pb-4">
                      <h1 className="text-3xl font-bold uppercase tracking-tighter mb-2">Alex Developer</h1>
                      <p className="text-sm italic">San Francisco, CA | alex.dev@email.com | (555) 0123-4567</p>
                   </header>
                   <section className="mb-6">
                      <h2 className="text-lg font-bold uppercase border-b border-black mb-3">Professional Experience</h2>
                      <div className="mb-4">
                         <div className="flex justify-between font-bold">
                            <span>TECHCORP</span>
                            <span>2021 – Present</span>
                         </div>
                         <div className="flex justify-between italic mb-2">
                            <span>Lead Full-Stack Developer</span>
                            <span>San Francisco, CA</span>
                         </div>
                         <ul className="list-disc ml-5 text-sm space-y-1">
                            <li>Architected and implemented a high-performance career automation engine processing 1M+ records daily.</li>
                            <li>Engineered a 3-tier fallback AI routing system using Groq and Gemini, reducing operational costs by 60%.</li>
                         </ul>
                      </div>
                   </section>
                </div>
              )}
           </div>
        </div>
      </div>
    </div>
  );
}
