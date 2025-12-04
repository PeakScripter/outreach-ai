import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Activity, Search, Users, PhoneCall, Send, Route, Shield, Sparkles, LayoutDashboard, FileText, CheckCircle2 } from 'lucide-react';

// Use environment variable for API URL so it works both locally and on Vercel
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  // --- EXACT LOGIC START (No Changes) ---
  const [signals, setSignals] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [activeChannel, setActiveChannel] = useState('email'); // 'email' | 'linkedin' | 'call'
  const scorecard = result?.scorecard ?? {};
  const research = result?.research ?? {};
  const assets = result?.assets ?? {};
  const routing = result?.routing ?? {};
  const decisionMakers = research.decision_makers ?? [];

  useEffect(() => {
    axios.get(`${API_URL}/signals`).then(res => setSignals(res.data));
  }, []);

  const handleGenerate = async (lead) => {
    setProcessing(true);
    setSelectedLead(lead);
    setResult(null); 

    try {
      const res = await axios.post(`${API_URL}/process-lead`, {
        company: lead.company,
        signal: lead.signal
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
    }
    setProcessing(false);
  };
  // --- EXACT LOGIC END ---

  const currentDraft =
    activeChannel === 'email'
      ? assets.email
      : activeChannel === 'linkedin'
      ? assets.linkedin
      : assets.call_script;

  const handleCopyDraft = () => {
    if (!currentDraft) return;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(currentDraft).catch(() => {});
    }
  };

  // --- NEW UI (Professional B2B Look) ---
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col">
      
      {/* HEADER: Standard SaaS Toolbar */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-1.5 rounded-lg">
            <LayoutDashboard className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight">AutoReach</h1>
            <p className="text-xs text-slate-500 font-medium">Enterprise Outreach</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-medium flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
            System Operational
          </span>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        
        {/* SIDEBAR: List View */}
        <aside className="w-96 bg-white border-r border-slate-200 flex flex-col overflow-y-auto">
          <div className="p-4 border-b border-slate-100 bg-slate-50/50">
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4" /> Incoming Signals
            </h2>
          </div>
          
          <div className="p-3 space-y-3">
            {signals.map((lead) => (
              <div 
                key={lead.id} 
                onClick={() => handleGenerate(lead)}
                className={`
                  p-4 rounded-xl border cursor-pointer transition-all duration-200
                  ${selectedLead?.id === lead.id 
                    ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-200 shadow-sm' 
                    : 'bg-white border-slate-200 hover:border-indigo-300 hover:shadow-sm'
                  }
                `}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className={`font-semibold text-sm ${selectedLead?.id === lead.id ? 'text-indigo-900' : 'text-slate-800'}`}>
                    {lead.company}
                  </h3>
                  <span className="text-xs text-slate-400 font-mono">{lead.time}</span>
                </div>
                <p className="text-xs text-slate-600 mb-3 line-clamp-2">{lead.signal}</p>
                
                <button 
                  onClick={(e) => { e.stopPropagation(); handleGenerate(lead); }}
                  disabled={processing}
                  className={`
                    w-full py-1.5 text-xs font-medium rounded-lg border transition-colors flex items-center justify-center gap-2
                    ${selectedLead?.id === lead.id 
                      ? 'bg-indigo-600 text-white border-indigo-600 hover:bg-indigo-700' 
                      : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                    }
                  `}
                >
                  {processing && selectedLead?.id === lead.id ? "Processing..." : "Generate Outreach"}
                </button>
              </div>
            ))}
          </div>
        </aside>

        {/* MAIN CANVAS: Workspace */}
        <section className="flex-1 overflow-y-auto bg-slate-50 p-8">
          {!result && !processing && (
            <div className="h-full flex flex-col items-center justify-center text-slate-400">
              <div className="w-16 h-16 bg-white rounded-full shadow-sm border border-slate-200 flex items-center justify-center mb-4">
                <Search className="w-8 h-8 text-slate-300" />
              </div>
              <p className="text-sm font-medium">Select a lead to initialize workspace</p>
            </div>
          )}

          {(processing || result) && (
            <div className="max-w-4xl mx-auto space-y-6">
              
              {/* STATUS BAR (Replaces the "Terminal") */}
              <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-3">System Status</p>
                <div className="space-y-2 h-32 overflow-y-auto font-mono text-xs">
                  {processing && !result ? (
                     <div className="flex items-center gap-2 text-indigo-600">
                        <span className="w-2 h-2 bg-indigo-600 rounded-full animate-pulse"></span>
                        Running analysis on {selectedLead.company}...
                     </div>
                  ) : (
                    result?.logs.map((log, i) => (
                      <div key={i} className="flex items-center gap-2 text-slate-600 border-b border-slate-50 last:border-0 pb-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                        {log}
                      </div>
                    ))
                  )}
                </div>
              </div>

              {result && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-500 space-y-6">
                  
                  {/* METRICS ROW */}
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                      <p className="text-xs font-bold text-slate-400 uppercase">Lead Score</p>
                      <div className="flex items-end gap-2 mt-2">
                        <span className={`text-3xl font-bold ${result.score > 70 ? 'text-emerald-600' : 'text-amber-500'}`}>
                          {result.score}
                        </span>
                        <span className="text-sm text-slate-400 mb-1">/ 100</span>
                      </div>
                      <div className="mt-2 text-xs text-slate-500 font-medium">
                         {scorecard.intent_level} Intent
                      </div>
                    </div>

                    <div className="col-span-2 bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                      <p className="text-xs font-bold text-slate-400 uppercase">Recommendation</p>
                      <div className="flex items-start gap-3 mt-3">
                         <div className="bg-indigo-50 p-2 rounded-md">
                           <Route className="w-5 h-5 text-indigo-600" />
                         </div>
                         <div>
                            <p className="font-semibold text-slate-900">{scorecard.next_best_action}</p>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {scorecard.reasons?.map((reason) => (
                                <span key={reason} className="text-[10px] bg-slate-100 text-slate-600 px-2 py-1 rounded border border-slate-200 font-medium">
                                  {reason}
                                </span>
                              ))}
                            </div>
                         </div>
                      </div>
                    </div>
                  </div>

                  {/* RESEARCH CARD */}
                  <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
                    <div className="bg-slate-50 px-5 py-3 border-b border-slate-200">
                      <h3 className="text-sm font-bold text-slate-700 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-slate-400" /> Research Summary
                      </h3>
                    </div>
                    <div className="p-5">
                      <p className="text-sm text-slate-600 leading-relaxed mb-6">{research.summary}</p>
                      
                      <div className="grid md:grid-cols-2 gap-8">
                        <div>
                          <p className="text-xs font-bold text-slate-400 uppercase mb-3">Pain Points</p>
                          <ul className="space-y-2">
                            {research.pain_points?.map((pain) => (
                              <li key={pain} className="flex items-start gap-2 text-sm text-slate-700">
                                <Shield className="w-4 h-4 text-red-400 mt-0.5" /> {pain}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-400 uppercase mb-3">Opportunities</p>
                          <ul className="space-y-2">
                            {research.opportunities?.map((opp) => (
                              <li key={opp} className="flex items-start gap-2 text-sm text-slate-700">
                                <Sparkles className="w-4 h-4 text-amber-400 mt-0.5" /> {opp}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* PEOPLE */}
                  <div className="bg-white border border-slate-200 rounded-lg shadow-sm p-5">
                    <h3 className="text-sm font-bold text-slate-700 flex items-center gap-2 mb-4">
                      <Users className="w-4 h-4 text-slate-400" /> Key Decision Makers
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {decisionMakers.map((contact) => (
                        <div key={contact.email} className="p-3 bg-slate-50 rounded border border-slate-100 flex items-start justify-between">
                          <div>
                            <p className="font-semibold text-sm text-slate-900">{contact.name}</p>
                            <p className="text-xs text-slate-500">{contact.title}</p>
                          </div>
                          <span className="text-[10px] bg-white px-2 py-1 rounded border border-slate-200 text-slate-400">
                            Verified
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* GENERATED ASSETS */}
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-white border border-slate-200 rounded-lg shadow-sm p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-bold text-slate-900 flex items-center gap-2">
                          <Send className="w-4 h-4 text-indigo-600" /> Outreach Drafts
                        </h3>
                        <div className="flex items-center gap-2">
                          <div className="inline-flex rounded-full bg-slate-100 p-1 text-xs">
                            <button
                              className={`px-3 py-1 rounded-full ${
                                activeChannel === 'email'
                                  ? 'bg-indigo-600 text-white'
                                  : 'text-slate-600'
                              }`}
                              onClick={() => setActiveChannel('email')}
                            >
                              Email
                            </button>
                            <button
                              className={`px-3 py-1 rounded-full ${
                                activeChannel === 'linkedin'
                                  ? 'bg-indigo-600 text-white'
                                  : 'text-slate-600'
                              }`}
                              onClick={() => setActiveChannel('linkedin')}
                            >
                              LinkedIn
                            </button>
                            <button
                              className={`px-3 py-1 rounded-full ${
                                activeChannel === 'call'
                                  ? 'bg-indigo-600 text-white'
                                  : 'text-slate-600'
                              }`}
                              onClick={() => setActiveChannel('call')}
                            >
                              Call Script
                            </button>
                          </div>
                          <button
                            onClick={handleCopyDraft}
                            className="text-xs bg-white border border-slate-200 px-3 py-1 rounded shadow-sm text-slate-600 hover:text-indigo-600"
                          >
                            Copy Draft
                          </button>
                        </div>
                      </div>
                      <div className="bg-slate-50 p-4 rounded border border-slate-100 min-h-[160px] text-sm text-slate-700 leading-relaxed prose prose-slate max-w-none">
                        <ReactMarkdown>
                          {currentDraft || 'No draft available for this channel.'}
                        </ReactMarkdown>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm">
                        <h3 className="text-xs font-bold text-slate-400 uppercase mb-2 flex items-center gap-2">
                           <Route className="w-4 h-4" /> Routing Info
                        </h3>
                        <div className="space-y-3 text-sm">
                           <div className="flex justify-between border-b border-slate-50 pb-2">
                              <span className="text-slate-500">Owner</span>
                              <span className="font-medium text-slate-900">{routing.recommended_owner}</span>
                           </div>
                           <div className="flex justify-between border-b border-slate-50 pb-2">
                              <span className="text-slate-500">Priority</span>
                              <span className="font-medium text-red-600 bg-red-50 px-2 rounded-full text-xs py-0.5">{routing.priority}</span>
                           </div>
                           <div className="flex justify-between">
                              <span className="text-slate-500">CRM Target</span>
                              <span className="font-medium text-slate-900">{routing.crm_target}</span>
                           </div>
                        </div>
                      </div>

                      <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-4">
                        <p className="text-xs font-bold text-indigo-800 uppercase mb-1">Agent Note</p>
                        <p className="text-sm text-indigo-900">{routing.notes}</p>
                      </div>
                    </div>
                  </div>

                </div>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}