import type { Case, CrudeAssay, ProcessUnit, Product, Stream, SolveResult } from "./types";
import { getGuestId } from "./guest";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Guest-Id": getGuestId(),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  // Cases
  listCases: () => request<Case[]>("/api/cases"),
  getCase: (id: number) => request<Case>(`/api/cases/${id}`),
  createCase: (data: { name: string; description?: string }) =>
    request<Case>("/api/cases", { method: "POST", body: JSON.stringify(data) }),
  updateCase: (id: number, data: Partial<Case>) =>
    request<Case>(`/api/cases/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteCase: (id: number) =>
    request<void>(`/api/cases/${id}`, { method: "DELETE" }),
  cloneCase: (id: number) =>
    request<Case>(`/api/cases/${id}/clone`, { method: "POST" }),

  // Crudes
  listCrudes: (caseId: number) =>
    request<CrudeAssay[]>(`/api/cases/${caseId}/crudes`),
  createCrude: (caseId: number, data: Partial<CrudeAssay>) =>
    request<CrudeAssay>(`/api/cases/${caseId}/crudes`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateCrude: (crudeId: number, data: Partial<CrudeAssay>) =>
    request<CrudeAssay>(`/api/crudes/${crudeId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteCrude: (crudeId: number) =>
    request<void>(`/api/crudes/${crudeId}`, { method: "DELETE" }),
  upsertCuts: (
    crudeId: number,
    cuts: Array<{
      cut_name: string;
      yield_pct: number;
      density?: number | null;
      sulfur_pct?: number | null;
    }>
  ) =>
    request(`/api/crudes/${crudeId}/cuts`, {
      method: "PUT",
      body: JSON.stringify({ cuts }),
    }),

  // Units
  listUnits: (caseId: number) =>
    request<ProcessUnit[]>(`/api/cases/${caseId}/units`),
  createUnit: (caseId: number, data: Partial<ProcessUnit>) =>
    request<ProcessUnit>(`/api/cases/${caseId}/units`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateUnit: (unitId: number, data: Partial<ProcessUnit>) =>
    request<ProcessUnit>(`/api/units/${unitId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteUnit: (unitId: number) =>
    request<void>(`/api/units/${unitId}`, { method: "DELETE" }),
  upsertYields: (
    unitId: number,
    yields: Array<{
      input_stream: string;
      output_stream: string;
      yield_fraction: number;
    }>
  ) =>
    request(`/api/units/${unitId}/yields`, {
      method: "PUT",
      body: JSON.stringify({ yields }),
    }),

  // Products
  listProducts: (caseId: number) =>
    request<Product[]>(`/api/cases/${caseId}/products`),
  createProduct: (caseId: number, data: Partial<Product>) =>
    request<Product>(`/api/cases/${caseId}/products`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateProduct: (productId: number, data: Partial<Product>) =>
    request<Product>(`/api/products/${productId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteProduct: (productId: number) =>
    request<void>(`/api/products/${productId}`, { method: "DELETE" }),

  // Streams
  listStreams: (caseId: number) =>
    request<Stream[]>(`/api/cases/${caseId}/streams`),
  createStream: (caseId: number, data: Partial<Stream>) =>
    request<Stream>(`/api/cases/${caseId}/streams`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateStream: (streamId: number, data: Partial<Stream>) =>
    request<Stream>(`/api/streams/${streamId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteStream: (streamId: number) =>
    request<void>(`/api/streams/${streamId}`, { method: "DELETE" }),

  // Solver
  optimize: (caseId: number) =>
    request<SolveResult>(`/api/cases/${caseId}/optimize`, { method: "POST" }),
  getResults: (caseId: number) =>
    request<SolveResult>(`/api/cases/${caseId}/results`),

  // Guest
  resetWorkspace: () =>
    request<Case>("/api/guest/reset", { method: "POST" }),
};
