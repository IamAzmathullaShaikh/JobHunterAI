import React, { useState, useEffect } from "react";
import { BarChart3, TrendingUp, Target, Activity, Loader2, ArrowUpRight, AlertCircle } from "lucide-react";

export default function AnalyticsDashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchMetrics() {
      try {
        const response = await fetch("/api/tracker/analytics");
        const data = await response.json();
        setMetrics(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchMetrics();
  }, []);

  if (isLoading) {
    return (
      <div className="h-96 flex flex-col items-center justify-center space-y-4 bg-slate-900 border border-slate-800 rounded-3xl">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-slate-500 font-bold uppercase tracking-widest text-[10px]">Aggregating career data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <MetricCard
          title="Total Applied"
          value={metrics?.total_applied || 0}
          icon={TrendingUp}
          color="text-indigo-400"
          sub="Across all platforms"
        />
        <MetricCard
          title="Interview Rate"
          value={`${metrics?.interview_conversion || 0}%`}
          icon={Activity}
          color="text-emerald-400"
          sub="Application to Interview"
        />
        <MetricCard
          title="Avg Match Score"
          value={`${Math.round(metrics?.average_match_score || 0)}%`}
          icon={Target}
          color="text-purple-400"
          sub="JD-Resume alignment"
        />
        <MetricCard
          title="Offer Rate"
          value={`${metrics?.offer_rate || 0}%`}
          icon={ArrowUpRight}
          color="text-amber-400"
          sub="Final stage conversion"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 bg-slate-900 border border-slate-800 rounded-3xl p-6">
           <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">Application Pipeline Distribution</h3>
           <div className="space-y-6">
              {Object.entries(metrics?.status_distribution || {}).map(([status, count]: [string, any]) => (
                <div key={status} className="space-y-2">
                   <div className="flex justify-between items-center text-xs font-bold">
                      <span className="text-slate-300 uppercase tracking-tighter">{status}</span>
                      <span className="text-white">{count} Jobs</span>
                   </div>
                   <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                      <div
                        className="bg-indigo-500 h-full rounded-full transition-all duration-1000"
                        style={{ width: `${(count / (metrics?.total_applied || 1)) * 100}%` }}
                      />
                   </div>
                </div>
              ))}
           </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 flex flex-col">
           <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">Optimization Insights</h3>
           <div className="flex-1 space-y-4">
              <div className="p-4 bg-emerald-500/5 border border-emerald-500/10 rounded-2xl">
                 <p className="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-1">Top Strength</p>
                 <p className="text-xs text-slate-300">Your "Match Score" is consistently above 80% for Backend roles.</p>
              </div>
              <div className="p-4 bg-amber-500/5 border border-amber-500/10 rounded-2xl">
                 <p className="text-[10px] font-black text-amber-400 uppercase tracking-widest mb-1">Skill Gap Alert</p>
                 <p className="text-xs text-slate-300">"Kubernetes" appeared in 40% of missed matches this week.</p>
              </div>
              <div className="p-4 bg-rose-500/5 border border-rose-500/10 rounded-2xl">
                 <p className="text-[10px] font-black text-rose-400 uppercase tracking-widest mb-1">Velocity Warning</p>
                 <p className="text-xs text-slate-300">Daily application volume is down 20% compared to last week.</p>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, color, sub }: any) {
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
