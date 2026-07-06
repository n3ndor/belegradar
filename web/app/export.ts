import type { Extraction, Result } from "./types";

export function downloadFile(filename: string, content: string, mime: string, bom = false) {
  const blob = new Blob([bom ? "﻿" + content : content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function copyText(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}

export function toJson(result: Result): string {
  return JSON.stringify(result.extraction, null, 2);
}

function csvCell(value: unknown): string {
  const s = value === null || value === undefined ? "" : String(value);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

// One row per line item, invoice-level fields repeated on each row. Denormalized
// on purpose so it imports cleanly into a spreadsheet or accounting tool. Amounts
// keep dot decimals (matching the JSON); the VAT breakdown is one summary cell.
export function toCsv(e: Extraction): string {
  const header = [
    "invoice_number", "invoice_date", "due_date", "vendor_name", "vendor_vat_id",
    "customer_name", "currency", "description", "quantity", "unit_price",
    "line_total", "net_total", "vat_summary", "gross_total", "iban",
  ];
  const vatSummary = e.vat_breakdown.map((v) => `${v.rate}% = ${v.amount}`).join(" | ");
  const invoiceCols = [
    e.invoice_number, e.invoice_date, e.due_date, e.vendor_name, e.vendor_vat_id,
    e.customer_name, e.currency,
  ];
  const totalsCols = [e.net_total, vatSummary, e.gross_total, e.iban];

  const rows: unknown[][] = [];
  if (e.line_items.length === 0) {
    rows.push([...invoiceCols, "", "", "", "", ...totalsCols]);
  } else {
    for (const li of e.line_items) {
      rows.push([...invoiceCols, li.description, li.quantity, li.unit_price, li.total, ...totalsCols]);
    }
  }
  return [header, ...rows].map((r) => r.map(csvCell).join(",")).join("\r\n");
}

export function baseName(e: Extraction, fallback: string): string {
  const raw =
    e.invoice_number && e.invoice_number !== "unknown"
      ? e.invoice_number
      : fallback.replace(/\.pdf$/i, "");
  return raw.replace(/[^\w.-]+/g, "_").slice(0, 60) || "invoice";
}
