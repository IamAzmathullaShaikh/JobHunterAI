import React from "react";
import {
  Sparkles,
  Target,
  FileSignature,
  Layout,
  FileText,
  Brain,
  Users,
  Briefcase,
  ClipboardList,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Zap
} from "lucide-react";
import { cn } from "../lib/utils";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: any) => void;
  isCollapsed: boolean;
  setIsCollapsed: (val: boolean) => void;
  telemetry?: any;
}

export default function Sidebar({
  activeTab,
  setActiveTab,
  isCollapsed,
  setIsCollapsed,
  telemetry
}: SidebarProps) {

  const navItems = [
    { id: "ats", label: "ATS Matcher", icon: Target },
    { id: "writer", label: "Resume Writer", icon: FileSignature },
    { id: "builder", label: "Resume Builder", icon: Layout },
    { id: "cover", label: "Cover Letter", icon: FileText },
    { id: "prep", label: "Prep Studio", icon: Brain },
    { id: "recruiters", label: "Recruiter Finder", icon: Users },
    { id: "jobs", label: "Job Board", icon: Briefcase },
    { id: "kanban", label: "Tracker CRM", icon: ClipboardList },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
  ];

  return (
    <aside
      className={cn(
        "h-screen bg-slate-950 border-r border-slate-900 transition-all duration-300 flex flex-col z-50",
        isCollapsed ? "w-20" : "w-64"
      )}
    >
      {/* Header */}
      <div className="p-6 flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center gap-3">
            <div className="bg-indigo-600 p-1.5 rounded-lg shadow-lg shadow-indigo-600/20">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-sm font-black tracking-tighter text-white uppercase italic">
              JobHunter<span className="text-indigo-400">AI</span>
            </h1>
          </div>
        )}
        {isCollapsed && (
           <div className="mx-auto bg-indigo-600 p-1.5 rounded-lg shadow-lg shadow-indigo-600/20">
             <Sparkles className="w-4 h-4 text-white" />
           </div>
        )}
      </div>

      {/* Nav Items */}
      <nav className="flex-1 px-3 space-y-1 mt-4">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={cn(
              "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all group",
              activeTab === item.id
                ? "bg-indigo-600/10 text-indigo-400 border border-indigo-500/20"
                : "text-slate-500 hover:text-slate-100 hover:bg-slate-900"
            )}
          >
            <item.icon className={cn(
              "w-4 h-4 shrink-0",
              activeTab === item.id ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-100"
            )} />
            {!isCollapsed && <span>{item.label}</span>}
            {!isCollapsed && activeTab === item.id && (
              <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400" />
            )}
          </button>
        ))}
      </nav>

      {/* Footer / Status */}
      <div className="p-4 border-t border-slate-900 space-y-4">
        {!isCollapsed && (
          <div className="bg-slate-900/50 rounded-2xl p-4 border border-slate-800/50">
            <div className="flex items-center justify-between mb-3">
               <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Engine Status</span>
               <div className="flex items-center gap-1.5">
                  <div className={cn(
                    "w-1.5 h-1.5 rounded-full",
                    telemetry?.keys?.groq ? "bg-emerald-500 animate-pulse" : "bg-red-500"
                  )} />
                  <span className="text-[10px] font-bold text-slate-400">GROQ</span>
               </div>
            </div>
            <div className="flex items-center gap-2 text-xs">
               <Zap className="w-3 h-3 text-indigo-400" />
               <span className="text-slate-300 font-mono text-[10px]">{telemetry?.circuit_breakers?.groq?.latency || "---"} ms</span>
            </div>
          </div>
        )}

        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full flex items-center justify-center p-2 rounded-xl border border-slate-800 hover:bg-slate-900 text-slate-500 transition-colors"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}
