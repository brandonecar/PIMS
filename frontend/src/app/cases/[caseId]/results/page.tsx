"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { SolveResult } from "@/lib/types";

export default function ResultsPage() {
  const { caseId } = useParams();
  const numCaseId = Number(caseId);
  const [result, setResult] = useState<SolveResult | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await api.getResults(numCaseId);
      setResult(data);
    } catch (e) {
      console.error("Failed to load results:", e);
    } finally {
      setLoading(false);
    }
  }, [numCaseId]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return <div className="p-4 text-sm text-slate-500">Loading results...</div>;
  }

  if (!result || result.status === "not_run") {
    return (
      <div className="h-full flex items-center justify-center">
        <p className="text-sm text-slate-400">
          No optimization results yet. Go to the Optimize tab to run the solver.
        </p>
      </div>
    );
  }

  if (result.status !== "Optimal") {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-sm font-medium text-amber-700">
            Solver status: {result.status}
          </p>
          <p className="text-xs text-slate-400 mt-1">
            The LP did not find an optimal solution.
          </p>
        </div>
      </div>
    );
  }

  const m = result.margin;

  return (
    <div className="h-full overflow-auto p-4 min-w-0">
      {/* Margin headline */}
      <div className="mb-4 px-3 py-2 bg-green-50 border border-green-200 rounded text-sm">
        <span className="font-semibold text-green-800">
          Gross Margin: ${m.gross_margin?.toLocaleString()} / day
        </span>
        <span className="ml-2 text-xs text-green-600">
          (Revenue ${m.revenue?.toLocaleString()} &minus; Crude $
          {m.crude_cost?.toLocaleString()} &minus; Processing $
          {m.processing_cost?.toLocaleString()})
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        {/* Crude slate */}
        <Section title="Crude Slate">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-100">
                <th className="text-left py-1 font-medium">Crude</th>
                <th className="text-right py-1 font-medium">Volume (bpd)</th>
                <th className="text-right py-1 font-medium">$/bbl</th>
                <th className="text-right py-1 font-medium">Total Cost</th>
              </tr>
            </thead>
            <tbody>
              {result.crude_slate.map((c) => (
                <tr key={c.crude} className="border-b border-slate-50">
                  <td className="py-1">{c.crude}</td>
                  <td className="text-right">{fmt(c.volume)}</td>
                  <td className="text-right">${c.cost_per_bbl.toFixed(2)}</td>
                  <td className="text-right">${fmt(c.total_cost)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>

        {/* Unit throughputs */}
        <Section title="Unit Throughputs">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-100">
                <th className="text-left py-1 font-medium">Unit</th>
                <th className="text-right py-1 font-medium">Throughput</th>
                <th className="text-right py-1 font-medium">Max Cap</th>
                <th className="text-right py-1 font-medium">Util %</th>
                <th className="text-right py-1 font-medium">Cost</th>
              </tr>
            </thead>
            <tbody>
              {result.unit_throughputs.map((u) => (
                <tr key={u.unit} className="border-b border-slate-50">
                  <td className="py-1">{u.unit}</td>
                  <td className="text-right">{fmt(u.throughput)}</td>
                  <td className="text-right">{fmt(u.max_capacity)}</td>
                  <td className="text-right">
                    <UtilBar pct={u.utilization_pct} />
                  </td>
                  <td className="text-right">${fmt(u.processing_cost)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>

        {/* Product outputs */}
        <Section title="Product Outputs">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-100">
                <th className="text-left py-1 font-medium">Product</th>
                <th className="text-right py-1 font-medium">Volume (bpd)</th>
                <th className="text-right py-1 font-medium">$/bbl</th>
                <th className="text-right py-1 font-medium">Revenue</th>
                <th className="text-right py-1 font-medium">Sulfur %</th>
              </tr>
            </thead>
            <tbody>
              {result.product_outputs.map((p) => (
                <tr key={p.product} className="border-b border-slate-50">
                  <td className="py-1">{p.product}</td>
                  <td className="text-right">{fmt(p.volume)}</td>
                  <td className="text-right">${p.price_per_bbl.toFixed(2)}</td>
                  <td className="text-right">${fmt(p.revenue)}</td>
                  <td className="text-right">
                    {p.sulfur_pct != null ? (
                      <SulfurCell value={p.sulfur_pct} max={p.sulfur_max} />
                    ) : (
                      <span className="text-slate-300">&mdash;</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>

        {/* Stream flows */}
        <Section title="Material Flows">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-100">
                <th className="text-left py-1 font-medium">Stream</th>
                <th className="text-left py-1 font-medium">To</th>
                <th className="text-left py-1 font-medium">Type</th>
                <th className="text-right py-1 font-medium">Volume</th>
              </tr>
            </thead>
            <tbody>
              {result.stream_flows.map((f, i) => (
                <tr key={i} className="border-b border-slate-50">
                  <td className="py-1">{f.stream}</td>
                  <td>{f.destination}</td>
                  <td className="text-slate-400">
                    {f.flow_type === "unit_feed" ? "Unit" : "Product"}
                  </td>
                  <td className="text-right">{fmt(f.volume)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      </div>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border border-slate-200 rounded bg-white p-3 min-w-0 overflow-x-auto">
      <h3 className="text-xs font-semibold text-slate-500 mb-2">{title}</h3>
      {children}
    </div>
  );
}

function UtilBar({ pct }: { pct: number }) {
  const color =
    pct >= 95 ? "bg-red-500" : pct >= 70 ? "bg-amber-400" : "bg-green-400";
  return (
    <div className="inline-flex items-center gap-1.5">
      <div className="w-12 h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <span>{pct.toFixed(1)}%</span>
    </div>
  );
}

function SulfurCell({ value, max }: { value: number; max?: number }) {
  const ratio = max && max > 0 ? value / max : 0;
  const color =
    ratio >= 0.95
      ? "text-red-600 font-medium"
      : ratio >= 0.8
        ? "text-amber-600"
        : "text-slate-600";
  return (
    <span className={color} title={max ? `Max: ${max}%` : undefined}>
      {value.toFixed(4)}
    </span>
  );
}

function fmt(n: number): string {
  return n.toLocaleString(undefined, { maximumFractionDigits: 0 });
}
