"use client";

import "@/lib/ag-grid";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AgGridReact } from "ag-grid-react";
import type { ColDef, CellValueChangedEvent, ValueParserParams } from "ag-grid-community";
import { api } from "@/lib/api";
import type { ProcessUnit } from "@/lib/types";

const numberParser = (params: ValueParserParams) => {
  const val = Number(params.newValue);
  return isNaN(val) ? params.oldValue : val;
};

export default function UnitsPage() {
  const { caseId } = useParams();
  const numCaseId = Number(caseId);
  const [units, setUnits] = useState<ProcessUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState<Set<number>>(new Set());

  const loadUnits = useCallback(async () => {
    try {
      const data = await api.listUnits(numCaseId);
      setUnits(data);
      setDirty(new Set());
    } catch (e) {
      console.error("Failed to load units:", e);
    } finally {
      setLoading(false);
    }
  }, [numCaseId]);

  useEffect(() => {
    loadUnits();
  }, [loadUnits]);

  const columnDefs = useMemo<ColDef<ProcessUnit>[]>(
    () => [
      { field: "id", headerName: "ID", width: 60, editable: false },
      { field: "name", headerName: "Unit Name", width: 150, editable: true },
      { field: "unit_type", headerName: "Type", width: 120, editable: true },
      {
        field: "min_capacity",
        headerName: "Min Cap (bpd)",
        width: 130,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
      {
        field: "max_capacity",
        headerName: "Max Cap (bpd)",
        width: 130,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
      {
        field: "variable_cost_per_bbl",
        headerName: "Var Cost ($/bbl)",
        width: 140,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
    ],
    []
  );

  const onCellValueChanged = useCallback(
    (event: CellValueChangedEvent<ProcessUnit>) => {
      if (event.data) {
        setDirty((prev) => new Set(prev).add(event.data!.id));
      }
    },
    []
  );

  const handleSave = async () => {
    setSaving(true);
    try {
      const promises = units
        .filter((u) => dirty.has(u.id))
        .map((u) =>
          api.updateUnit(u.id, {
            name: u.name,
            unit_type: u.unit_type,
            min_capacity: u.min_capacity,
            max_capacity: u.max_capacity,
            variable_cost_per_bbl: u.variable_cost_per_bbl,
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
      const created = await api.createUnit(numCaseId, {
        name: "New Unit",
        unit_type: "Generic",
        min_capacity: 0,
        max_capacity: 0,
        variable_cost_per_bbl: 0,
      });
      setUnits((prev) => [...prev, created]);
    } catch (e) {
      console.error("Failed to add unit:", e);
    }
  };

  if (loading) {
    return <div className="p-4 text-sm text-slate-500">Loading units...</div>;
  }

  return (
    <div className="h-full flex flex-col p-3 gap-2">
      <div className="flex items-center gap-2 shrink-0">
        <h2 className="text-sm font-semibold text-slate-700">Process Units</h2>
        <div className="flex-1" />
        <button
          onClick={handleAdd}
          className="px-3 py-1 text-xs bg-white border border-slate-300 rounded hover:bg-slate-50"
        >
          + Add Unit
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

      <div className="flex-1 ag-theme-alpine">
        <AgGridReact<ProcessUnit>
          theme="legacy"
          rowData={units}
          columnDefs={columnDefs}
          onCellValueChanged={onCellValueChanged}
          getRowId={(params) => String(params.data.id)}
          domLayout="normal"
          headerHeight={32}
          rowHeight={30}
        />
      </div>

      {/* Yields summary */}
      {units.length > 0 && (
        <div className="shrink-0 border-t border-slate-200 pt-2 max-h-[200px] overflow-auto">
          <h3 className="text-xs font-semibold text-slate-500 mb-1">
            Unit Yields (read-only summary)
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {units.map((unit) => (
              <div
                key={unit.id}
                className="border border-slate-200 rounded bg-white p-2"
              >
                <div className="text-xs font-medium mb-1">{unit.name}</div>
                {unit.yields.length === 0 ? (
                  <div className="text-xs text-slate-400">No yields defined</div>
                ) : (
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="text-slate-400">
                        <th className="text-left font-normal">Input</th>
                        <th className="text-left font-normal">Output</th>
                        <th className="text-right font-normal">Fraction</th>
                      </tr>
                    </thead>
                    <tbody>
                      {unit.yields.map((y) => (
                        <tr key={y.id}>
                          <td>{y.input_stream}</td>
                          <td>{y.output_stream}</td>
                          <td className="text-right">
                            {y.yield_fraction.toFixed(3)}
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
