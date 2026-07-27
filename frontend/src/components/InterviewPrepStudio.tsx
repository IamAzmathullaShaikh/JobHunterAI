import React, { useState, useEffect } from "react";
import {
  Brain, Sparkles, Loader2, Send, ChevronRight,
  Target, Award, History, Plus, Trophy, MessageSquare,
  CheckCircle2, XCircle, Wand2, ChevronLeft, FileText
} from "lucide-react";
import { Resume, JobListing, InterviewSession, InterviewQuestion } from "../types.ts";

interface Props {
  resumes: Resume[];
  jobs: JobListing[];
}

export default function InterviewPrepStudio({ resumes, jobs }: Props) {
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [activeSession, setActiveSession] = useState<InterviewSession | null>(null);
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0);
  const [userAnswer, setUserAnswer] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Setup form states
  const [selectedResumeId, setSelectedResumeId] = useState<number | "">("");
  const [selectedJobId, setSelectedJobId] = useState<any>("");
  const [difficulty, setDifficulty] = useState("Senior");

  useEffect(() => {
    async function loadSessions() {
      try {
        const res = await fetch("/api/interview/sessions");
        const data = await res.json();
        setSessions(data);
      } catch (err) { console.error(err); }
    }
    loadSessions();
  }, []);

  const startNewSession = async () => {
    if (!selectedResumeId) return;
    setIsGenerating(true);
    try {
      const selectedJob = jobs.find(j => j.id === selectedJobId);
      const isManual = typeof selectedJobId === 'string' && selectedJobId.startsWith('app-');

      const response = await fetch("/api/interview/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: `Prep: ${selectedJob?.title || difficulty}`,
          resume_id: selectedResumeId,
          job_id: isManual ? null : selectedJobId,
          job_description: isManual ? selectedJob?.description_raw : null,
          difficulty
        })
      });
      const newSession = await response.json();
      // Fetch full session with questions
      const fullRes = await fetch(`/api/interview/sessions/${newSession.id}`);
      const fullSession = await fullRes.json();

      setSessions(prev => [fullSession, ...prev]);
      setActiveSession(fullSession);
      setCurrentQuestionIdx(0);
    } catch (err) { console.error(err); }
    finally { setIsGenerating(false); }
  };

  const submitAnswer = async () => {
    if (!activeSession || !userAnswer.trim()) return;
    const currentQuestion = activeSession.questions?.[currentQuestionIdx];
    if (!currentQuestion) return;

    setIsEvaluating(true);
    try {
      const res = await fetch(`/api/interview/questions/${currentQuestion.id}/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_answer: userAnswer })
      });
      const updatedQuestion = await res.json();

      // Update local state
      const updatedQuestions = [...(activeSession.questions || [])];
      updatedQuestions[currentQuestionIdx] = updatedQuestion;
      setActiveSession({ ...activeSession, questions: updatedQuestions });
      setUserAnswer("");
    } catch (err) { console.error(err); }
    finally { setIsEvaluating(false); }
  };

  const nextQuestion = () => {
    if (activeSession?.questions && currentQuestionIdx < activeSession.questions.length - 1) {
      setCurrentQuestionIdx(currentQuestionIdx + 1);
    }
  };

  const prevQuestion = () => {
    if (currentQuestionIdx > 0) {
      setCurrentQuestionIdx(currentQuestionIdx - 1);
    }
  };

  const finalizeSession = async () => {
    if (!activeSession) return;
    setIsFinalizing(true);
    try {
      const res = await fetch(`/api/interview/sessions/${activeSession.id}/finalize`, { method: "POST" });
      const updated = await res.json();
      setActiveSession(updated);
    } catch (err) { console.error(err); }
    finally { setIsFinalizing(false); }
  };

  const exportSession = async (format: string) => {
    if (!activeSession) return;
    setIsExporting(true);
    try {
      const response = await fetch(`/api/interview/sessions/${activeSession.id}/export`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ format })
      });
      const data = await response.json();
      if (data.success) {
        if (format === "pdf") window.open(data.download_url, "_blank");
        else {
           const blob = new Blob([data.data], { type: 'text/plain' });
           const url = window.URL.createObjectURL(blob);
           const a = document.createElement('a');
           a.href = url;
           a.download = `interview_summary.md`;
           a.click();
        }
      }
    } catch (err) { console.error(err); }
    finally { setIsExporting(false); }
  };

  return (
    <div className="space-y-6 animate-fade-in relative">
      <div className="flex flex-col xl:flex-row gap-6">

        {/* Sidebar: Session History */}
        <div className="xl:w-80 space-y-6 shrink-0">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-2">
                <History className="w-4 h-4 text-purple-400" />
                Prep History
              </h3>
              <button onClick={() => setActiveSession(null)} className="p-1.5 bg-indigo-600 rounded-lg text-white hover:bg-indigo-500 transition-colors">
                <Plus className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1 no-scrollbar">
              {sessions.map(s => (
                <button
                  key={s.id}
                  onClick={async () => {
                    const res = await fetch(`/api/interview/sessions/${s.id}`);
                    setActiveSession(await res.json());
                    setCurrentQuestionIdx(0);
                  }}
                  className={`w-full text-left p-4 rounded-2xl border transition-all ${activeSession?.id === s.id ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg' : 'bg-slate-950/50 border-slate-800 text-slate-400 hover:border-slate-700'}`}
                >
                  <div className="font-bold text-sm truncate">{s.name}</div>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-[10px] font-black uppercase opacity-60">{s.difficulty}</span>
                    <span className="bg-slate-900/50 px-2 py-0.5 rounded text-[10px] font-mono">
                      {new Date(s.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </button>
              ))}
              {sessions.length === 0 && (
                <p className="text-[10px] text-slate-600 italic text-center py-4">No sessions yet. Start your first mock interview!</p>
              )}
            </div>
          </div>

          {activeSession && activeSession.questions && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
               <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Progress</h3>
               <div className="flex flex-wrap gap-2">
                  {activeSession.questions.map((q, i) => (
                    <button
                      key={q.id}
                      onClick={() => setCurrentQuestionIdx(i)}
                      className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs transition-all ${currentQuestionIdx === i ? 'bg-indigo-600 text-white' : q.user_answer ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-950 border border-slate-800 text-slate-600'}`}
                    >
                      {i + 1}
                    </button>
                  ))}
               </div>
            </div>
          )}
        </div>

        {/* Main Interface */}
        <div className="flex-1 bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden flex flex-col min-h-[700px]">
           {!activeSession ? (
             <div className="h-full flex flex-col items-center justify-center p-12 text-center space-y-8">
                <div className="space-y-4">
                  <Brain className="w-16 h-16 text-purple-400 mx-auto opacity-20" />
                  <h2 className="text-2xl font-black text-white uppercase italic">AI Interview Coach</h2>
                  <p className="text-slate-400 text-sm max-w-md mx-auto">Create a persistent interview workspace grounded in your resume and a target job. Practice with real-time AI feedback.</p>
                </div>

                <div className="w-full max-w-xl bg-slate-950/50 border border-slate-800 rounded-3xl p-8 space-y-6 text-left">
                   <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Grounding Resume</label>
                        <select
                          value={selectedResumeId}
                          onChange={e => setSelectedResumeId(Number(e.target.value))}
                          className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none focus:border-indigo-500"
                        >
                          <option value="">Choose a resume...</option>
                          {resumes.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                        </select>
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Target Job</label>
                        <select
                          value={selectedJobId}
                          onChange={e => {
                            const val = e.target.value;
                            setSelectedJobId(val.startsWith('app-') ? val : Number(val));
                          }}
                          className="w-full bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white outline-none focus:border-indigo-500"
                        >
                          <option value="">{jobs.length > 0 ? "Choose from your board..." : "No jobs found. Find jobs in Job Board first."}</option>
                          {jobs.map(j => <option key={j.id} value={j.id}>{j.title} @ {j.company_name}</option>)}
                        </select>
                      </div>
                   </div>

                   <div className="space-y-1">
                      <label className="text-[10px] font-bold text-slate-500 uppercase ml-1">Seniority Level</label>
                      <div className="grid grid-cols-5 gap-2">
                         {["Junior", "Mid", "Senior", "Staff", "Lead"].map(lv => (
                           <button
                             key={lv}
                             onClick={() => setDifficulty(lv)}
                             className={`py-2 rounded-lg border text-[10px] font-black uppercase transition-all ${difficulty === lv ? 'bg-purple-600 border-purple-500 text-white shadow-lg' : 'bg-slate-900 border-slate-800 text-slate-600 hover:border-slate-700'}`}
                           >
                             {lv}
                           </button>
                         ))}
                      </div>
                   </div>

                   <button
                     onClick={startNewSession}
                     disabled={isGenerating || !selectedResumeId || !selectedJobId}
                     className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-black py-4 rounded-2xl flex items-center justify-center gap-3 shadow-lg shadow-indigo-600/20 transition-all uppercase tracking-widest text-sm"
                   >
                     {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                     {isGenerating ? "Preparing Questions..." : "Launch Interview Studio"}
                   </button>
                </div>
             </div>
           ) : activeSession.status === "Completed" ? (
             <div className="flex-1 overflow-y-auto p-8 animate-fade-in">
                <div className="max-w-4xl mx-auto space-y-12">
                   <div className="text-center space-y-4">
                      <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto border border-emerald-500/20">
                         <Trophy className="w-10 h-10 text-emerald-500" />
                      </div>
                      <h2 className="text-3xl font-black text-white uppercase italic">Interview Results</h2>
                      <div className="flex items-center justify-center gap-6">
                         <div className="text-center">
                            <div className="text-4xl font-black text-indigo-400">{Math.round(activeSession.overall_score || 0)}/10</div>
                            <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Overall Score</div>
                         </div>
                         <div className="h-12 w-px bg-slate-800"></div>
                         <div className="text-center">
                            <div className="text-4xl font-black text-white">{activeSession.questions?.length}</div>
                            <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Questions</div>
                         </div>
                      </div>
                   </div>

                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <button onClick={() => exportSession("pdf")} disabled={isExporting} className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 transition-all">
                        {isExporting ? <Loader2 className="w-5 h-5 animate-spin" /> : <FileText className="w-5 h-5 text-rose-400" />}
                        Download PDF Summary
                      </button>
                      <button onClick={() => exportSession("markdown")} className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 transition-all">
                        <FileText className="w-5 h-5 text-emerald-400" />
                        Download Markdown
                      </button>
                   </div>

                   <div className="space-y-6">
                      <h3 className="text-xs font-black text-slate-500 uppercase tracking-[0.2em]">Detailed Analysis</h3>
                      {activeSession.questions?.map((q, i) => (
                        <div key={q.id} className="bg-slate-950/50 border border-slate-800 rounded-3xl p-6 space-y-4">
                           <div className="flex justify-between items-start">
                              <div className="space-y-1">
                                 <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">{q.category}</span>
                                 <h4 className="font-bold text-white text-sm">{q.question_text}</h4>
                              </div>
                              <div className="bg-slate-900 px-3 py-1 rounded-lg border border-slate-800 text-xs font-mono font-black">{Math.round(q.score || 0)}/10</div>
                           </div>
                           <p className="text-xs text-slate-400 italic">"{q.user_answer}"</p>
                           <div className="p-4 bg-indigo-600/5 rounded-xl border border-indigo-500/10 text-[11px] text-slate-300 leading-relaxed">
                              {q.feedback?.suggestions}
                           </div>
                        </div>
                      ))}
                   </div>
                </div>
             </div>
           ) : (
             <>
               <div className="bg-slate-950/50 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <h2 className="text-sm font-black text-white uppercase italic">{activeSession.name}</h2>
                    <span className="bg-purple-600/10 text-purple-400 text-[10px] font-black px-2 py-0.5 rounded border border-purple-500/20">{activeSession.difficulty}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={prevQuestion} disabled={currentQuestionIdx === 0} className="p-2 hover:bg-slate-800 rounded-lg disabled:opacity-30"><ChevronLeft className="w-4 h-4" /></button>
                    <span className="text-xs font-bold text-slate-500">Question {currentQuestionIdx + 1} of {activeSession.questions?.length}</span>
                    <button onClick={nextQuestion} disabled={currentQuestionIdx === (activeSession.questions?.length || 0) - 1} className="p-2 hover:bg-slate-800 rounded-lg disabled:opacity-30"><ChevronRight className="w-4 h-4" /></button>
                  </div>
               </div>

               <div className="flex-1 overflow-y-auto p-8 space-y-8">
                  {/* Current Question Display */}
                  <div className="max-w-3xl mx-auto space-y-8">
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <span className="bg-slate-800 text-slate-400 text-[9px] font-black px-2 py-0.5 rounded uppercase tracking-widest">
                          {activeSession.questions?.[currentQuestionIdx]?.category || "General"}
                        </span>
                      </div>
                      <h3 className="text-2xl font-bold text-white leading-tight">
                        {activeSession.questions?.[currentQuestionIdx]?.question_text}
                      </h3>
                    </div>

                    {!activeSession.questions?.[currentQuestionIdx]?.user_answer ? (
                      <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <textarea
                          value={userAnswer}
                          onChange={e => setUserAnswer(e.target.value)}
                          placeholder="Type your response here. Focus on the STAR method for behavioral questions..."
                          className="w-full h-64 bg-slate-950 border border-slate-800 rounded-3xl p-8 text-sm text-slate-300 outline-none focus:border-indigo-500 transition-all resize-none shadow-inner"
                        />
                        <button
                          onClick={submitAnswer}
                          disabled={isEvaluating || !userAnswer.trim()}
                          className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-black py-4 rounded-2xl flex items-center justify-center gap-3 shadow-lg shadow-indigo-600/20 transition-all uppercase tracking-widest text-sm"
                        >
                          {isEvaluating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                          {isEvaluating ? "Analyzing Response..." : "Submit Answer"}
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-8 animate-in fade-in duration-700">
                        {/* User Answer Card */}
                        <div className="bg-slate-950 border border-slate-800 rounded-3xl p-8 space-y-4 shadow-xl">
                          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                            <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Your Response</h4>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold text-slate-400">SCORE</span>
                              <div className="bg-emerald-500 text-white text-xs font-black w-8 h-8 flex items-center justify-center rounded-lg shadow-lg shadow-emerald-500/20">
                                {Math.round(activeSession.questions?.[currentQuestionIdx]?.score || 0)}
                              </div>
                            </div>
                          </div>
                          <p className="text-sm text-slate-400 italic leading-relaxed">
                            "{activeSession.questions?.[currentQuestionIdx]?.user_answer}"
                          </p>
                        </div>

                        {/* AI Feedback Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                           <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                              <h5 className="text-[9px] font-black text-emerald-400 uppercase tracking-widest flex items-center gap-2"><CheckCircle2 className="w-3 h-3" /> Key Strengths</h5>
                              <ul className="space-y-2">
                                {(activeSession.questions?.[currentQuestionIdx]?.feedback?.strengths || []).map((s: string, i: number) => (
                                  <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                                    <ChevronRight className="w-3 h-3 text-emerald-500 mt-0.5 shrink-0" /> {s}
                                  </li>
                                ))}
                              </ul>
                           </div>
                           <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
                              <h5 className="text-[9px] font-black text-rose-400 uppercase tracking-widest flex items-center gap-2"><XCircle className="w-3 h-3" /> Gaps & Weaknesses</h5>
                              <ul className="space-y-2">
                                {(activeSession.questions?.[currentQuestionIdx]?.feedback?.weaknesses || []).map((w: string, i: number) => (
                                  <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                                    <ChevronRight className="w-3 h-3 text-rose-500 mt-0.5 shrink-0" /> {w}
                                  </li>
                                ))}
                              </ul>
                           </div>
                        </div>

                        {/* Improved Version */}
                        <div className="bg-indigo-600/5 border border-indigo-500/20 rounded-3xl p-8 space-y-6">
                           <div className="flex items-center justify-between">
                              <h4 className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.2em] flex items-center gap-2">
                                <Wand2 className="w-3.5 h-3.5" /> AI Coach Version
                              </h4>
                           </div>
                           <div className="text-sm text-slate-300 leading-relaxed font-sans bg-slate-950/50 p-6 rounded-2xl border border-slate-800">
                             {activeSession.questions?.[currentQuestionIdx]?.improved_answer}
                           </div>
                           <p className="text-[10px] text-slate-500 italic">This version uses the STAR framework to maximize impact and alignment with JD keywords.</p>
                        </div>

                        <div className="flex justify-center pb-8 gap-4">
                           {currentQuestionIdx === (activeSession.questions?.length || 0) - 1 ? (
                             <button onClick={finalizeSession} disabled={isFinalizing} className="bg-emerald-600 hover:bg-emerald-500 text-white font-black py-3 px-12 rounded-2xl flex items-center gap-2 transition-all uppercase text-sm tracking-widest shadow-lg shadow-emerald-600/20">
                                {isFinalizing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Trophy className="w-5 h-5" />}
                                Finalize Session
                             </button>
                           ) : (
                             <button onClick={nextQuestion} className="bg-slate-800 hover:bg-slate-700 text-white font-bold py-3 px-8 rounded-2xl flex items-center gap-2 transition-all text-xs">
                               Continue to Next Question <ChevronRight className="w-4 h-4" />
                             </button>
                           )}
                        </div>
                      </div>
                    )}
                  </div>
               </div>
             </>
           )}
        </div>
      </div>
    </div>
  );
}
