import React, { useState, useEffect } from "react";
import { Users, Search, Mail, Linkedin, Loader2, Sparkles, Copy, Check, Filter, Trash2, Save, Send, Building2, UserCircle, Wand2, FileText } from "lucide-react";
import EngineStatusChip from "./EngineStatusChip.tsx";
import { CandidateProfile, Resume, RecruiterContact } from "../types.ts";

interface RecruiterFinderProps {
  resumeText: string;
  profile: CandidateProfile | null;
  resumes: Resume[];
}

export default function RecruiterFinder({ resumeText, profile, resumes }: RecruiterFinderProps) {
  const [activeTab, setActiveTab] = useState<"find" | "crm">("find");

  const [company, setCompany] = useState("");
  const [department, setDepartment] = useState("Engineering");
  const [isSearching, setIsSearching] = useState(false);
  const [discoveredLeads, setDiscoveredLeads] = useState<RecruiterContact[]>([]);

  const [crmContacts, setCrmContacts] = useState<RecruiterContact[]>([]);
  const [selectedContact, setSelectedContact] = useState<RecruiterContact | null>(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const [outreachDraft, setOutreachDraft] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (activeTab === "crm") loadCRM();
  }, [activeTab]);

  const loadCRM = async () => {
    try {
      const res = await fetch("/api/recruiters/contacts");
      setCrmContacts(await res.json());
    } catch (err) { console.error(err); }
  };

  const findRecruiters = async () => {
    if (!company) return;
    setIsSearching(true);
    setDiscoveredLeads([]);
    try {
      const response = await fetch("/api/recruiters/find", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: company,
          department: department,
          resume_text: resumeText
        })
      });
      const data = await response.json();
      // Map API lead to RecruiterContact
      setDiscoveredLeads(data.map((l: any) => ({
        name: l.person_name,
        title: l.title,
        company: company,
        department: department,
        email: l.email,
        linkedin_url: l.linkedin_url,
        confidence_score: l.confidence_score,
        match_explanation: l.match_explanation,
        status: "Not Contacted"
      })));
    } catch (err) { console.error(err); }
    finally { setIsSearching(false); }
  };

  const addToCRM = async (contact: RecruiterContact) => {
    try {
      const res = await fetch("/api/recruiters/contacts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(contact)
      });
      const newContact = await res.json();
      setCrmContacts(prev => [newContact, ...prev]);
      // Remove from discovered
      setDiscoveredLeads(prev => prev.filter(l => l.linkedin_url !== contact.linkedin_url));
    } catch (err) { console.error(err); }
  };

  const updateCRMContact = async (id: number, status: string, notes: string) => {
    try {
      const res = await fetch(`/api/recruiters/contacts/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status, notes })
      });
      const updated = await res.json();
      setCrmContacts(prev => prev.map(c => c.id === id ? updated : c));
      setSelectedContact(updated);
    } catch (err) { console.error(err); }
  };

  const generateOutreach = async (contactId: number) => {
    if (resumes.length === 0) return;
    setIsGenerating(true);
    try {
      const res = await fetch("/api/recruiters/generate-outreach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recruiter_id: contactId,
          resume_id: resumes[0].id,
          message_type: "Intro"
        })
      });
      const data = await res.json();
      setOutreachDraft(data.outreach);
    } catch (err) { console.error(err); }
    finally { setIsGenerating(false); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-indigo-400" />
            <h2 className="text-xl font-black text-white uppercase tracking-tight">Recruiter Intelligence</h2>
          </div>
          <div className="flex bg-slate-950 rounded-xl p-1 p-1 border border-slate-800">
             <button onClick={() => setActiveTab("find")} className={`px-4 py-1.5 rounded-lg text-[10px] font-black uppercase transition-all ${activeTab === 'find' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}>Discovery</button>
             <button onClick={() => setActiveTab("crm")} className={`px-4 py-1.5 rounded-lg text-[10px] font-black uppercase transition-all ${activeTab === 'crm' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}>My CRM</button>
          </div>
        </div>

        {activeTab === "find" ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Target Company</label>
                <div className="relative">
                  <Building2 className="absolute left-3 top-2.5 w-4 h-4 text-slate-600" />
                  <input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="e.g. Stripe, Google" className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:border-indigo-500 outline-none transition-all" />
                </div>
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Department</label>
                <select value={department} onChange={(e) => setDepartment(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500 outline-none transition-all">
                  {["Engineering", "Product", "Sales", "Human Resources", "Marketing"].map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div className="flex items-end">
                <button onClick={findRecruiters} disabled={isSearching} className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-bold py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all">
                  {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />} Identify Decision Makers
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
               <div className="lg:col-span-2 space-y-4">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">Discovered Profiles</h3>
                  {discoveredLeads.length > 0 ? discoveredLeads.map((lead, i) => (
                    <div key={i} className="bg-slate-950/50 border border-slate-800 rounded-2xl p-4 flex items-center justify-between hover:border-slate-700 transition-all group">
                       <div className="flex items-center gap-4">
                          <div className="w-10 h-10 bg-slate-900 rounded-full flex items-center justify-center border border-slate-800 text-indigo-400 font-black text-xs">{lead.name[0]}</div>
                          <div>
                             <div className="font-bold text-white text-sm">{lead.name}</div>
                             <div className="text-[10px] text-slate-500 font-bold uppercase tracking-tight">{lead.title}</div>
                             {lead.match_explanation && <div className="text-[9px] text-indigo-400 mt-1 italic max-w-[200px]">{lead.match_explanation}</div>}
                          </div>
                       </div>
                       <div className="flex items-center gap-3">
                          <div className="text-right hidden sm:block">
                             <div className="text-[10px] font-black text-emerald-400 uppercase">Verified</div>
                             <div className="text-[9px] text-slate-600 font-mono">{lead.email || "No Email Found"}</div>
                          </div>
                          <button onClick={() => addToCRM(lead)} className="bg-slate-800 hover:bg-indigo-600 p-2 rounded-xl text-slate-400 hover:text-white transition-all"><Save className="w-4 h-4" /></button>
                       </div>
                    </div>
                  )) : (
                    <div className="h-48 border border-dashed border-slate-800 rounded-3xl flex flex-col items-center justify-center opacity-20">
                       <UserCircle className="w-8 h-8 mb-2" />
                       <p className="text-[10px] font-black uppercase">Launch discovery to find real contacts</p>
                    </div>
                  )}
               </div>
               <div className="bg-slate-950/30 border border-slate-800 rounded-3xl p-6">
                  <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-4 flex items-center gap-2"><Sparkles className="w-3.5 h-3.5" /> AI Insight</h3>
                  <p className="text-[11px] text-slate-500 leading-relaxed italic">Discovered recruiters are ranked based on their relevance to the {department} department and current open roles at {company || "the company"}.</p>
               </div>
            </div>
          </>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
             <div className="lg:col-span-2 space-y-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">Tracked Contacts</h3>
                <div className="space-y-3">
                   {crmContacts.map(c => (
                     <div key={c.id} onClick={() => { setSelectedContact(c); setOutreachDraft(""); }} className={`p-4 rounded-2xl border cursor-pointer transition-all ${selectedContact?.id === c.id ? 'bg-indigo-600/10 border-indigo-500' : 'bg-slate-950/50 border-slate-800 hover:border-slate-700'}`}>
                        <div className="flex justify-between items-start">
                           <div>
                              <div className="font-bold text-white">{c.name}</div>
                              <div className="text-xs text-slate-500">{c.title} @ {c.company}</div>
                           </div>
                           <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded border ${c.status === 'Sent' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-slate-900 border-slate-800 text-slate-500'}`}>{c.status}</span>
                        </div>
                     </div>
                   ))}
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 mt-6">
                   <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Export My CRM</h3>
                   <div className="grid grid-cols-2 gap-3">
                      <a href="/api/recruiters/export?format=csv" target="_blank" className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex items-center justify-center gap-2 transition-all text-[10px]">
                         <FileText className="w-4 h-4 text-emerald-400" /> Export CSV
                      </a>
                      <a href="/api/recruiters/export?format=xlsx" target="_blank" className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 rounded-2xl flex items-center justify-center gap-2 transition-all text-[10px]">
                         <Save className="w-4 h-4 text-blue-400" /> Export Excel
                      </a>
                   </div>
                </div>
             </div>

             <div className="bg-slate-950 border border-slate-800 rounded-3xl p-6 flex flex-col min-h-[500px]">
                {selectedContact ? (
                   <div className="space-y-6 animate-fade-in flex flex-col h-full">
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-600/20 text-white font-black text-xl">{selectedContact.name[0]}</div>
                            <div>
                               <h4 className="font-black text-white">{selectedContact.name}</h4>
                               <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase">
                                  <Building2 className="w-3 h-3" /> {selectedContact.company}
                                  <Linkedin className="w-3 h-3" /> <a href={selectedContact.linkedin_url} target="_blank" className="hover:text-indigo-400">Profile</a>
                               </div>
                            </div>
                         </div>
                         <button onClick={() => generateOutreach(selectedContact.id!)} disabled={isGenerating} className="bg-slate-800 hover:bg-indigo-600 p-2 rounded-xl text-slate-400 hover:text-white transition-all">
                            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                         </button>
                      </div>

                      <div className="space-y-2">
                         <label className="text-[10px] font-black text-slate-600 uppercase">Outreach Status</label>
                         <div className="grid grid-cols-3 gap-2">
                            {["Not Contacted", "Draft Ready", "Sent", "Viewed", "Replied", "Closed"].map(s => (
                              <button key={s} onClick={() => updateCRMContact(selectedContact.id!, s, selectedContact.notes || "")} className={`py-1.5 rounded-lg border text-[9px] font-black uppercase transition-all ${selectedContact.status === s ? 'bg-indigo-600 border-indigo-500 text-white' : 'bg-slate-900 border-slate-800 text-slate-600 hover:border-slate-700'}`}>{s}</button>
                            ))}
                         </div>
                      </div>

                      <div className="flex-1 flex flex-col space-y-4">
                         <div className="flex-1 bg-slate-900/50 border border-slate-800 rounded-2xl p-4 flex flex-col">
                            <h5 className="text-[9px] font-black text-indigo-400 uppercase tracking-widest mb-3">Personalized Outreach Draft</h5>
                            <div className="flex-1 text-[11px] text-slate-300 font-sans whitespace-pre-wrap overflow-y-auto max-h-[150px]">
                               {outreachDraft || "Select 'Magic Wand' to generate a hyper-tailored intro using your resume."}
                            </div>
                            {outreachDraft && <button onClick={() => { navigator.clipboard.writeText(outreachDraft); setCopied(true); setTimeout(()=>setCopied(false),2000); }} className="mt-2 text-[9px] font-black uppercase text-indigo-400 flex items-center justify-end gap-1">{copied ? "Copied!" : "Copy Draft"}</button>}
                         </div>

                         <div className="space-y-2">
                            <label className="text-[10px] font-black text-slate-600 uppercase">Internal CRM Notes</label>
                            <textarea value={selectedContact.notes || ""} onChange={(e) => updateCRMContact(selectedContact.id!, selectedContact.status, e.target.value)} placeholder="Add conversation history or follow-up notes..." className="w-full h-24 bg-slate-900 border border-slate-800 rounded-2xl p-4 text-xs text-slate-400 outline-none focus:border-indigo-500 resize-none" />
                         </div>
                      </div>
                   </div>
                ) : (
                   <div className="flex-1 flex flex-col items-center justify-center text-center opacity-20">
                      <UserCircle className="w-12 h-12 mb-3" />
                      <p className="text-[10px] font-black uppercase">Select a contact to manage outreach</p>
                   </div>
                )}
             </div>
          </div>
        )}
      </div>
    </div>
  );
}
