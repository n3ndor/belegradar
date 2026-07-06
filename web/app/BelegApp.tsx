"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ResultView from "./ResultView";
import { SAMPLES } from "./samples";
import { STRINGS, type Lang } from "./i18n";
import { baseName, copyText, downloadFile, toCsv, toJson } from "./export";
import type { ApiError, Result } from "./types";

export default function BelegApp() {
  const [lang, setLang] = useState<Lang>("de");
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const cacheRef = useRef<Record<string, Result> | null>(null);

  const s = STRINGS[lang];

  // Restore language choice after mount (avoids hydration mismatch).
  useEffect(() => {
    const saved = localStorage.getItem("belegradar-lang");
    if (saved === "de" || saved === "en") setLang(saved);
  }, []);

  const switchLang = () => {
    const next: Lang = lang === "de" ? "en" : "de";
    setLang(next);
    localStorage.setItem("belegradar-lang", next);
  };

  const flash = (key: string) => {
    setFeedback(key);
    setTimeout(() => setFeedback((f) => (f === key ? null : f)), 1600);
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
      if (!data.ok) setError((data as ApiError).error);
      else setResult(data as Result);
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(null);
    }
  }, []);

  const onFile = useCallback(
    async (file: File) => {
      if (file.size > 4 * 1024 * 1024) {
        setError(lang === "de" ? "Datei zu groß (max. 4 MB)." : "File too large (max 4 MB).");
        return;
      }
      send(await file.arrayBuffer(), file.name);
    },
    [send, lang],
  );

  // Samples are pre-extracted: serve the cached result instantly, no LLM call.
  const onSample = useCallback(async (id: string, label: string) => {
    setError(null);
    try {
      if (!cacheRef.current) {
        const resp = await fetch("/samples/results.json");
        cacheRef.current = await resp.json();
      }
      const cached = cacheRef.current?.[id];
      if (cached) {
        setFileName(label);
        // tokens:0 marks this as a pre-computed sample (no live LLM call), so
        // the header shows the "sample" label instead of a token count.
        setResult({ ...cached, tokens: 0 });
        return;
      }
    } catch {
      // fall through to live extraction
    }
    try {
      const resp = await fetch(`/samples/${id}.pdf`);
      send(await resp.arrayBuffer(), label);
    } catch {
      setError(lang === "de" ? "Beispiel konnte nicht geladen werden." : "Could not load the sample.");
    }
  }, [send, lang]);

  const ibanValid =
    result && result.extraction.iban
      ? !result.validation.flags.some((f) => f.field === "iban" && f.severity === "error")
      : null;

  const base = result ? baseName(result.extraction, fileName ?? "invoice") : "invoice";

  return (
    <main style={{ maxWidth: 1040, margin: "0 auto", padding: "40px 20px 80px" }}>
      {/* Top bar: brand + language switch */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 26 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 24 }}>🧾</span>
          <span style={{ fontSize: 19, fontWeight: 700, letterSpacing: "-0.02em" }}>BelegRadar</span>
        </div>
        <button
          onClick={switchLang}
          aria-label="Switch language"
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 7,
            fontSize: 13,
            fontWeight: 500,
            padding: "7px 12px",
            borderRadius: 999,
            border: "1px solid var(--border)",
            background: "var(--surface)",
            color: "var(--ink)",
            cursor: "pointer",
          }}
        >
          <span style={{ fontSize: 15 }}>{s.switchFlag}</span>
          {s.switchLabel}
        </button>
      </div>

      {/* Header */}
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: "clamp(1.8rem, 4vw, 2.6rem)", fontWeight: 700, letterSpacing: "-0.03em", lineHeight: 1.1, margin: "0 0 12px" }}>
          {s.tagline}
        </h1>
        <p style={{ color: "var(--muted)", fontSize: 16, lineHeight: 1.6, maxWidth: 640, margin: 0 }}>
          {s.intro} <strong style={{ color: "var(--ink)" }}>{s.introStored}</strong>
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
        onClick={() => !loading && inputRef.current?.click()}
        style={{
          border: `1.5px dashed ${dragging ? "var(--accent)" : "var(--border)"}`,
          background: dragging ? "var(--accent-soft)" : "var(--surface)",
          borderRadius: 16,
          padding: "38px 24px",
          textAlign: "center",
          cursor: loading ? "default" : "pointer",
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
        {loading ? (
          <p style={{ margin: 0, fontSize: 15, fontWeight: 600, display: "inline-flex", alignItems: "center", gap: 10 }}>
            <span className="spinner" />
            {s.extracting.replace("{name}", loading)}
          </p>
        ) : (
          <>
            <p style={{ margin: 0, fontSize: 15, fontWeight: 600 }}>{s.dropPrompt}</p>
            <p style={{ margin: "6px 0 0", fontSize: 13, color: "var(--muted)" }}>{s.dropHint}</p>
          </>
        )}
      </div>

      {/* Sample gallery */}
      <div style={{ marginTop: 22 }}>
        <p style={{ fontSize: 13, color: "var(--muted)", margin: "0 0 10px" }}>{s.samplesPrompt}</p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {SAMPLES.map((sample) => (
            <button
              key={sample.id}
              onClick={() => onSample(sample.id, sample.label)}
              disabled={loading !== null}
              title={sample.note[lang]}
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
              <span>{sample.flag}</span>
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{ marginTop: 24, padding: "14px 16px", borderRadius: 12, background: "var(--err-soft)", color: "var(--err)", fontSize: 14 }}>
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div key={fileName ?? "r"} style={{ marginTop: 30, animation: "fadeIn .35s ease" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14, flexWrap: "wrap", gap: 8 }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, margin: 0 }}>
              {fileName}
              <span style={{ marginLeft: 10, fontSize: 12, fontWeight: 600, color: result.validation.ok ? "var(--ok)" : "var(--err)" }}>
                {result.validation.ok ? s.numbersOk : s.numbersWarn}
              </span>
            </h2>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>
              {result.tokens ? `${result.tokens} ${s.tokensLabel}` : s.cached}
            </span>
          </div>

          {/* Export bar */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 20 }}>
            <button style={btnFilled()} onClick={() => { downloadFile(`${base}.csv`, toCsv(result.extraction), "text/csv;charset=utf-8", true); flash("dlcsv"); }}>
              {feedback === "dlcsv" ? s.saved : `⤓ ${s.downloadCsv}`}
            </button>
            <button style={btnFilled()} onClick={() => { downloadFile(`${base}.json`, toJson(result), "application/json"); flash("dljson"); }}>
              {feedback === "dljson" ? s.saved : `⤓ ${s.downloadJson}`}
            </button>
            <button style={btnOutline()} onClick={async () => { if (await copyText(toCsv(result.extraction))) flash("cpcsv"); }}>
              {feedback === "cpcsv" ? s.copied : s.copyCsv}
            </button>
            <button style={btnOutline()} onClick={async () => { if (await copyText(toJson(result))) flash("cpjson"); }}>
              {feedback === "cpjson" ? s.copied : s.copyJson}
            </button>
          </div>

          <ResultView result={result} ibanValid={ibanValid} s={s} />
        </div>
      )}

      {/* Footer */}
      <footer style={{ marginTop: 56, paddingTop: 22, borderTop: "1px solid var(--border)", fontSize: 12.5, color: "var(--muted)", lineHeight: 1.7 }}>
        <p style={{ margin: "0 0 8px" }}>{s.footerPrivacy}</p>
        <p style={{ margin: 0 }}>
          {s.footerEnginePrefix}{" "}
          <a href="https://pypi.org/project/belegradar/" style={link()}>belegradar</a> {s.footerEngineOnPypi} ·{" "}
          <a href="https://github.com/n3ndor/belegradar" style={link()}>{s.footerEngineSource}</a> ·{" "}
          <a href="https://nagysolution.com" style={link()}>nagysolution.com</a>
        </p>
      </footer>

      <style>{`
        @media (max-width: 760px){ .result-grid{ grid-template-columns: 1fr !important; } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
        @keyframes spin { to { transform: rotate(360deg); } }
        .spinner { width: 16px; height: 16px; border-radius: 50%; border: 2px solid var(--border); border-top-color: var(--accent); display: inline-block; animation: spin .7s linear infinite; }
      `}</style>
    </main>
  );
}

function link(): React.CSSProperties {
  return { color: "var(--accent)", textDecoration: "none" };
}
function btnFilled(): React.CSSProperties {
  return {
    fontSize: 13.5,
    fontWeight: 600,
    padding: "10px 16px",
    borderRadius: 10,
    border: "1px solid var(--accent)",
    background: "var(--accent)",
    color: "#fff",
    cursor: "pointer",
  };
}
function btnOutline(): React.CSSProperties {
  return {
    fontSize: 13.5,
    fontWeight: 500,
    padding: "10px 16px",
    borderRadius: 10,
    border: "1px solid var(--border)",
    background: "var(--surface)",
    color: "var(--accent)",
    cursor: "pointer",
  };
}
