"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { CrudeAssay, ProcessUnit, Product } from "@/lib/types";

export default function EconomicsPage() {
  const { caseId } = useParams();
  const numCaseId = Number(caseId);
  const [crudes, setCrudes] = useState<CrudeAssay[]>([]);
  const [units, setUnits] = useState<ProcessUnit[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [c, u, p] = await Promise.all([
        api.listCrudes(numCaseId),
        api.listUnits(numCaseId),
        api.listProducts(numCaseId),
      ]);
      setCrudes(c);
      setUnits(u);
      setProducts(p);
    } catch (e) {
      console.error("Failed to load economics data:", e);
    } finally {
      setLoading(false);
    }
  }, [numCaseId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return <div className="p-4 text-sm text-slate-500">Loading economics...</div>;
  }

  return (
    <div className="h-full overflow-auto p-3">
      <h2 className="text-sm font-semibold text-slate-700 mb-3">
        Economics Summary
      </h2>

      <div className="grid grid-cols-3 gap-4">
        {/* Crude costs */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 mb-1">
            Crude Costs
          </h3>
          <table className="w-full text-xs border border-slate-200 rounded bg-white">
            <thead>
              <tr className="bg-slate-50 text-slate-500">
                <th className="text-left px-2 py-1 font-medium">Crude</th>
                <th className="text-right px-2 py-1 font-medium">$/bbl</th>
                <th className="text-right px-2 py-1 font-medium">Max Vol</th>
              </tr>
            </thead>
            <tbody>
              {crudes.map((c) => (
                <tr key={c.id} className="border-t border-slate-100">
                  <td className="px-2 py-1">{c.crude_name}</td>
                  <td className="px-2 py-1 text-right">
                    ${c.cost_per_bbl.toFixed(2)}
                  </td>
                  <td className="px-2 py-1 text-right">
                    {c.max_volume.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Unit variable costs */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 mb-1">
            Unit Variable Costs
          </h3>
          <table className="w-full text-xs border border-slate-200 rounded bg-white">
            <thead>
              <tr className="bg-slate-50 text-slate-500">
                <th className="text-left px-2 py-1 font-medium">Unit</th>
                <th className="text-right px-2 py-1 font-medium">$/bbl</th>
                <th className="text-right px-2 py-1 font-medium">Max Cap</th>
              </tr>
            </thead>
            <tbody>
              {units.map((u) => (
                <tr key={u.id} className="border-t border-slate-100">
                  <td className="px-2 py-1">{u.name}</td>
                  <td className="px-2 py-1 text-right">
                    ${u.variable_cost_per_bbl.toFixed(2)}
                  </td>
                  <td className="px-2 py-1 text-right">
                    {u.max_capacity.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Product prices */}
        <div>
          <h3 className="text-xs font-semibold text-slate-500 mb-1">
            Product Prices
          </h3>
          <table className="w-full text-xs border border-slate-200 rounded bg-white">
            <thead>
              <tr className="bg-slate-50 text-slate-500">
                <th className="text-left px-2 py-1 font-medium">Product</th>
                <th className="text-right px-2 py-1 font-medium">$/bbl</th>
                <th className="text-right px-2 py-1 font-medium">Max Dem</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id} className="border-t border-slate-100">
                  <td className="px-2 py-1">{p.name}</td>
                  <td className="px-2 py-1 text-right">
                    ${p.price_per_bbl.toFixed(2)}
                  </td>
                  <td className="px-2 py-1 text-right">
                    {p.max_demand.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
