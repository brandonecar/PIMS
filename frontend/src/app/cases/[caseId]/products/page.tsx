"use client";

import "@/lib/ag-grid";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AgGridReact } from "ag-grid-react";
import type { ColDef, CellValueChangedEvent, ValueParserParams } from "ag-grid-community";
import { api } from "@/lib/api";
import type { Product } from "@/lib/types";

const numberParser = (params: ValueParserParams) => {
  const val = Number(params.newValue);
  return isNaN(val) ? params.oldValue : val;
};

export default function ProductsPage() {
  const { caseId } = useParams();
  const numCaseId = Number(caseId);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dirty, setDirty] = useState<Set<number>>(new Set());

  const loadProducts = useCallback(async () => {
    try {
      const data = await api.listProducts(numCaseId);
      setProducts(data);
      setDirty(new Set());
    } catch (e) {
      console.error("Failed to load products:", e);
    } finally {
      setLoading(false);
    }
  }, [numCaseId]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const columnDefs = useMemo<ColDef<Product>[]>(
    () => [
      { field: "id", headerName: "ID", width: 60, editable: false },
      { field: "name", headerName: "Product", width: 150, editable: true },
      {
        field: "price_per_bbl",
        headerName: "Price ($/bbl)",
        width: 120,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
      {
        field: "min_demand",
        headerName: "Min Demand",
        width: 120,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
      {
        field: "max_demand",
        headerName: "Max Demand",
        width: 120,
        editable: true,
        type: "numericColumn",
        valueParser: numberParser,
      },
    ],
    []
  );

  const onCellValueChanged = useCallback(
    (event: CellValueChangedEvent<Product>) => {
      if (event.data) {
        setDirty((prev) => new Set(prev).add(event.data!.id));
      }
    },
    []
  );

  const handleSave = async () => {
    setSaving(true);
    try {
      const promises = products
        .filter((p) => dirty.has(p.id))
        .map((p) =>
          api.updateProduct(p.id, {
            name: p.name,
            price_per_bbl: p.price_per_bbl,
            min_demand: p.min_demand,
            max_demand: p.max_demand,
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
      const created = await api.createProduct(numCaseId, {
        name: "New Product",
        price_per_bbl: 0,
        min_demand: 0,
        max_demand: 0,
      });
      setProducts((prev) => [...prev, created]);
    } catch (e) {
      console.error("Failed to add product:", e);
    }
  };

  if (loading) {
    return <div className="p-4 text-sm text-slate-500">Loading products...</div>;
  }

  return (
    <div className="h-full flex flex-col p-3 gap-2">
      <div className="flex items-center gap-2 shrink-0">
        <h2 className="text-sm font-semibold text-slate-700">Products</h2>
        <div className="flex-1" />
        <button
          onClick={handleAdd}
          className="px-3 py-1 text-xs bg-white border border-slate-300 rounded hover:bg-slate-50"
        >
          + Add Product
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
        <AgGridReact<Product>
          theme="legacy"
          rowData={products}
          columnDefs={columnDefs}
          onCellValueChanged={onCellValueChanged}
          getRowId={(params) => String(params.data.id)}
          domLayout="normal"
          headerHeight={32}
          rowHeight={30}
        />
      </div>

      {/* Blend specs summary */}
      {products.some((p) => p.blend_specs.length > 0) && (
        <div className="shrink-0 border-t border-slate-200 pt-2">
          <h3 className="text-xs font-semibold text-slate-500 mb-1">
            Blend Specifications
          </h3>
          <table className="w-full text-xs border border-slate-200 rounded bg-white">
            <thead>
              <tr className="bg-slate-50 text-slate-500">
                <th className="text-left px-2 py-1 font-medium">Product</th>
                <th className="text-left px-2 py-1 font-medium">Property</th>
                <th className="text-right px-2 py-1 font-medium">Min</th>
                <th className="text-right px-2 py-1 font-medium">Max</th>
                <th className="text-left px-2 py-1 font-medium">Type</th>
              </tr>
            </thead>
            <tbody>
              {products.flatMap((p) =>
                p.blend_specs.map((spec) => (
                  <tr key={spec.id} className="border-t border-slate-100">
                    <td className="px-2 py-1">{p.name}</td>
                    <td className="px-2 py-1">{spec.property_name}</td>
                    <td className="px-2 py-1 text-right">
                      {spec.min_value ?? "\u2014"}
                    </td>
                    <td className="px-2 py-1 text-right">
                      {spec.max_value ?? "\u2014"}
                    </td>
                    <td className="px-2 py-1">{spec.blend_type}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
