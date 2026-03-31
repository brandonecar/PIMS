"use client";

import "@/lib/ag-grid";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AgGridReact } from "ag-grid-react";
import type { ColDef, CellValueChangedEvent, ValueParserParams } from "ag-grid-community";
import { api } from "@/lib/api";
import type { CrudeAssay } from "@/lib/types";

const numberParser = (params: ValueParserParams) => {
  const val = Number(params.newValue);
  return isNaN(val) ? params.oldValue : val;
};

export default function CrudesPage() {
  const { caseId } = useParams();
  const numCaseId = Number(caseId);
  const [crudes, setCrudes] = useState<CrudeAssay[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState<Set<number>>(new Set());

  const loadCrudes = useCallback(async () => {
    try {
      const data = await api.listCrudes(numCaseId);
      setCrudes(data);
      setDirty(new Set());
    } catch (e) {
      console.error("Failed to load crudes:", e);
    } finally {
      setLoading(false);
    }
  }, [numCaseId]);

  useEffect(() => {
    loadCrudes();
  }, [loadCrudes]);

  const columnDefs = useMemo<ColDef<CrudeAssay>[]>(
    () => [
      { field: "id", headerName: "ID", width: 60, editable: false },
      { field: "crude_name", headerName: "Crude Name", width: 150, editable: true },
      {
        field: "api_gravity",
        headerName: "API Gravity",
        width: 110,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
      {
        field: "sulfur_pct",
        headerName: "Sulfur %",
        width: 100,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
      {
        field: "cost_per_bbl",
        headerName: "Cost ($/bbl)",
        width: 120,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
      {
        field: "min_volume",
        headerName: "Min Vol",
        width: 100,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
      {
        field: "max_volume",
        headerName: "Max Vol",
        width: 100,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
    ],
    []
  );

  const onCellValueChanged = useCallback(
    (event: CellValueChangedEvent<CrudeAssay>) => {
      if (event.data) {
        setDirty((prev) => new Set(prev).add(event.data!.id));
      }
    },
    []
  );

  const handleSave = async () => {
    setSaving(true);
    try {
      const promises = crudes
        .filter((c) => dirty.has(c.id))
        .map((c) =>
          api.updateCrude(c.id, {
            crude_name: c.crude_name,
            api_gravity: c.api_gravity,
            sulfur_pct: c.sulfur_pct,
            cost_per_bbl: c.cost_per_bbl,
            min_volume: c.min_volume,
            max_volume: c.max_volume,
          })
        );
      await Promise.all(promises);
      setDirty(new Set());
    } catch (e) {
      console.error("Failed to save:", e);
    } finally {
      setSaving(false);
    }
  };

  const handleAdd = async () => {
    try {
      const created = await api.createCrude(numCaseId, {
        crude_name: "New Crude",
        cost_per_bbl: 0,
        min_volume: 0,
        max_volume: 0,
      });
      setCrudes((prev) => [...prev, created]);
    } catch (e) {
      console.error("Failed to add crude:", e);
    }
  };

  if (loading) {
    return <div className="p-4 text-sm text-slate-500">Loading crudes...</div>;
  }

  return (
    <div className="h-full flex flex-col p-3 gap-2">
      {/* Toolbar */}
      <div className="flex items-center gap-2 shrink-0">
        <h2 className="text-sm font-semibold text-slate-700">Crude Assays</h2>
        <div className="flex-1" />
        <button
          onClick={handleAdd}
          className="px-3 py-1 text-xs bg-white border border-slate-300 rounded hover:bg-slate-50"
        >
          + Add Crude
        </button>
        {dirty.size > 0 && (
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-3 py-1 text-xs bg-[#1a1a2e] text-white rounded hover:bg-[#2a2a4e] disabled:opacity-50"
          >
            {saving ? "Saving..." : `Save (${dirty.size})`}
          </button>
        )}
      </div>

      {/* Grid */}
      <div className="flex-1 ag-theme-alpine">
        <AgGridReact<CrudeAssay>
          theme="legacy"
          rowData={crudes}
          columnDefs={columnDefs}
          onCellValueChanged={onCellValueChanged}
          getRowId={(params) => String(params.data.id)}
          domLayout="normal"
          headerHeight={32}
          rowHeight={30}
        />
      </div>

      {/* Cuts summary below grid */}
      {crudes.length > 0 && (
        <div className="shrink-0 border-t border-slate-200 pt-2">
          <h3 className="text-xs font-semibold text-slate-500 mb-1">
            Distillation Cuts (read-only summary)
          </h3>
          <div className="grid grid-cols-3 gap-2">
            {crudes.map((crude) => (
              <div
                key={crude.id}
                className="border border-slate-200 rounded bg-white p-2"
              >
                <div className="text-xs font-medium mb-1">
                  {crude.crude_name}
                </div>
                {crude.cuts.length === 0 ? (
                  <div className="text-xs text-slate-400">No cuts defined</div>
                ) : (
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-slate-400">
                        <th className="text-left font-normal">Cut</th>
                        <th className="text-right font-normal">Yield %</th>
                        <th className="text-right font-normal">S %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {crude.cuts.map((cut) => (
                        <tr key={cut.id}>
                          <td>{cut.cut_name}</td>
                          <td className="text-right">{cut.yield_pct}</td>
                          <td className="text-right">
                            {cut.sulfur_pct ?? "\u2014"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
