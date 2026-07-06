"use client";

import { useCallback, useRef, useState } from "react";
import ResultView from "./ResultView";
import { SAMPLES } from "./samples";
import { baseName, copyText, downloadFile, toCsv, toJson } from "./export";
import type { ApiError, Result } from "./types";

export default function BelegApp() {
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState<string | null>(null); // label of what's loading
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const flashCopied = (which: string) => {
    setCopied(which);
    setTimeout(() => setCopied((c) => (c === which ? null : c)), 1600);
  };

  const send = useCallback(async (bytes: ArrayBuffer, label: string) => {
    setLoading(label);
    setError(null);
    setResult(null);
    setFileName(label);
    try {
      const resp = await fetch("/api/extract", {
        method: "POST",
        headers: { "Content-Type": "application/pdf" },
        body: bytes,
      });
      const data: Result | ApiError = await resp.json();
      if (!data.ok) {
        setError((data as ApiError).error);
      } else {
        setResult(data as Result);
      }
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(null);
    }
  }, []);

  const onFile = useCallback(
    async (file: File) => {
      if (file.size > 4 * 1024 * 1024) {
        setError("File too large (max 4 MB).");
        return;
      }
      send(await file.arrayBuffer(), file.name);
    },
    [send],
  );

  const onSample = useCallback(
    async (id: string, label: string) => {
      setLoading(label);
      setError(null);
      setResult(null);
      try {
        const resp = await fetch(`/samples/${id}.pdf`);
        send(await resp.arrayBuffer(), label);
      } catch {
        setError("Could not load the sample.");
        setLoading(null);
      }
    },
    [send],
  );

  const ibanValid =
    result && result.extraction.iban
      ? !result.validation.flags.some((f) => f.field === "iban" && f.severity === "error")
      : null;

  return (
    <main style={{ maxWidth: 1040, margin: "0 auto", padding: "48px 20px 80px" }}>
      {/* Header */}
      <header style={{ marginBottom: 36 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
          <span style={{ fontSize: 26 }}>🧾</span>
          <span style={{ fontSize: 20, fontWeight: 700, letterSpacing: "-0.02em" }}>BelegRadar</span>
        </div>
        <h1 style={{ fontSize: "clamp(1.8rem, 4vw, 2.6rem)", fontWeight: 700, letterSpacing: "-0.03em", lineHeight: 1.1, margin: "0 0 12px" }}>
          PDF-Rechnung rein, geprüfte Daten raus.
        </h1>
        <p style={{ color: "var(--muted)", fontSize: 16, lineHeight: 1.6, maxWidth: 620, margin: 0 }}>
          Drop an invoice PDF and get structured JSON back: vendor, line items,
          VAT breakdown, totals, IBAN. Every number is checked in code, not
          guessed. <strong style={{ color: "var(--ink)" }}>Nothing is stored.</strong>
        </p>
      </header>

      {/* Drop zone */}
      <div
        onDragOver={(ev) => {
          ev.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(ev) => {
          ev.preventDefault();
          setDragging(false);
          const file = ev.dataTransfer.files?.[0];
          if (file) onFile(file);
        }}
        onClick={() => inputRef.current?.click()}
        style={{
          border: `1.5px dashed ${dragging ? "var(--accent)" : "var(--border)"}`,
          background: dragging ? "var(--accent-soft)" : "var(--surface)",
          borderRadius: 16,
          padding: "40px 24px",
          textAlign: "center",
          cursor: "pointer",
          transition: "all .15s",
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          hidden
          onChange={(ev) => {
            const file = ev.target.files?.[0];
            if (file) onFile(file);
          }}
        />
        <p style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>
          {loading ? `Extracting ${loading}…` : "Drop a PDF invoice here, or click to choose"}
        </p>
        <p style={{ margin: "6px 0 0", fontSize: 13, color: "var(--muted)" }}>
          Text-layer PDFs, max 4 MB. Scans are politely rejected.
        </p>
      </div>

      {/* Sample gallery */}
      <div style={{ marginTop: 22 }}>
        <p style={{ fontSize: 13, color: "var(--muted)", margin: "0 0 10px" }}>
          Or try a sample (no upload needed):
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {SAMPLES.map((s) => (
            <button
              key={s.id}
              onClick={() => onSample(s.id, s.label)}
              disabled={loading !== null}
              title={s.note}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                fontSize: 12.5,
                padding: "7px 11px",
                borderRadius: 999,
                border: "1px solid var(--border)",
                background: "var(--surface)",
                color: "var(--ink)",
                cursor: loading ? "default" : "pointer",
                opacity: loading ? 0.55 : 1,
              }}
            >
              <span>{s.flag}</span>
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div
          style={{
            marginTop: 24,
            padding: "14px 16px",
            borderRadius: 12,
            background: "var(--err-soft)",
            color: "var(--err)",
            fontSize: 14,
          }}
        >
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ marginTop: 30 }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14, flexWrap: "wrap", gap: 8 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>
              {fileName}
              <span style={{ marginLeft: 10, fontSize: 12, fontWeight: 500, color: result.validation.ok ? "var(--ok)" : "var(--err)" }}>
                {result.validation.ok ? "✓ numbers check out" : "⚠ see validation flags"}
              </span>
            </h2>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>{result.tokens} tokens</span>
          </div>

          {/* Export bar */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 18 }}>
            <button
              style={exportBtn()}
              onClick={async () => (await copyText(toJson(result))) && flashCopied("json")}
            >
              {copied === "json" ? "✓ Copied" : "Copy JSON"}
            </button>
            <button
              style={exportBtn()}
              onClick={() =>
                downloadFile(
                  `${baseName(result.extraction, fileName ?? "invoice")}.json`,
                  toJson(result),
                  "application/json",
                )
              }
            >
              Download .json
            </button>
            <button
              style={exportBtn()}
              onClick={async () => (await copyText(toCsv(result.extraction))) && flashCopied("csv")}
            >
              {copied === "csv" ? "✓ Copied" : "Copy CSV"}
            </button>
            <button
              style={exportBtn()}
              onClick={() =>
                downloadFile(
                  `${baseName(result.extraction, fileName ?? "invoice")}.csv`,
                  toCsv(result.extraction),
                  "text/csv;charset=utf-8",
                  true,
                )
              }
            >
              Download .csv
            </button>
          </div>

          <ResultView result={result} ibanValid={ibanValid} />
        </div>
      )}

      {/* Footer */}
      <footer style={{ marginTop: 56, paddingTop: 22, borderTop: "1px solid var(--border)", fontSize: 12.5, color: "var(--muted)", lineHeight: 1.7 }}>
        <p style={{ margin: "0 0 8px" }}>
          <strong style={{ color: "var(--ink)" }}>Privacy:</strong> uploads are
          processed in memory and never stored or logged. Sample invoices are
          fictional. This is a demo; do not use it as tax advice.
        </p>
        <p style={{ margin: 0 }}>
          Extraction engine:{" "}
          <a href="https://pypi.org/project/belegradar/" style={link()}>
            belegradar
          </a>{" "}
          on PyPI ·{" "}
          <a href="https://github.com/n3ndor/belegradar" style={link()}>
            source & accuracy eval
          </a>{" "}
          ·{" "}
          <a href="https://nagysolution.com" style={link()}>
            nagysolution.com
          </a>
        </p>
      </footer>

      <style>{`@media (max-width: 760px){ .result-grid{ grid-template-columns: 1fr !important; } }`}</style>
    </main>
  );
}

function link(): React.CSSProperties {
  return { color: "var(--accent)", textDecoration: "none" };
}

function exportBtn(): React.CSSProperties {
  return {
    fontSize: 13,
    fontWeight: 500,
    padding: "8px 14px",
    borderRadius: 9,
    border: "1px solid var(--border)",
    background: "var(--surface)",
    color: "var(--accent)",
    cursor: "pointer",
  };
}
