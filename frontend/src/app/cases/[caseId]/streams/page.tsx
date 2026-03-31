"use client";

import "@/lib/ag-grid";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AgGridReact } from "ag-grid-react";
import type { ColDef } from "ag-grid-community";
import { api } from "@/lib/api";
import type { Stream } from "@/lib/types";

export default function StreamsPage() {
  const { caseId } = useParams();
  const numCaseId = Number(caseId);
  const [streams, setStreams] = useState<Stream[]>([]);
  const [loading, setLoading] = useState(true);

  const loadStreams = useCallback(async () => {
    try {
      const data = await api.listStreams(numCaseId);
      setStreams(data);
    } catch (e) {
      console.error("Failed to load streams:", e);
    } finally {
      setLoading(false);
    }
  }, [numCaseId]);

  useEffect(() => {
    loadStreams();
  }, [loadStreams]);

  const columnDefs = useMemo<ColDef<Stream>[]>(
    () => [
      { field: "id", headerName: "ID", width: 60 },
      { field: "name", headerName: "Stream Name", width: 200 },
      { field: "stream_type", headerName: "Type", width: 130 },
    ],
    []
  );

  if (loading) {
    return <div className="p-4 text-sm text-slate-500">Loading streams...</div>;
  }

  return (
    <div className="h-full flex flex-col p-3 gap-2">
      <div className="flex items-center gap-2 shrink-0">
        <h2 className="text-sm font-semibold text-slate-700">Streams</h2>
        <span className="text-xs text-slate-400">
          {streams.length} streams defined
        </span>
      </div>

      <div className="flex-1 ag-theme-alpine">
        <AgGridReact<Stream>
          theme="legacy"
          rowData={streams}
          columnDefs={columnDefs}
          getRowId={(params) => String(params.data.id)}
          domLayout="normal"
          headerHeight={32}
          rowHeight={30}
        />
      </div>
    </div>
  );
}
