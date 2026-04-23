import { useState, useEffect, useRef } from 'react';
import { Terminal, Shield, Cpu, Activity, Send, Database, Layers, Code, CheckCircle2, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Mocked Reasoning Spiral Component
const ReasoningSpiral = () => {
  return (
    <div className="relative w-full h-64 flex items-center justify-center overflow-hidden bg-black/50 rounded-xl border border-cybercyan/20">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        className="absolute w-48 h-48 border-4 border-dashed border-cybercyan/30 rounded-full"
      />
      <motion.div
        animate={{ rotate: -360 }}
        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
        className="absolute w-32 h-32 border-4 border-dotted border-mythosgold/40 rounded-full"
      />
      <div className="z-10 text-center">
        <Layers className="w-12 h-12 text-cybercyan mx-auto mb-2 animate-pulse" />
        <p className="text-xs font-mono text-cybercyan/80 uppercase tracking-widest">Latent Thinking Loop</p>
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
        <div key={`action-${match.index}`} className="my-4 border border-cybercyan/30 rounded-lg overflow-hidden bg-cybercyan/5">
          <div className="bg-cybercyan/10 px-4 py-2 border-b border-cybercyan/30 flex justify-between items-center">
            <span className="text-xs font-bold flex items-center text-cybercyan">
              <Code size={14} className="mr-2" /> {match[1]}: {match[2]}
            </span>
          </div>
          <pre className="p-4 text-xs overflow-x-auto text-white/90 font-mono">
            {match[3].trim()}
          </pre>
        </div>
      );
      lastIndex = fileActionRegex.lastIndex;
    }
    parts.push(<span key="text-end">{output.substring(lastIndex)}</span>);

    return (
      <div className="mb-4 text-left">
        <div className="text-xs font-bold text-cybercyan/60 mb-1 uppercase tracking-tighter flex items-center">
           <Cpu size={12} className="mr-1" /> {log.data.agent} Response
        </div>
        <div className="text-white/80 whitespace-pre-wrap">{parts}</div>
      </div>
    );
  }

  if (log.type === 'SWD_VERIFY_RESULT') {
    const success = log.data.success;
    return (
      <div className={`mb-4 p-3 rounded-lg border flex items-center space-x-3 ${success ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
        {success ? <CheckCircle2 size={18} className="text-green-500" /> : <AlertTriangle size={18} className="text-red-500" />}
        <div>
          <p className="text-xs font-bold uppercase tracking-widest">{success ? 'Integrity Verified' : 'Integrity Breach'}</p>
          <p className="text-[10px] text-white/60 font-mono">{log.data.path} - SHA-256 Match</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-3 text-left">
      <span className="text-white/40 font-mono text-[10px] mr-2">[{log.type}]</span>
      <span className="text-white/60">{typeof log.data === 'string' ? log.data : JSON.stringify(log.data)}</span>
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
    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws/state`);
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
    <div className="flex h-screen bg-obsidian text-white font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-20 flex flex-col items-center py-8 border-r border-white/5 space-y-8 bg-black/20">
        <div className="w-12 h-12 bg-cybercyan/10 rounded-xl flex items-center justify-center border border-cybercyan/20">
          <Cpu className="text-cybercyan w-8 h-8" />
        </div>
        <nav className="flex flex-col space-y-6">
          <button onClick={() => setActiveTab('chat')} className={`p-3 rounded-xl transition-colors ${activeTab === 'chat' ? 'bg-cybercyan/20 text-cybercyan' : 'text-white/40 hover:text-white'}`}>
            <Terminal size={24} />
          </button>
          <button onClick={() => setActiveTab('verify')} className={`p-3 rounded-xl transition-colors ${activeTab === 'verify' ? 'bg-mythosgold/20 text-mythosgold' : 'text-white/40 hover:text-white'}`}>
            <Shield size={24} />
          </button>
          <button onClick={() => setActiveTab('memory')} className={`p-3 rounded-xl transition-colors ${activeTab === 'memory' ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white'}`}>
            <Database size={24} />
          </button>
        </nav>
        <div className="mt-auto">
          <Activity className="text-cybercyan/30 w-6 h-6 animate-pulse" />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden p-8">
        <header className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold tracking-tighter text-white/90 uppercase">OpenMythos <span className="text-cybercyan">Latent UI</span></h1>
            <p className="text-xs font-mono text-white/30 uppercase">Recurrent Depth Orchestrator v0.5.0</p>
          </div>
          <div className="flex space-x-4 text-left">
            <div className="px-4 py-2 bg-white/5 rounded-lg border border-white/10">
              <p className="text-[10px] text-white/40 uppercase font-bold">Total Tokens</p>
              <p className="text-sm font-mono text-cybercyan">{stats.total_tokens.toLocaleString()}</p>
            </div>
            <div className="px-4 py-2 bg-white/5 rounded-lg border border-white/10">
              <p className="text-[10px] text-white/40 uppercase font-bold">Cost</p>
              <p className="text-sm font-mono text-mythosgold">${stats.total_cost.toFixed(4)}</p>
            </div>
          </div>
        </header>

        <div className="flex-1 flex space-x-8 overflow-hidden">
          {/* Left Column: Command & Logs */}
          <div className="flex-1 flex flex-col space-y-6 overflow-hidden">
            {/* Log Terminal */}
            <div className="flex-1 bg-black/40 rounded-2xl border border-white/5 p-8 overflow-y-auto font-sans text-sm relative">
              <div className="absolute top-4 right-4 text-[10px] text-cybercyan/40 uppercase animate-pulse font-mono">Live Stream Active</div>
              <AnimatePresence>
                {logs.map((log, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <LogEntry log={log} />
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={logEndRef} />
            </div>

            {/* Input Area */}
            <div className="relative group">
              <input
                type="text"
                value={task}
                onChange={(e) => setTask(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && runTask()}
                placeholder="Initialize task sequence..."
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-5 pl-8 pr-16 focus:outline-none focus:border-cybercyan/50 transition-all text-white placeholder-white/20 shadow-2xl"
              />
              <button
                onClick={runTask}
                className="absolute right-4 top-1/2 -translate-y-1/2 bg-cybercyan text-obsidian p-3 rounded-xl hover:scale-105 active:scale-95 transition-transform shadow-lg"
              >
                <Send size={24} />
              </button>
            </div>
          </div>

          {/* Right Column: Visualization */}
          <div className="w-80 flex flex-col space-y-6">
            <ReasoningSpiral />

            <div className="flex-1 bg-black/40 rounded-2xl border border-white/5 p-6 overflow-hidden flex flex-col">
              <h3 className="text-xs font-bold text-white/40 uppercase mb-6 flex items-center font-mono tracking-widest">
                <Activity size={14} className="mr-2 text-cybercyan" /> Agent Hive
              </h3>
              <div className="flex-1 flex flex-col justify-center items-center space-y-4">
                <div className="w-20 h-20 rounded-full bg-cybercyan/10 border border-cybercyan flex items-center justify-center relative">
                   <div className="absolute inset-0 bg-cybercyan/20 rounded-full animate-ping" />
                   <span className="text-[10px] font-bold text-cybercyan text-center z-10">MASTER<br/>ORCH</span>
                </div>
                <div className="w-1 px-4 h-12 border-r border-dashed border-white/10" />
                <div className="flex space-x-6">
                   <div className="w-14 h-14 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group hover:border-cybercyan/50 transition-colors">
                     <span className="text-[10px] text-white/40 group-hover:text-cybercyan transition-colors">PLAN</span>
                   </div>
                   <div className="w-14 h-14 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group hover:border-cybercyan/50 transition-colors">
                     <span className="text-[10px] text-white/40 group-hover:text-cybercyan transition-colors">CODE</span>
                   </div>
                </div>
              </div>
            </div>

            <div className="bg-mythosgold/5 rounded-2xl border border-mythosgold/20 p-6">
               <h3 className="text-xs font-bold text-mythosgold uppercase mb-3 font-mono tracking-widest">Integrity Gate</h3>
               <div className="flex items-center space-x-3 bg-black/40 p-3 rounded-lg border border-mythosgold/10">
                 <div className="w-2 h-2 rounded-full bg-mythosgold animate-pulse" />
                 <p className="text-[10px] font-mono text-mythosgold/80 uppercase tracking-widest">SWD ACTIVE</p>
               </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;
