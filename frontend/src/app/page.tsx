"use client";

import React, { useState, useEffect } from "react";
import { 
  Droplet, 
  Moon, 
  Activity, 
  Utensils, 
  BookOpen, 
  Smartphone, 
  Smile, 
  Sparkles, 
  Footprints, 
  CheckCircle2, 
  Server, 
  Database, 
  Cpu, 
  ArrowRight,
  ShieldCheck,
  RefreshCw
} from "lucide-react";

interface ModuleCard {
  title: string;
  category: string;
  metric: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  color: string;
  tag: string;
}

const MODULES: ModuleCard[] = [
  {
    title: "Water Intake",
    category: "Physical Health",
    metric: "2,500 ml target",
    icon: Droplet,
    description: "Real-time hydration logging, reminder intervals, and daily volume targets.",
    color: "from-blue-500/20 to-cyan-500/20 text-cyan-400 border-cyan-500/30",
    tag: "Tracker #1",
  },
  {
    title: "Sleep & Recovery",
    category: "Rest",
    metric: "8.0 hrs target",
    icon: Moon,
    description: "Bedtime, wake cycles, sleep duration, disruption count, and subjective quality rating (1-5).",
    color: "from-indigo-500/20 to-purple-500/20 text-indigo-400 border-indigo-500/30",
    tag: "Tracker #2",
  },
  {
    title: "Exercise & Fitness",
    category: "Physical Health",
    metric: "45 mins / day",
    icon: Activity,
    description: "Workout classification, perceived exertion scale (RPE 1-10), and caloric expenditure.",
    color: "from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30",
    tag: "Tracker #3",
  },
  {
    title: "Food & Nutrition",
    category: "Physical Health",
    metric: "Mindful Meals",
    icon: Utensils,
    description: "Meal timing, nutritional density rating, hunger markers, and mindful eating habits.",
    color: "from-amber-500/20 to-orange-500/20 text-amber-400 border-amber-500/30",
    tag: "Tracker #4",
  },
 
  
  {
    title: "Mood & Wellbeing",
    category: "Mind & Focus",
    metric: "1-10 Scale",
    icon: Smile,
    description: "Emotional valence, energy rating, contextual trigger tags, and reflective notes.",
    color: "from-violet-500/20 to-fuchsia-500/20 text-fuchsia-400 border-fuchsia-500/30",
    tag: "Tracker #5",
  },
 

];

export default function HomePage() {
  const [backendStatus, setBackendStatus] = useState<"checking" | "connected" | "offline">("checking");
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [waterConsumed, setWaterConsumed] = useState(0);
  const [sleepHours, setSleepHours] = useState(0);
  const [exerciseMinutes, setExerciseMinutes] = useState(0);
  const [mealsLogged, setMealsLogged] = useState(0);
  const [mood, setMood] = useState("");
  const [backendData, setBackendData] = useState<any>(null);

  const checkBackendHealth = async () => {
    setBackendStatus("checking");
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/health", {
        headers: { "Content-Type": "application/json" },
      });
      if (res.ok) {
        const data = await res.json();
        setBackendData(data);
        setBackendStatus("connected");
      } else {
        setBackendStatus("offline");
      }
    } catch {
      setBackendStatus("offline");
    }
  };

  useEffect(() => {
    checkBackendHealth();
  }, []);

  return (
    <main className="min-h-screen bg-[#070b14] text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-[#090e1c]/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center font-bold text-slate-950 text-xl shadow-lg shadow-emerald-500/20">
              V
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-white">Vita<span className="text-emerald-400">Sync</span></span>
              <span className="hidden sm:inline-block ml-3 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 rounded-full border border-emerald-500/20">
                Phase 1: Foundation
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-xs px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800">
              <span className={`h-2 w-2 rounded-full ${backendStatus === "connected" ? "bg-emerald-400 animate-pulse" : backendStatus === "checking" ? "bg-amber-400" : "bg-rose-500"}`} />
              <span className="text-slate-400">Python API:</span>
              <span className={backendStatus === "connected" ? "text-emerald-400 font-medium" : "text-slate-400"}>
                {backendStatus === "connected" ? "Online (Port 8000)" : backendStatus === "checking" ? "Connecting..." : "Offline (Start Uvicorn)"}
              </span>
              <button 
                onClick={checkBackendHealth} 
                title="Refresh backend status"
                className="ml-1 text-slate-400 hover:text-white transition-colors"
              >
                <RefreshCw className="h-3 w-3" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 px-4 sm:px-6 lg:px-8 border-b border-slate-800/60 bg-gradient-to-b from-[#090e1c] to-[#070b14]">
        <div className="max-w-5xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300 font-medium">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
            <span>Lifestyle Tracking • Health Data Privacy • Google Gemini AI Recommendations</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Sync Your Lifestyle With <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
              Better Habits
            </span>
          </h1>

          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            A comprehensive lifestyle and habit-management architecture unifying 9 daily wellness dimensions with cross-metric statistical correlation and personalized AI-driven habit coaching.
          </p>

          {/* Architecture Status Badges */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6 max-w-3xl mx-auto text-left">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="flex items-center space-x-2 text-cyan-400 font-medium text-sm mb-1">
                <Server className="h-4 w-4" />
                <span>Next.js 15 + TypeScript</span>
              </div>
              <p className="text-xs text-slate-400">Presentation, UI widgets, responsive cockpit & client caching.</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="flex items-center space-x-2 text-emerald-400 font-medium text-sm mb-1">
                <Cpu className="h-4 w-4" />
                <span>Python FastAPI</span>
              </div>
              <p className="text-xs text-slate-400">Core business logic, multi-metric correlation & Google Gemini AI service.</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
              <div className="flex items-center space-x-2 text-indigo-400 font-medium text-sm mb-1">
                <Database className="h-4 w-4" />
                <span>Supabase PostgreSQL</span>
              </div>
              <p className="text-xs text-slate-400">13 relational tables, Row Level Security (RLS), and time-series indexes.</p>
            </div>
          </div>
        </div>
      </section>

      {/* 9 Core Tracking Modules Grid */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex-1 w-full">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">The 9 Lifestyle Dimensions</h2>
            <p className="text-sm text-slate-400 mt-1">Foundational data schema configured and ready for ingestion.</p>
          </div>
          <div className="flex items-center space-x-2 text-xs text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20">
            <CheckCircle2 className="h-4 w-4" />
            <span>Database migrations prepared in /supabase/migrations</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {MODULES.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div 
                key={idx}
                onClick={() => setSelectedModule(item.title)}  
                className="group relative p-5 rounded-2xl bg-[#0b101f] border border-slate-800/80 hover:border-slate-700 transition-all duration-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                      {item.category}
                    </span>
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {item.tag}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 mb-3">
                    <div className={`p-2.5 rounded-xl border bg-gradient-to-br ${item.color}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white group-hover:text-emerald-400 transition-colors">
                        {item.title}
                      </h3>
                      <p className="text-xs text-slate-400">{item.metric}</p>
                    </div>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed">
                    {item.description}
                  </p>
                </div>

                <div className="pt-4 mt-4 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                  <span>Schema: <code className="text-slate-300 font-mono text-[11px]">public.{item.title.toLowerCase().replace(/[^a-z0-9]/g, "_")}_logs</code></span>
                  <span className="text-slate-500 group-hover:text-slate-300 transition-colors">
                    <ArrowRight className="h-3.5 w-3.5" />
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {selectedModule && (
  <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4">
    <div className="w-full max-w-md rounded-2xl border border-slate-700 bg-[#0b101f] p-6">
      <h2 className="text-2xl font-bold text-white">{selectedModule}</h2>

      {selectedModule === "Water Intake" ? (
        <div className="mt-5 text-slate-300">
          <p>💧 Daily target: 2500 ml</p>
          <p className="mt-2">Water consumed: {waterConsumed} ml</p>

          {waterConsumed < 1250 && (
            <p className="mt-2 text-sm text-amber-400">
              ⚠️ You are below your daily water target. Keep drinking water.
            </p>
          )}

          {waterConsumed >= 2500 && (
            <p className="mt-2 text-sm text-emerald-400">
              🎉 Great job! You reached your daily water target.
            </p>
          )}

          <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-slate-700">
            <div
              className="h-full rounded-full bg-cyan-400 transition-all"
              style={{
                width: `${Math.min((waterConsumed / 2500) * 100, 100)}%`,
              }}
            />
          </div>

          <p className="mt-2 text-sm text-slate-400">
            Daily target: 2500 ml
          </p>

          <button
            onClick={() => setWaterConsumed((prev) => prev + 250)}
            className="mt-4 rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-slate-950"
          >
            + Add Water
          </button>
        </div>
      ) : selectedModule === "Sleep & Recovery" ? (
        <div className="mt-5 text-slate-300">
          <p>😴 Daily target: 8 hours</p>
          <p className="mt-2">Sleep duration: {sleepHours} hours</p>

          <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-slate-700">
            <div
              className="h-full rounded-full bg-indigo-400"
              style={{ width: `${Math.min((sleepHours / 8) * 100, 100)}%` }}
            />
          </div>

          {sleepHours < 8 ? (
  <p className="mt-3 text-sm text-amber-400">
    ⚠️ Try to get enough sleep for better recovery.
  </p>
) : (
  <p className="mt-3 text-sm text-emerald-400">
    🎉 Great job! You reached your 8-hour sleep target.
  </p>
)}
          <button
  onClick={() => setSleepHours((prev) => Math.min(prev + 1, 8))}
  className="mt-4 rounded-lg bg-indigo-500 px-4 py-2 font-semibold text-white"
>
  + Add 1 Hour Sleep
</button>
        </div>
     ) : selectedModule === "Exercise & Fitness" ? (
  <div className="mt-5 text-slate-300">
    <p>🏃 Daily target: 30 minutes</p>
    <p className="mt-2">Exercise completed: {exerciseMinutes} minutes</p>

    <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-slate-700">
      <div
        className="h-full rounded-full bg-orange-400 transition-all"
        style={{
          width: `${Math.min((exerciseMinutes / 30) * 100, 100)}%`,
        }}
      />
    </div>

    {exerciseMinutes < 30 ? (
      <p className="mt-3 text-sm text-amber-400">
        ⚠️ Keep moving to reach your daily exercise target.
      </p>
    ) : (
      <p className="mt-3 text-sm text-emerald-400">
        🎉 Great job! You reached your exercise target.
      </p>
    )}

    <button
      onClick={() =>
        setExerciseMinutes((prev) => Math.min(prev + 10, 30))
      }
      className="mt-4 rounded-lg bg-orange-500 px-4 py-2 font-semibold text-slate-950"
    >
      + Add 10 Minutes
    </button>
  </div>
) : selectedModule === "Food & Nutrition" ? (
  <div className="mt-5 text-slate-300">
    <p>🍎 Daily target: 3 balanced meals</p>
    <p className="mt-2">Meals logged: {mealsLogged}</p>

    <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-slate-700">
      <div
        className="h-full rounded-full bg-green-400 transition-all"
        style={{
          width: `${Math.min((mealsLogged / 3) * 100, 100)}%`,
        }}
      />
    </div>

    {mealsLogged < 3 ? (
      <p className="mt-3 text-sm text-amber-400">
        ⚠️ Try to log all 3 meals for a balanced day.
      </p>
    ) : (
      <p className="mt-3 text-sm text-emerald-400">
        🎉 Great job! You logged all 3 meals.
      </p>
    )}

    <button
      onClick={() => setMealsLogged((prev) => Math.min(prev + 1, 3))}
      className="mt-4 rounded-lg bg-green-500 px-4 py-2 font-semibold text-slate-950"
    >
      + Log Meal
    </button>
  </div>
) : selectedModule === "Mood & Wellbeing" ? (
  <div className="mt-5 text-slate-300">
    <p>😊 How are you feeling today?</p>

    <div className="mt-4 flex flex-wrap gap-2">
      <button
        onClick={() => setMood("😊 Happy")}
        className="rounded-lg bg-slate-700 px-3 py-2"
      >
        😊 Happy
      </button>

      <button
        onClick={() => setMood("😐 Okay")}
        className="rounded-lg bg-slate-700 px-3 py-2"
      >
        😐 Okay
      </button>

      <button
        onClick={() => setMood("😔 Low")}
        className="rounded-lg bg-slate-700 px-3 py-2"
      >
        😔 Low
      </button>
    </div>

    {mood && (
      <p className="mt-4 text-sm text-emerald-400">
        Today's mood: {mood}
      </p>
    )}
  </div>
) : (
  <p className="mt-2 text-slate-400">
    Your {selectedModule} tracker is ready.
  </p>
)}

      <button
        onClick={() => setSelectedModule(null)}
        className="mt-6 rounded-lg bg-emerald-500 px-4 py-2 font-semibold text-slate-950"
      >
        Close
      </button>
    </div>
  </div>
)}
      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#090e1c] py-6 px-4 text-center text-xs text-slate-400">
        <p>VitaSync Architecture • Next.js Frontend + Python FastAPI Backend + Supabase PostgreSQL + Google Gemini AI</p>
      </footer>
    </main>
  );
}
