"use client";

export default function ResultsPage() {
  return (
    <div className="h-full flex flex-col items-center justify-center p-6">
      <div className="max-w-md text-center">
        <h2 className="text-sm font-semibold text-slate-700 mb-2">
          Results
        </h2>
        <p className="text-xs text-slate-500 mb-2">
          Nothing to show here yet since I haven’t run the solver.
        </p>
        <p className="text-xs text-slate-400">
          Once that part is connected, this page should show crude slate, unit
          utilization, product volumes, margin, and the main active constraints.
        </p>
      </div>
    </div>
  );
}
