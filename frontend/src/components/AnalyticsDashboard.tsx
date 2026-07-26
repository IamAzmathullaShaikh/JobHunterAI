import React, { useState, useEffect } from "react";
import {
  BarChart3, TrendingUp, Target, Activity, Loader2, ArrowUpRight,
  AlertCircle, Briefcase, Users, Brain, History, Sparkles,
  ChevronRight, PieChart, Database, ListTodo
} from "lucide-react";

export default function AnalyticsDashboard() {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    async function fetchAnalytics() {
      setIsLoading(true);
      try {
        const response = await fetch(`/api/tracker/analytics?days=${days}`);
        const result = await response.json();
        setData(result);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchAnalytics();
  }, [days]);

  if (isLoading) {
    return (
      <div className="h-[600px] flex flex-col items-center justify-center space-y-4 bg-slate-900 border border-slate-800 rounded-3xl">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-slate-500 font-bold uppercase tracking-widest text-[10px]">Assembling Mission Control...</p>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-8 animate-fade-in">

      {/* Header & Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
             <h2 className="text-2xl font-black text-white uppercase italic tracking-tight">Mission Control</h2>
             <span className="bg-indigo-600/10 text-indigo-400 text-[9px] font-black px-2 py-0.5 rounded border border-indigo-500/20 uppercase">{data.current_status}</span>
          </div>
          <p className="text-xs text-slate-500 font-bold uppercase tracking-widest mt-1">Global Intelligence Dashboard</p>
        </div>
        <div className="flex bg-slate-900 rounded-xl p-1 border border-slate-800">
           {[7, 30, 90].map(d => (
             <button
               key={d}
               onClick={() => setDays(d)}
               className={`px-4 py-1.5 rounded-lg text-[10px] font-black uppercase transition-all ${days === d ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}
             >
               Last {d} Days
             </button>
           ))}
        </div>
      </div>

      {/* Row 1: Executive KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard title="Total Applications" value={data.kpis.funnel.applied} sub="Active searches" icon={Briefcase} color="text-indigo-400" />
        <MetricCard title="Success Rate" value={`${data.kpis.funnel.success_rate}%`} sub="Application to Offer" icon={ArrowUpRight} color="text-emerald-400" />
        <MetricCard title="Recruiter Response" value={`${data.kpis.networking.response_rate}%`} sub="Outreach impact" icon={Users} color="text-amber-400" />
        <MetricCard title="Avg ATS Score" value={`${data.kpis.resume.avg_ats_score}%`} sub="Resume quality" icon={Target} color="text-purple-400" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">

        {/* Row 2, Col 1-2: AI Insights & Skill Gaps */}
        <div className="xl:col-span-2 space-y-8">
          <div className="bg-indigo-600/5 border border-indigo-500/20 rounded-3xl p-8 relative overflow-hidden group">
             <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:scale-110 transition-transform"><Sparkles className="w-32 h-32 text-indigo-400" /></div>
             <h3 className="text-xs font-black text-indigo-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
                <Brain className="w-4 h-4" /> AI Strategic Recommendations
             </h3>
             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {data.recommendations.map((rec: string, i: number) => (
                  <div key={i} className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl flex items-start gap-4">
                     <div className="w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center shrink-0 text-[10px] font-black text-white">{i+1}</div>
                     <p className="text-sm text-slate-300 font-medium leading-relaxed">{rec}</p>
                  </div>
                ))}
             </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
             <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
                <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2"><Target className="w-4 h-4 text-emerald-400" /> Market Skill Demand</h3>
                <div className="space-y-4">
                   {data.skill_insights.top_market_skills.map((s: any, i: number) => (
                     <div key={i} className="space-y-2">
                        <div className="flex justify-between text-[10px] font-bold">
                           <span className="text-slate-300 uppercase">{s.name}</span>
                           <span className="text-slate-500">{s.demand} Jobs</span>
                        </div>
                        <div className="h-1.5 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                           <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${(s.demand / data.kpis.funnel.applied) * 100}%` }} />
                        </div>
                     </div>
                   ))}
                </div>
             </div>

             <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 flex flex-col">
                <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2"><AlertCircle className="w-4 h-4 text-rose-400" /> Identified Skill Gaps</h3>
                <div className="flex-1 flex flex-wrap gap-2 content-start">
                   {data.skill_insights.identified_gaps.map((gap: string, i: number) => (
                     <div key={i} className="px-4 py-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-xs font-bold uppercase tracking-tight flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-rose-500 rounded-full animate-pulse" />
                        {gap}
                     </div>
                   ))}
                </div>
                <p className="mt-6 text-[10px] text-slate-600 italic">Recommendations: Consider updating your projects to include these technologies.</p>
             </div>
          </div>
        </div>

        {/* Row 2, Col 3: Career Timeline */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 flex flex-col">
           <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-8 flex items-center gap-2"><History className="w-4 h-4 text-indigo-400" /> Activity Timeline</h3>
           <div className="flex-1 space-y-8 overflow-y-auto max-h-[600px] pr-2 custom-scrollbar">
              {data.timeline.map((event: any, i: number) => (
                <div key={i} className="relative pl-6 border-l border-slate-800 last:border-0 pb-8 last:pb-0">
                   <div className="absolute -left-1.5 top-0 w-3 h-3 bg-indigo-600 rounded-full border-4 border-slate-900" />
                   <div className="text-[10px] text-slate-500 font-mono mb-1">{new Date(event.date).toLocaleDateString()}</div>
                   <div className="text-sm font-bold text-white mb-1">{event.title}</div>
                   <div className="text-[9px] font-black uppercase text-indigo-400/60 tracking-widest">{event.type.replace('_', ' ')}</div>
                </div>
              ))}
              {data.timeline.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center opacity-20 space-y-3">
                   <ListTodo className="w-12 h-12" />
                   <p className="text-[10px] font-black uppercase">No search events recorded yet</p>
                </div>
              )}
           </div>
        </div>

      </div>

      {/* Row 3: Distributions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
         <DistributionCard title="Source Mix" data={data.job_distribution.by_source} icon={Database} />
         <DistributionCard title="Work Arrangement" data={data.job_distribution.by_mode} icon={PieChart} />
         <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-6">Practice Metrics</h3>
            <div className="grid grid-cols-2 gap-4 h-full pb-8">
               <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 text-center flex flex-col justify-center">
                  <div className="text-2xl font-black text-white">{data.kpis.practice.sessions_completed}</div>
                  <div className="text-[9px] font-black text-slate-500 uppercase">Sessions</div>
               </div>
               <div className="bg-slate-950 p-4 rounded-2xl border border-slate-800 text-center flex flex-col justify-center">
                  <div className="text-2xl font-black text-purple-400">{data.kpis.practice.avg_score}%</div>
                  <div className="text-[9px] font-black text-slate-500 uppercase">Avg Score</div>
               </div>
            </div>
         </div>
      </div>

    </div>
  );
}

function MetricCard({ title, value, sub, icon: Icon, color }: any) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 hover:border-slate-700 transition-all group">
      <div className="flex justify-between items-start mb-4">
        <div className={`p-2 rounded-xl bg-slate-950 border border-slate-800 ${color} group-hover:scale-110 transition-transform`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="space-y-1">
        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{title}</h3>
        <p className="text-3xl font-black text-white">{value}</p>
        <p className="text-[10px] font-bold text-slate-600 italic">{sub}</p>
      </div>
    </div>
  );
}

function DistributionCard({ title, data, icon: Icon }: any) {
  const entries = Object.entries(data || {});
  const total = entries.reduce((a, b: any) => a + b[1], 0);
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
       <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2"><Icon className="w-4 h-4 text-indigo-400" /> {title}</h3>
       <div className="space-y-4">
          {entries.length > 0 ? entries.map(([key, val]: [string, any]) => (
            <div key={key} className="flex items-center justify-between">
               <span className="text-xs font-bold text-slate-300">{key || 'Other'}</span>
               <div className="flex items-center gap-3">
                  <div className="w-32 h-1 bg-slate-950 rounded-full overflow-hidden">
                    <div className="bg-indigo-500 h-full" style={{ width: `${(val / (total || 1)) * 100}%` }} />
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">{val}</span>
               </div>
            </div>
          )) : (
            <p className="text-[10px] text-slate-600 italic py-4">Insufficient data for distribution.</p>
          )}
       </div>
    </div>
  );
}
