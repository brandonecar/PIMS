"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { Case } from "@/lib/types";

export default function CasesPage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [newName, setNewName] = useState("");
  const router = useRouter();

  const loadCases = async () => {
    try {
      const data = await api.listCases();
      setCases(data);
    } catch (e) {
      console.error("Failed to load cases:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCases();
  }, []);

  const handleCreate = async () => {
    if (!newName.trim()) return;
    try {
      const created = await api.createCase({ name: newName.trim() });
      setNewName("");
      setCases((prev) => [...prev, created]);
    } catch (e) {
      console.error("Failed to create case:", e);
    }
  };

  const handleClone = async (id: number) => {
    try {
      const cloned = await api.cloneCase(id);
      setCases((prev) => [...prev, cloned]);
    } catch (e) {
      console.error("Failed to clone case:", e);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteCase(id);
      setCases((prev) => prev.filter((c) => c.id !== id));
    } catch (e) {
      console.error("Failed to delete case:", e);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-[#f8f9fa]">
      {/* Header */}
      <header className="h-10 bg-[#1a1a2e] text-white flex items-center px-4 shrink-0">
        <span className="font-semibold text-sm tracking-wide">
          PIMS Optimizer
        </span>
        <span className="ml-4 text-xs text-slate-400">Case Management</span>
      </header>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-lg font-semibold mb-4">Cases</h1>

          {/* Create form */}
          <div className="flex gap-2 mb-6">
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
              placeholder="New case name..."
              className="flex-1 border border-slate-300 rounded px-3 py-1.5 text-sm bg-white focus:outline-none focus:ring-1 focus:ring-slate-400"
            />
            <button
              onClick={handleCreate}
              className="px-4 py-1.5 text-sm bg-[#1a1a2e] text-white rounded hover:bg-[#2a2a4e] transition-colors"
            >
              Create Case
            </button>
          </div>

          {/* Cases list */}
          {loading ? (
            <p className="text-sm text-slate-500">Loading...</p>
          ) : cases.length === 0 ? (
            <p className="text-sm text-slate-500">
              No cases yet. Create one to get started.
            </p>
          ) : (
            <div className="border border-slate-200 rounded bg-white">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    <th className="text-left px-3 py-2 font-medium">ID</th>
                    <th className="text-left px-3 py-2 font-medium">Name</th>
                    <th className="text-left px-3 py-2 font-medium">
                      Description
                    </th>
                    <th className="text-left px-3 py-2 font-medium">
                      Updated
                    </th>
                    <th className="text-right px-3 py-2 font-medium">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {cases.map((c) => (
                    <tr
                      key={c.id}
                      className="border-b border-slate-100 last:border-0 hover:bg-slate-50 cursor-pointer"
                      onClick={() => router.push(`/cases/${c.id}/crudes`)}
                    >
                      <td className="px-3 py-2 text-slate-500">{c.id}</td>
                      <td className="px-3 py-2 font-medium">{c.name}</td>
                      <td className="px-3 py-2 text-slate-500">
                        {c.description || "—"}
                      </td>
                      <td className="px-3 py-2 text-slate-500">
                        {new Date(c.updated_at).toLocaleDateString()}
                      </td>
                      <td className="px-3 py-2 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleClone(c.id);
                          }}
                          className="text-xs px-2 py-1 text-slate-600 hover:bg-slate-200 rounded mr-1"
                        >
                          Clone
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(c.id);
                          }}
                          className="text-xs px-2 py-1 text-red-600 hover:bg-red-50 rounded"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
