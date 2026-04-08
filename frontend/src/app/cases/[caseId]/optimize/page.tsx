"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { SolveResult } from "@/lib/types";

export default function OptimizePage() {
  const { caseId } = useParams();
  const router = useRouter();
  const numCaseId = Number(caseId);

  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<SolveResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async () => {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.optimize(numCaseId);
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Optimization failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="h-full flex flex-col p-4 gap-4 min-w-0">
      <div className="flex items-center gap-3 flex-wrap">
        <h2 className="text-sm font-semibold text-slate-700">Optimization</h2>
        <button
          onClick={handleOptimize}
          disabled={running}
          className="px-4 py-1.5 text-sm bg-[#1a1a2e] text-white rounded hover:bg-[#2a2a4e] disabled:opacity-50 transition-colors"
        >
          {running ? "Solving..." : "Run Optimization"}
        </button>
        {result?.status === "Optimal" && (
          <button
            onClick={() => router.push(`/cases/${caseId}/results`)}
            className="px-3 py-1.5 text-xs text-slate-600 border border-slate-300 rounded hover:bg-slate-50"
          >
            View Full Results
          </button>
        )}
      </div>

      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
          {error}
        </div>
      )}

      {result && (
        <div className="flex-1 overflow-auto min-w-0">
          {/* Status bar */}
          <div
            className={`px-3 py-2 rounded text-sm font-medium mb-4 ${
              result.status === "Optimal"
                ? "bg-green-50 text-green-800 border border-green-200"
                : "bg-amber-50 text-amber-800 border border-amber-200"
            }`}
          >
            {result.status === "Optimal"
              ? `Optimal solution found — Gross margin: $${result.margin.gross_margin?.toLocaleString()} / day`
              : `Solver status: ${result.status}`}
            {result.solve_time_ms != null && (
              <span className="ml-3 text-xs opacity-70">
                ({result.solve_time_ms.toFixed(0)}ms)
              </span>
            )}
          </div>

          {result.status === "Optimal" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Margin summary */}
              <div className="border border-slate-200 rounded bg-white p-3">
                <h3 className="text-xs font-semibold text-slate-500 mb-2">
                  Margin Breakdown
                </h3>
                <table className="w-full text-xs">
                  <tbody>
                    <tr>
                      <td className="py-0.5">Revenue</td>
                      <td className="text-right text-green-700">
                        ${result.margin.revenue?.toLocaleString()}
                      </td>
                    </tr>
                    <tr>
                      <td className="py-0.5">Crude cost</td>
                      <td className="text-right text-red-700">
                        (${result.margin.crude_cost?.toLocaleString()})
                      </td>
                    </tr>
                    <tr>
                      <td className="py-0.5">Processing cost</td>
                      <td className="text-right text-red-700">
                        (${result.margin.processing_cost?.toLocaleString()})
                      </td>
                    </tr>
                    <tr className="border-t border-slate-200 font-semibold">
                      <td className="pt-1">Gross Margin</td>
                      <td className="text-right pt-1">
                        ${result.margin.gross_margin?.toLocaleString()}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Crude slate */}
              <div className="border border-slate-200 rounded bg-white p-3">
                <h3 className="text-xs font-semibold text-slate-500 mb-2">
                  Crude Slate
                </h3>
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-400">
                      <th className="text-left font-normal">Crude</th>
                      <th className="text-right font-normal">Volume</th>
                      <th className="text-right font-normal">Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.crude_slate.map((c) => (
                      <tr key={c.crude}>
                        <td className="py-0.5">{c.crude}</td>
                        <td className="text-right">
                          {c.volume.toLocaleString()}
                        </td>
                        <td className="text-right">
                          ${c.total_cost.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Product outputs */}
              <div className="border border-slate-200 rounded bg-white p-3">
                <h3 className="text-xs font-semibold text-slate-500 mb-2">
                  Product Outputs
                </h3>
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-slate-400">
                      <th className="text-left font-normal">Product</th>
                      <th className="text-right font-normal">Volume</th>
                      <th className="text-right font-normal">Revenue</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.product_outputs.map((p) => (
                      <tr key={p.product}>
                        <td className="py-0.5">{p.product}</td>
                        <td className="text-right">
                          {p.volume.toLocaleString()}
                        </td>
                        <td className="text-right">
                          ${p.revenue.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {!result && !error && !running && (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-xs text-slate-400">
            Click &quot;Run Optimization&quot; to solve the refinery LP for this
            case.
          </p>
        </div>
      )}
    </div>
  );
}
