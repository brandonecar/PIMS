"use client";

import { useEffect, useState } from "react";
import { useParams, usePathname, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { Case } from "@/lib/types";

const TABS = [
  { key: "crudes", label: "Crudes" },
  { key: "units", label: "Units" },
  { key: "products", label: "Products" },
  { key: "streams", label: "Streams" },
  { key: "economics", label: "Economics" },
  { key: "optimize", label: "Optimize" },
  { key: "results", label: "Results" },
] as const;

export default function CaseWorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams();
  const pathname = usePathname();
  const router = useRouter();
  const caseId = Number(params.caseId);

  const [caseData, setCaseData] = useState<Case | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [bottomOpen, setBottomOpen] = useState(true);

  // Determine active tab from pathname
  const segments = pathname.split("/");
  const activeTab = segments[3] || "crudes";

  useEffect(() => {
    api.getCase(caseId).then(setCaseData).catch(console.error);
    api.listCases().then(setCases).catch(console.error);
  }, [caseId]);

  return (
    <div className="h-screen flex flex-col bg-[#f8f9fa]">
      {/* ── Header ──────────────────────────────────────────── */}
      <header className="h-10 bg-[#1a1a2e] text-white flex items-center px-4 shrink-0">
        <button
          onClick={() => router.push("/cases")}
          className="font-semibold text-sm tracking-wide hover:text-slate-300 transition-colors"
        >
          PIMS Optimizer
        </button>
        {caseData && (
          <span className="ml-4 text-xs text-slate-400">
            {caseData.name}
          </span>
        )}
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* ── Left Sidebar ────────────────────────────────── */}
        <aside className="w-[220px] bg-white border-r border-slate-200 flex flex-col shrink-0">
          <div className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-100">
            Cases
          </div>
          <nav className="flex-1 overflow-y-auto">
            {cases.map((c) => (
              <button
                key={c.id}
                onClick={() => router.push(`/cases/${c.id}/${activeTab}`)}
                className={`w-full text-left px-3 py-1.5 text-sm border-b border-slate-50 hover:bg-slate-50 transition-colors ${
                  c.id === caseId
                    ? "bg-slate-100 font-medium text-[#1a1a2e]"
                    : "text-slate-600"
                }`}
              >
                {c.name}
              </button>
            ))}
          </nav>
          <div className="border-t border-slate-200 px-3 py-2">
            <button
              onClick={() => router.push("/cases")}
              className="text-xs text-slate-500 hover:text-slate-700"
            >
              Manage Cases
            </button>
          </div>
        </aside>

        {/* ── Main Area ───────────────────────────────────── */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Workspace Tabs */}
          <div className="h-9 bg-white border-b border-slate-200 flex items-end px-1 shrink-0">
            {TABS.map((tab) => (
              <button
                key={tab.key}
                onClick={() => router.push(`/cases/${caseId}/${tab.key}`)}
                className={`px-4 py-1.5 text-xs font-medium rounded-t transition-colors ${
                  activeTab === tab.key
                    ? "bg-[#f8f9fa] text-[#1a1a2e] border border-slate-200 border-b-transparent -mb-px"
                    : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-auto">{children}</div>

          {/* ── Bottom Panel (Solver Log placeholder) ────── */}
          <div className="border-t border-slate-200 bg-white shrink-0">
            <button
              onClick={() => setBottomOpen(!bottomOpen)}
              className="w-full px-3 py-1 text-xs font-medium text-slate-500 hover:bg-slate-50 flex items-center gap-1 border-b border-slate-100"
            >
              <span className={`transition-transform ${bottomOpen ? "rotate-180" : ""}`}>
                &#9650;
              </span>
              Solver Log
            </button>
            {bottomOpen && (
              <div className="h-[140px] overflow-auto px-3 py-2 font-mono text-xs text-slate-500 bg-slate-50">
                <p>No optimization runs yet.</p>
                <p className="text-slate-400 mt-1">
                  Configure your case data, then go to the Optimize tab to run
                  the LP solver.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
