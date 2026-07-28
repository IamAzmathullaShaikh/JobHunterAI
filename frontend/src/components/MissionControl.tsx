import React from "react";
import {
  BarChart3,
  Briefcase,
  CheckCircle,
  Clock,
  Flame,
  Target,
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  FileText
} from "lucide-react";
import { JobListing, CandidateProfile } from "../types";
import { cn } from "../lib/utils";

import { Card, CardHeader, CardTitle, CardContent } from "./ui/Card";
import { Button } from "./ui/Button";

interface MissionControlProps {
  jobs: JobListing[];
  profile: CandidateProfile | null;
  onNavigate: (tab: any) => void;
}

export default function MissionControl({ jobs, profile, onNavigate }: MissionControlProps) {
  const trackedCount = jobs.filter(j => j.application).length;
  const interviewingCount = jobs.filter(j => j.application?.status === "Interviewing").length;

  const stats = [
    { label: "Tracked Roles", value: trackedCount, icon: Briefcase, color: "text-indigo-400" },
    { label: "Interviewing", value: interviewingCount, icon: Clock, color: "text-emerald-400" },
    { label: "Profile Status", value: profile ? "100%" : "0%", icon: ShieldCheck, color: "text-blue-400" },
    { label: "Application Velocity", value: "8/wk", icon: Flame, color: "text-orange-400" },
  ];

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-3xl font-black tracking-tight text-white">
            System <span className="text-indigo-400 italic">Overview</span>
          </h2>
          <p className="text-slate-500 text-sm mt-1 font-medium italic">Your career fleet is operational and ready for deployment.</p>
        </div>
        <div className="flex items-center gap-3">
           <Button onClick={() => onNavigate("jobs")} size="lg">
             Discover Jobs <ArrowRight className="w-3 h-3 ml-2" />
           </Button>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <Card key={idx} className="group hover:border-indigo-500/30">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
               <div className={cn("p-2 rounded-xl bg-black border border-slate-800", stat.color)}>
                 <stat.icon className="w-4 h-4" />
               </div>
               <TrendingUp className="w-4 h-4 text-slate-700" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-black text-white">{stat.value}</div>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">{stat.label}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Secondary Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
         {/* Recent Jobs */}
         <div className="xl:col-span-2 space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-indigo-400" />
              Pipeline <span className="text-slate-500">Activity</span>
            </h3>
            <Card className="rounded-[32px] overflow-hidden">
               <div className="divide-y divide-slate-800/50">
                  {jobs.slice(0, 5).map(job => (
                    <div key={job.id} className="p-5 flex items-center justify-between hover:bg-white/[0.02] transition-colors group">
                       <div className="flex items-center gap-4">
                          <div className="w-10 h-10 rounded-2xl bg-black border border-slate-800 flex items-center justify-center text-xs font-black text-slate-400 group-hover:border-indigo-500/50 transition-colors">
                             {job.company_name.charAt(0)}
                          </div>
                          <div>
                             <div className="text-sm font-bold text-white">{job.title}</div>
                             <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{job.company_name}</div>
                          </div>
                       </div>
                       <div className="flex items-center gap-6">
                          <span className="hidden md:inline text-[10px] font-bold text-slate-600 uppercase tracking-widest">{job.source}</span>
                          <div className="bg-black px-3 py-1.5 rounded-xl border border-slate-800 text-[10px] font-black text-slate-400">
                            {job.application?.status || "Discovered"}
                          </div>
                       </div>
                    </div>
                  ))}
                  {jobs.length === 0 && (
                    <div className="p-20 text-center space-y-4">
                      <div className="inline-flex p-4 rounded-3xl bg-slate-900 border border-slate-800 text-slate-700">
                        <Target className="w-8 h-8" />
                      </div>
                      <p className="text-slate-600 text-xs font-bold uppercase tracking-tighter">No active pipeline data discovered.</p>
                    </div>
                  )}
               </div>
            </Card>
         </div>

         {/* Document Shortcuts */}
         <div className="space-y-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" />
              Quick <span className="text-slate-500">Links</span>
            </h3>
            <div className="grid grid-cols-1 gap-4">
               {[
                 { label: "Resume Builder", tab: "builder", desc: "Refine your AI resume" },
                 { label: "Cover Letter", tab: "cover", desc: "Generate targeted drafts" },
                 { label: "Prep Studio", tab: "prep", desc: "Practice STAR questions" },
               ].map(link => (
                 <Card
                   key={link.tab}
                   className="p-1 hover:border-indigo-500/30 cursor-pointer group"
                   onClick={() => onNavigate(link.tab)}
                 >
                    <div className="p-4 bg-black/40 rounded-[22px] border border-transparent group-hover:border-indigo-500/10 transition-all">
                       <div className="text-xs font-black text-white group-hover:text-indigo-400 transition-colors uppercase tracking-tight">{link.label}</div>
                       <div className="text-[10px] text-slate-500 mt-1 font-bold">{link.desc}</div>
                    </div>
                 </Card>
               ))}
            </div>
         </div>
      </div>
    </div>
  );
}
