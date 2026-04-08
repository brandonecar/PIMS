"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams, usePathname, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { Case, SolveResult } from "@/lib/types";

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
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [bottomOpen, setBottomOpen] = useState(true);
  const [solveResult, setSolveResult] = useState<SolveResult | null>(null);

  const segments = pathname.split("/");
  const activeTab = segments[3] || "crudes";

  const loadSolveResult = useCallback(() => {
    api.getResults(caseId).then(setSolveResult).catch(console.error);
  }, [caseId]);

  useEffect(() => {
    api.getCase(caseId).then(setCaseData).catch(console.error);
    api.listCases().then(setCases).catch(console.error);
    loadSolveResult();
  }, [caseId, loadSolveResult]);

  return (
    <div className="h-screen flex flex-col bg-[#f8f9fa]">
      {/* Header */}
      <header className="h-10 bg-[#1a1a2e] text-white flex items-center px-3 shrink-0 gap-2">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="w-7 h-7 flex items-center justify-center rounded hover:bg-white/10 transition-colors text-sm"
          title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
        >
          {sidebarOpen ? "\u2630" : "\u2630"}
        </button>
        <button
          onClick={() => router.push("/cases")}
          className="font-semibold text-sm tracking-wide hover:text-slate-300 transition-colors"
        >
          PIMS Optimizer
        </button>
        {caseData && (
          <span className="text-xs text-slate-400 truncate max-w-[200px]">
            / {caseData.name}
          </span>
        )}
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        {sidebarOpen && (
          <aside className="w-[200px] bg-white border-r border-slate-200 flex flex-col shrink-0">
            <div className="px-3 py-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-100">
              Cases
            </div>
            <nav className="flex-1 overflow-y-auto">
              {cases.map((c) => (
                <button
                  key={c.id}
                  onClick={() => router.push(`/cases/${c.id}/${activeTab}`)}
                  className={`w-full text-left px-3 py-1.5 text-sm border-b border-slate-50 hover:bg-slate-50 transition-colors truncate ${
                    c.id === caseId
                      ? "bg-slate-100 font-medium text-[#1a1a2e]"
                      : "text-slate-600"
                  }`}
                  title={c.name}
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
        )}

        {/* Main Area */}
        <div className="flex-1 flex flex-col overflow-hidden min-w-0">
          {/* Tabs */}
          <div className="h-9 bg-white border-b border-slate-200 flex items-end px-1 shrink-0 overflow-x-auto">
            {TABS.map((tab) => (
              <button
                key={tab.key}
                onClick={() => router.push(`/cases/${caseId}/${tab.key}`)}
                className={`px-3 py-1.5 text-xs font-medium rounded-t transition-colors whitespace-nowrap shrink-0 ${
                  activeTab === tab.key
                    ? "bg-[#f8f9fa] text-[#1a1a2e] border border-slate-200 border-b-transparent -mb-px"
                    : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="flex-1 overflow-auto min-w-0">{children}</div>

          {/* Bottom Panel */}
          <div className="border-t border-slate-200 bg-white shrink-0">
            <button
              onClick={() => setBottomOpen(!bottomOpen)}
              className="w-full px-3 py-1 text-xs font-medium text-slate-500 hover:bg-slate-50 flex items-center gap-1 border-b border-slate-100"
            >
              <span
                className={`transition-transform text-[10px] ${bottomOpen ? "rotate-180" : ""}`}
              >
                &#9650;
              </span>
              Solver Status
              {solveResult?.status === "Optimal" && (
                <span className="ml-2 text-green-600 font-normal">
                  Optimal &mdash; ${solveResult.margin?.gross_margin?.toLocaleString()}/day
                </span>
              )}
            </button>
            {bottomOpen && (
              <div className="max-h-[120px] overflow-auto px-3 py-2 text-xs text-slate-500 bg-slate-50">
                {!solveResult || solveResult.status === "not_run" ? (
                  <p className="text-slate-400">
                    No optimization runs yet. Go to the Optimize tab to run the
                    solver.
                  </p>
                ) : solveResult.status === "Optimal" ? (
                  <div className="space-y-1">
                    <p className="text-green-700">
                      Status: Optimal
                      {solveResult.solve_time_ms != null &&
                        ` (${solveResult.solve_time_ms.toFixed(0)}ms)`}
                    </p>
                    <p>
                      Revenue: ${solveResult.margin?.revenue?.toLocaleString()}
                      {" | "}Crude: $
                      {solveResult.margin?.crude_cost?.toLocaleString()}
                      {" | "}Processing: $
                      {solveResult.margin?.processing_cost?.toLocaleString()}
                    </p>
                    <p className="text-slate-400">
                      Crude:{" "}
                      {solveResult.crude_slate
                        ?.filter((c) => c.volume > 0)
                        .map((c) => `${c.crude} ${c.volume.toLocaleString()} bpd`)
                        .join(", ")}
                    </p>
                  </div>
                ) : (
                  <p className="text-amber-700">
                    Status: {solveResult.status}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
