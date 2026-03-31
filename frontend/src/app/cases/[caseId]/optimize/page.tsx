"use client";

import { useParams } from "next/navigation";

export default function OptimizePage() {
  const { caseId } = useParams();

  return (
    <div className="h-full flex flex-col items-center justify-center p-6">
      <div className="max-w-md text-center">
        <h2 className="text-sm font-semibold text-slate-700 mb-2">
          Optimization
        </h2>
        <p className="text-xs text-slate-500 mb-4">
          This is where I’m hooking up the actual refinery solve. The case data,
          economics, and unit setup are already in place.
        </p>
        <button
          disabled
          className="px-4 py-2 text-sm bg-slate-200 text-slate-400 rounded cursor-not-allowed"
        >
          Run Optimization
        </button>
        <p className="text-xs text-slate-400 mt-4">
          Case ID: {caseId}
        </p>
      </div>
    </div>
  );
}
