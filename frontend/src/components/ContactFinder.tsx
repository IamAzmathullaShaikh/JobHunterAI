import React, { useState } from "react";
import { SearchCode, Users, MessageSquareCode, Copy, Check, Loader2, Link2, HelpCircle } from "lucide-react";
import { ContactFinderDTO } from "../types.ts";

interface ContactFinderProps {
  defaultSearchQuery: string;
}

export default function ContactFinder({ defaultSearchQuery }: ContactFinderProps) {
  const [companyName, setCompanyName] = useState("Prayag Marketing");
  const [targetRole, setTargetRole] = useState(defaultSearchQuery || "Territory Sales Executive");
  const [isSearching, setIsSearching] = useState(false);
  const [contactResult, setContactResult] = useState<ContactFinderDTO | null>(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!companyName.trim()) {
      setError("Please specify a target company name.");
      return;
    }

    setIsSearching(true);
    setError(null);
    setContactResult(null);
    try {
      const response = await fetch("/api/outreach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: companyName,
          target_role: targetRole,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to search contacts.");
      }

      const data = await response.json();
      setContactResult(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Something went wrong during the lookup.");
    } finally {
      setIsSearching(false);
    }
  };

  const copyToClipboard = () => {
    if (!contactResult) return;
    navigator.clipboard.writeText(contactResult.cold_outreach_dm_template);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-800/60 rounded-xl p-6 border border-slate-700/80 shadow-md">
      <div>
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Users className="w-5 h-5 text-indigo-400" />
          🎯 Find hiring managers and recruiters
        </h3>
        <p className="text-xs text-slate-400 mt-0.5">
          Step 4: Find people who can hire you and get an AI-drafted message to send them.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        {/* Left Input form */}
        <div className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">
              Company Name
            </label>
            <input
              type="text"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="e.g. Google, Prayag Marketing"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">
              Job Title
            </label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 px-3 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              placeholder="e.g. Territory Sales Executive"
            />
          </div>

          {error && <div className="text-rose-400 text-xs font-medium bg-rose-500/10 p-2.5 rounded border border-rose-500/20">{error}</div>}

          <button
            onClick={handleSearch}
            disabled={isSearching}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed text-slate-100 font-bold text-sm py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-md cursor-pointer"
          >
            {isSearching ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Finding contacts...
              </>
            ) : (
              <>
                <SearchCode className="w-4 h-4" />
                Find Recruiters & Draft Message
              </>
            )}
          </button>
        </div>

        {/* Right Output results */}
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-5 flex flex-col justify-between min-h-[220px]">
          {isSearching ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-6">
              <Loader2 className="w-8 h-8 animate-spin text-indigo-400 mb-2" />
              <p className="text-xs text-slate-400">Looking for recruiters and writing your message...</p>
            </div>
          ) : contactResult ? (
            <div className="space-y-5 flex-1 flex flex-col justify-between">
              <div>
                <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                  <Link2 className="w-3.5 h-3.5" />
                  🔗 Search Links:
                </h4>
                <ul className="space-y-1.5 text-xs text-slate-300">
                  {Object.entries(contactResult.suggested_search_queries).map(([label, url]) => (
                    <li key={label} className="flex items-center gap-1 bg-slate-950 p-2 rounded border border-slate-850 hover:border-slate-700 transition-colors">
                      <span className="font-semibold text-indigo-300">🌐 {label}:</span>
                      <a
                        href={url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-emerald-400 hover:text-emerald-300 font-semibold underline truncate block max-w-[200px] sm:max-w-[250px]"
                      >
                        Click to search
                      </a>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-3 border-t border-slate-850 flex-1 flex flex-col">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1">
                    <MessageSquareCode className="w-3.5 h-3.5" />
                    💬 Your personalized message:
                  </h4>
                  <button
                    onClick={copyToClipboard}
                    className="text-[11px] text-slate-400 hover:text-slate-200 flex items-center gap-1 font-semibold bg-slate-800 hover:bg-slate-750 border border-slate-700/60 px-2 py-0.5 rounded cursor-pointer transition-colors"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        Copy
                      </>
                    )}
                  </button>
                </div>
                <div className="bg-slate-950 p-3 rounded border border-slate-850 text-xs font-mono text-slate-300 overflow-y-auto max-h-[160px] whitespace-pre-wrap leading-relaxed select-all">
                  {contactResult.cold_outreach_dm_template}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center text-slate-500 py-6">
              <HelpCircle className="w-10 h-10 text-slate-600 mb-2" />
              <p className="text-xs">Enter a company and job title to find recruiters.</p>
              <span className="text-[10px] text-slate-600 mt-1"></span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
