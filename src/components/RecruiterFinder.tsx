import React, { useState } from "react";
import { Users, Search, Mail, Linkedin, Loader2, Sparkles, Copy, Check } from "lucide-react";
import EngineStatusChip from "./EngineStatusChip.tsx";

interface RecruiterLead {
  person_name: string;
  title: string;
  email: string;
  linkedin_url: string;
  confidence_score: number;
  draft_email?: string;
}

export default function RecruiterFinder() {
  const [company, setCompany] = useState("");
  const [department, setDepartment] = useState("Engineering");
  const [isSearching, setIsSearching] = useState(false);
  const [leads, setLeads] = useState<RecruiterLead[]>([]);
  const [selectedLead, setSelectedLead] = useState<RecruiterLead | null>(null);
  const [copied, setCopied] = useState(false);

  const findRecruiters = async () => {
    if (!company) return;
    setIsSearching(true);
    try {
      const response = await fetch("/api/recruiters/find", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company_name: company, department: department })
      });
      const data = await response.json();
      setLeads(data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsSearching(false);
    }
  };

  const copyEmail = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <Users className="w-6 h-6 text-indigo-400" />
          <h2 className="text-xl font-black text-white uppercase tracking-tight">Recruiter & Decision-Maker Finder</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="space-y-1">
            <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Target Company</label>
            <input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Stripe, Google"
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500 outline-none transition-all"
            />
          </div>
          <div className="space-y-1">
            <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Department</label>
            <select
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-indigo-500 outline-none transition-all"
            >
              <option>Engineering</option>
              <option>Sales</option>
              <option>Product</option>
              <option>Human Resources</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={findRecruiters}
              disabled={isSearching}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-bold py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all"
            >
              {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Identify Leads
            </button>
          </div>
        </div>

        {leads.length > 0 && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest px-1">Discovered Contacts</h3>
              {leads.map((lead, i) => (
                <div
                  key={i}
                  onClick={() => setSelectedLead(lead)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all ${selectedLead?.person_name === lead.person_name ? 'bg-indigo-600/10 border-indigo-500' : 'bg-slate-950/50 border-slate-800 hover:border-slate-700'}`}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-bold text-white">{lead.person_name}</div>
                      <div className="text-xs text-slate-400">{lead.title}</div>
                    </div>
                    <div className="flex gap-2">
                      <a href={lead.linkedin_url} target="_blank" className="p-1.5 bg-slate-800 rounded-lg hover:text-indigo-400 transition-colors"><Linkedin className="w-3.5 h-3.5" /></a>
                      <div className="bg-emerald-500/10 text-emerald-400 text-[10px] font-bold px-2 py-1 rounded-lg border border-emerald-500/20">{Math.round(lead.confidence_score * 100)}% Match</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-slate-950/50 border border-slate-800 rounded-3xl p-6 flex flex-col">
              {selectedLead ? (
                <div className="space-y-6 flex-1 flex flex-col animate-fade-in">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-widest">Cold Outreach Draft</h3>
                    <button
                      onClick={() => selectedLead.draft_email && copyEmail(selectedLead.draft_email)}
                      className="text-[10px] font-bold bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg flex items-center gap-2 transition-all"
                    >
                      {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                      {copied ? "Copied!" : "Copy Draft"}
                    </button>
                  </div>
                  <div className="flex-1 bg-slate-900/50 rounded-2xl p-4 text-xs text-slate-300 font-mono whitespace-pre-wrap leading-relaxed border border-slate-800 overflow-y-auto max-h-[300px]">
                    {selectedLead.draft_email || "Generating custom draft..."}
                  </div>
                  <div className="flex items-center gap-3 text-[10px] text-slate-500 font-bold bg-slate-900/30 p-3 rounded-xl">
                    <Mail className="w-3.5 h-3.5" />
                    Verified Email: <span className="text-emerald-400">{selectedLead.email}</span>
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center space-y-3 opacity-30">
                  <Sparkles className="w-10 h-10" />
                  <p className="text-sm font-bold uppercase tracking-tighter">Select a contact to generate outreach</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
