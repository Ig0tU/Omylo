import { useState, useEffect, useRef } from 'react';
import { Terminal, Shield, Cpu, Activity, Send, Database, Layers, Code, CheckCircle2, AlertTriangle, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Reasoning Spiral Component
const ReasoningSpiral = () => {
  return (
    <div className="relative w-full h-64 flex items-center justify-center overflow-hidden bg-black/50 rounded-2xl border border-cybercyan/20 shadow-[0_0_30px_rgba(0,245,255,0.1)]">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="absolute w-56 h-56 border-2 border-dashed border-cybercyan/20 rounded-full"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        className="absolute w-40 h-40 border-2 border-dotted border-mythosgold/30 rounded-full"
      />
      <motion.div
        animate={{
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.6, 0.3]
        }}
        transition={{ duration: 4, repeat: Infinity }}
        className="absolute w-24 h-24 bg-cybercyan/10 rounded-full blur-xl"
      />
      <div className="z-10 text-center">
        <Layers className="w-14 h-14 text-cybercyan mx-auto mb-3 animate-pulse shadow-[0_0_15px_rgba(0,245,255,0.5)]" />
        <p className="text-[10px] font-mono text-cybercyan font-bold uppercase tracking-[0.3em]">Latent Depth Reasoning</p>
        <p className="text-[8px] font-mono text-white/40 mt-1 uppercase">Looping Iterations: 16-64</p>
      </div>
    </div>
  );
};

const LogEntry = ({ log }: { log: any }) => {
  if (log.type === 'AGENT_OUTPUT') {
    const output = log.data.output;
    const fileActionRegex = /\[FILE_ACTION\]\s*(CREATE|MODIFY)\s+(\S+)\s+\[CONTENT\]([\s\S]*?)\[\/CONTENT\]\s*\[\/FILE_ACTION\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = fileActionRegex.exec(output)) !== null) {
      parts.push(<span key={`text-${match.index}`}>{output.substring(lastIndex, match.index)}</span>);
      parts.push(
        <div key={`action-${match.index}`} className="my-6 border border-cybercyan/30 rounded-xl overflow-hidden bg-black/60 shadow-xl">
          <div className="bg-cybercyan/10 px-5 py-3 border-b border-cybercyan/30 flex justify-between items-center">
            <span className="text-xs font-bold flex items-center text-cybercyan uppercase tracking-wider">
              <Code size={14} className="mr-2" /> {match[1]}: {match[2]}
            </span>
            <span className="text-[9px] font-mono text-cybercyan/50 px-2 py-0.5 border border-cybercyan/20 rounded">AUTHORITATIVE</span>
          </div>
          <pre className="p-6 text-xs overflow-x-auto text-white/90 font-mono leading-relaxed bg-[#0a0a0a]">
            {match[3].trim().replace(/\\n/g, '\n')}
          </pre>
        </div>
      );
      lastIndex = fileActionRegex.lastIndex;
    }
    parts.push(<span key="text-end">{output.substring(lastIndex)}</span>);

    return (
      <div className="mb-6 text-left group">
        <div className="text-[10px] font-bold text-cybercyan/60 mb-2 uppercase tracking-[0.2em] flex items-center">
           <Cpu size={12} className="mr-2" /> {log.data.agent} Sub-Matrix Execution
        </div>
        <div className="text-white/80 whitespace-pre-wrap font-sans leading-relaxed border-l-2 border-white/5 pl-4 group-hover:border-cybercyan/30 transition-colors">{parts}</div>
      </div>
    );
  }

  if (log.type === 'SWD_VERIFY_RESULT') {
    const success = log.data.success;
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`mb-6 p-4 rounded-xl border flex items-center space-x-4 ${success ? 'bg-green-500/10 border-green-500/20 shadow-[0_0_20px_rgba(34,197,94,0.05)]' : 'bg-red-500/10 border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.05)]'}`}
      >
        <div className={`p-2 rounded-lg ${success ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
            {success ? <CheckCircle2 size={20} className="text-green-400" /> : <AlertTriangle size={20} className="text-red-400" />}
        </div>
        <div>
          <p className={`text-xs font-bold uppercase tracking-[0.15em] ${success ? 'text-green-400' : 'text-red-400'}`}>
            {success ? 'Strict Write Integrity Verified' : 'Integrity Synchronization Failure'}
          </p>
          <p className="text-[10px] text-white/50 font-mono mt-1">Snapshot: {log.data.path} — {success ? 'SHA-256 Validation Success' : (log.data.error || 'State Drift Detected')}</p>
        </div>
        {success && <Zap size={14} className="ml-auto text-green-500/30" />}
      </motion.div>
    );
  }

  return (
    <div className="mb-4 text-left flex items-start space-x-3 opacity-60 hover:opacity-100 transition-opacity">
      <span className="text-white/30 font-mono text-[9px] mt-1 shrink-0 bg-white/5 px-1.5 py-0.5 rounded">[{log.type}]</span>
      <span className="text-white/70 text-[13px] leading-snug">{typeof log.data === 'string' ? log.data : JSON.stringify(log.data)}</span>
    </div>
  );
};

const App = () => {
  const [task, setTask] = useState('');
  const [logs, setLogs] = useState<{type: string, data: any}[]>([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [stats] = useState({ total_tokens: 0, total_cost: 0, sessions: 0 });
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const port = window.location.port || (window.location.protocol === 'https:' ? '443' : '80');
    const ws = new WebSocket(`${protocol}//${window.location.hostname}:${port}/ws/state`);
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      setLogs((prev) => [...prev, msg]);
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const runTask = async () => {
    if (!task) return;
    await fetch('/api/task/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task }),
    });
    setTask('');
  };

  return (
    <div className="flex h-screen bg-obsidian text-white font-sans overflow-hidden selection:bg-cybercyan/30">
      {/* Sidebar */}
      <aside className="w-24 flex flex-col items-center py-10 border-r border-white/5 space-y-10 bg-black/40 backdrop-blur-xl text-[0px]">
        <div className="w-14 h-14 bg-cybercyan/10 rounded-2xl flex items-center justify-center border border-cybercyan/30 shadow-[0_0_15px_rgba(0,245,255,0.1)]">
          <Cpu className="text-cybercyan w-8 h-8" />
        </div>
        <nav className="flex flex-col space-y-8">
          <button onClick={() => setActiveTab('chat')} className={`p-4 rounded-2xl transition-all duration-300 ${activeTab === 'chat' ? 'bg-cybercyan/20 text-cybercyan shadow-[0_0_20px_rgba(0,245,255,0.15)] scale-110' : 'text-white/30 hover:text-white hover:bg-white/5'}`}>
            <Terminal size={26} />
          </button>
          <button onClick={() => setActiveTab('verify')} className={`p-4 rounded-2xl transition-all duration-300 ${activeTab === 'verify' ? 'bg-mythosgold/20 text-mythosgold shadow-[0_0_20px_rgba(212,175,55,0.15)] scale-110' : 'text-white/30 hover:text-white hover:bg-white/5'}`}>
            <Shield size={26} />
          </button>
          <button onClick={() => setActiveTab('memory')} className={`p-4 rounded-2xl transition-all duration-300 ${activeTab === 'memory' ? 'bg-white/10 text-white scale-110' : 'text-white/30 hover:text-white hover:bg-white/5'}`}>
            <Database size={26} />
          </button>
        </nav>
        <div className="mt-auto pb-4">
          <Activity className="text-cybercyan w-6 h-6 animate-pulse opacity-40" />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden p-10 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-cybercyan/5 via-transparent to-transparent">
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-3xl font-black tracking-[.25em] text-white uppercase italic">OPEN<span className="text-cybercyan not-italic">MYTHOS</span></h1>
            <div className="flex items-center mt-2 space-x-3 text-left">
                <span className="w-2 h-2 rounded-full bg-cybercyan animate-ping" />
                <p className="text-[10px] font-mono text-white/40 uppercase tracking-[0.4em]">Recurrent Depth Orchestrator <span className="text-white/60">v0.5.0</span></p>
            </div>
          </div>
          <div className="flex space-x-6 text-left">
            <div className="px-6 py-3 bg-black/40 rounded-xl border border-white/10 backdrop-blur-md">
              <p className="text-[9px] text-white/30 uppercase font-black tracking-widest mb-1">Compute Capacity</p>
              <p className="text-lg font-mono text-cybercyan">84.2<span className="text-xs ml-1 opacity-60">TFLOPS</span></p>
            </div>
            <div className="px-6 py-3 bg-black/40 rounded-xl border border-white/10 backdrop-blur-md">
              <p className="text-[9px] text-white/30 uppercase font-black tracking-widest mb-1">Network Latency</p>
              <p className="text-lg font-mono text-mythosgold">{stats.total_tokens > 0 ? '12' : '0'}<span className="text-xs ml-1 opacity-60">MS</span></p>
            </div>
          </div>
        </header>

        <div className="flex-1 flex space-x-10 overflow-hidden">
          {/* Left Column: Command & Logs */}
          <div className="flex-1 flex flex-col space-y-8 overflow-hidden">
            {/* Log Terminal */}
            <div className="flex-1 bg-black/60 rounded-[2rem] border border-white/5 p-10 overflow-y-auto relative shadow-2xl backdrop-blur-sm scrollbar-hide">
              <div className="sticky top-0 z-20 flex justify-between items-center mb-6 pointer-events-none">
                  <div className="bg-cybercyan/10 px-3 py-1 rounded-full border border-cybercyan/20 backdrop-blur-md">
                    <p className="text-[9px] text-cybercyan font-bold uppercase tracking-widest animate-pulse">Live Matrix Stream</p>
                  </div>
              </div>
              <AnimatePresence initial={false}>
                {logs.map((log, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ type: "spring", damping: 25, stiffness: 200 }}
                  >
                    <LogEntry log={log} />
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={logEndRef} />
            </div>

            {/* Input Area */}
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-cybercyan/20 to-mythosgold/20 rounded-[2.5rem] blur opacity-25 group-focus-within:opacity-100 transition duration-1000"></div>
              <input
                type="text"
                value={task}
                onChange={(e) => setTask(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && runTask()}
                placeholder="Synchronize with latent space..."
                className="relative w-full bg-black/80 border border-white/10 rounded-[2rem] py-6 pl-10 pr-20 focus:outline-none focus:border-cybercyan/50 transition-all text-white placeholder-white/20 text-lg shadow-2xl backdrop-blur-xl"
              />
              <button
                onClick={runTask}
                className="absolute right-5 top-1/2 -translate-y-1/2 bg-cybercyan text-obsidian p-4 rounded-2xl hover:scale-105 active:scale-95 transition-all shadow-[0_0_20px_rgba(0,245,255,0.4)] group-hover:shadow-[0_0_30px_rgba(0,245,255,0.6)]"
              >
                <Send size={28} strokeWidth={2.5} />
              </button>
            </div>
          </div>

          {/* Right Column: Visualization */}
          <div className="w-96 flex flex-col space-y-8">
            <ReasoningSpiral />

            <div className="flex-1 bg-black/60 rounded-[2rem] border border-white/5 p-8 overflow-hidden flex flex-col shadow-2xl backdrop-blur-sm text-left">
              <h3 className="text-[11px] font-black text-white/30 uppercase mb-8 flex items-center font-mono tracking-[0.3em]">
                <Activity size={16} className="mr-3 text-cybercyan" /> Matrix Topology
              </h3>
              <div className="flex-1 flex flex-col justify-center items-center space-y-6">
                <div className="w-24 h-24 rounded-[2rem] bg-cybercyan/10 border-2 border-cybercyan flex items-center justify-center relative rotate-45 shadow-[0_0_30px_rgba(0,245,255,0.2)]">
                   <div className="absolute inset-0 bg-cybercyan/20 rounded-[1.8rem] animate-ping" />
                   <span className="text-[11px] font-black text-cybercyan text-center -rotate-45 leading-none">GOD<br/>ORCH</span>
                </div>
                <div className="w-0.5 h-16 bg-gradient-to-b from-cybercyan to-transparent opacity-20" />
                <div className="flex space-x-8">
                   <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group hover:border-cybercyan/50 transition-all duration-500 hover:shadow-[0_0_20px_rgba(0,245,255,0.1)]">
                     <span className="text-[10px] text-white/30 group-hover:text-cybercyan transition-colors font-black tracking-tighter">PLAN</span>
                   </div>
                   <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group hover:border-cybercyan/50 transition-all duration-500 hover:shadow-[0_0_20px_rgba(0,245,255,0.1)]">
                     <span className="text-[10px] text-white/30 group-hover:text-cybercyan transition-colors font-black tracking-tighter">CODE</span>
                   </div>
                </div>
              </div>
              <div className="mt-8 pt-8 border-t border-white/5">
                <div className="flex justify-between text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2">
                    <span>Matrix Density</span>
                    <span className="text-cybercyan">0.82</span>
                </div>
                <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: "82%" }}
                        className="h-full bg-cybercyan shadow-[0_0_10px_rgba(0,245,255,0.8)]"
                    />
                </div>
              </div>
            </div>

            <div className="bg-mythosgold/5 rounded-[2rem] border border-mythosgold/20 p-8 shadow-2xl backdrop-blur-sm text-left">
               <div className="flex justify-between items-center mb-4">
                    <h3 className="text-[11px] font-black text-mythosgold uppercase font-mono tracking-[0.3em]">Integrity</h3>
                    <div className="w-2 h-2 rounded-full bg-mythosgold animate-pulse shadow-[0_0_10px_rgba(212,175,55,1)]" />
               </div>
               <div className="bg-black/60 p-5 rounded-2xl border border-mythosgold/10">
                 <p className="text-[10px] font-mono text-mythosgold/80 uppercase tracking-[0.2em] font-bold">SWD Surveillance Active</p>
                 <p className="text-[9px] text-white/40 mt-1 uppercase font-mono">Zero Drift Policy Enabled</p>
               </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
