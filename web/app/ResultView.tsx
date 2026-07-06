"use client";

import type { Extraction, Flag, Result } from "./types";

const CONF_COLOR: Record<string, string> = {
  high: "var(--ok)",
  medium: "var(--warn)",
  low: "var(--err)",
};

const PFLICHT_LABELS: Record<string, string> = {
  vendor_name_address: "Name und Anschrift des Leistenden",
  vat_id_or_tax_number: "USt-IdNr. oder Steuernummer",
  invoice_date: "Rechnungsdatum",
  invoice_number: "Fortlaufende Rechnungsnummer",
  line_items: "Menge und Art der Leistung",
  net_amount: "Nettobetrag (Entgelt)",
  vat_rate_and_amount: "Steuersatz und Steuerbetrag",
  gross_amount: "Bruttobetrag",
};

function Dot({ level }: { level?: string }) {
  if (!level) return null;
  return (
    <span
      title={`confidence: ${level}`}
      style={{
        display: "inline-block",
        width: 7,
        height: 7,
        borderRadius: "50%",
        background: CONF_COLOR[level] ?? "var(--muted)",
        marginLeft: 6,
        verticalAlign: "middle",
      }}
    />
  );
}

function Field({
  label,
  value,
  conf,
}: {
  label: string;
  value: React.ReactNode;
  conf?: string;
}) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 16, padding: "7px 0" }}>
      <span style={{ color: "var(--muted)", fontSize: 13 }}>{label}</span>
      <span style={{ textAlign: "right", fontSize: 14, fontWeight: 500 }}>
        {value || <span style={{ color: "var(--muted)", fontWeight: 400 }}>—</span>}
        <Dot level={conf} />
      </span>
    </div>
  );
}

function money(v: string | null, currency: string): string {
  if (v === null) return "";
  return `${v} ${currency}`;
}

export default function ResultView({ result, ibanValid }: { result: Result; ibanValid: boolean | null }) {
  const e: Extraction = result.extraction;
  const c = e.confidence || {};
  const errors = result.validation.flags.filter((f) => f.severity === "error");
  const warns = result.validation.flags.filter((f) => f.severity === "warn");

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }} className="result-grid">
      {/* LEFT: raw text */}
      <section style={card()}>
        <h3 style={cardTitle()}>Raw PDF text</h3>
        <pre
          className="mono"
          style={{
            margin: 0,
            fontSize: 11.5,
            lineHeight: 1.55,
            color: "var(--muted)",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            maxHeight: 520,
            overflowY: "auto",
          }}
        >
          {result.raw_text}
        </pre>
      </section>

      {/* RIGHT: structured */}
      <section style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        <div style={card()}>
          <h3 style={cardTitle()}>Extracted fields</h3>
          <Field label="Vendor" value={e.vendor_name} conf={c.vendor_name} />
          <Field label="Address" value={e.vendor_address} conf={c.vendor_address} />
          <Field
            label="VAT ID"
            value={e.vendor_vat_id}
            conf={c.vendor_vat_id}
          />
          <Field label="Invoice no." value={e.invoice_number} conf={c.invoice_number} />
          <Field label="Invoice date" value={e.invoice_date} conf={c.invoice_date} />
          <Field label="Due date" value={e.due_date} conf={c.due_date} />
          <Field label="Customer" value={e.customer_name} conf={c.customer_name} />
          <Field
            label="IBAN"
            value={
              e.iban ? (
                <>
                  <span className="mono" style={{ fontSize: 13 }}>{e.iban}</span>
                  {ibanValid !== null && (
                    <span style={{ marginLeft: 8, color: ibanValid ? "var(--ok)" : "var(--err)", fontSize: 12 }}>
                      {ibanValid ? "✓ checksum" : "✗ checksum"}
                    </span>
                  )}
                </>
              ) : null
            }
            conf={c.iban}
          />
          <Field label="BIC" value={e.bic} conf={c.bic} />
        </div>

        {/* Line items */}
        {e.line_items.length > 0 && (
          <div style={card()}>
            <h3 style={cardTitle()}>Line items</h3>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ color: "var(--muted)", textAlign: "left" }}>
                  <th style={th()}>Description</th>
                  <th style={{ ...th(), textAlign: "right" }}>Qty</th>
                  <th style={{ ...th(), textAlign: "right" }}>Unit</th>
                  <th style={{ ...th(), textAlign: "right" }}>Total</th>
                </tr>
              </thead>
              <tbody>
                {e.line_items.map((li, i) => (
                  <tr key={i} style={{ borderTop: "1px solid var(--border)" }}>
                    <td style={td()}>{li.description}</td>
                    <td style={{ ...td(), textAlign: "right" }}>{li.quantity}</td>
                    <td style={{ ...td(), textAlign: "right" }}>{li.unit_price}</td>
                    <td style={{ ...td(), textAlign: "right" }}>{li.total}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* VAT + totals */}
        <div style={card()}>
          <h3 style={cardTitle()}>MwSt-Aufschlüsselung & totals</h3>
          {e.vat_breakdown.length > 0 ? (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, marginBottom: 10 }}>
              <thead>
                <tr style={{ color: "var(--muted)", textAlign: "left" }}>
                  <th style={th()}>Rate</th>
                  <th style={{ ...th(), textAlign: "right" }}>Base</th>
                  <th style={{ ...th(), textAlign: "right" }}>VAT</th>
                </tr>
              </thead>
              <tbody>
                {e.vat_breakdown.map((v, i) => (
                  <tr key={i} style={{ borderTop: "1px solid var(--border)" }}>
                    <td style={td()}>{v.rate}%</td>
                    <td style={{ ...td(), textAlign: "right" }}>{money(v.base, e.currency)}</td>
                    <td style={{ ...td(), textAlign: "right" }}>{money(v.amount, e.currency)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ color: "var(--muted)", fontSize: 13, margin: "0 0 10px" }}>
              No VAT stated (Kleinunternehmer or reverse charge).
            </p>
          )}
          <Field label="Net total" value={money(e.net_total, e.currency)} conf={c.net_total} />
          <div style={{ display: "flex", justifyContent: "space-between", paddingTop: 6, borderTop: "1px solid var(--border)" }}>
            <span style={{ fontWeight: 600 }}>Gross total</span>
            <span style={{ fontWeight: 700 }}>
              {money(e.gross_total, e.currency)}
              <Dot level={c.gross_total} />
            </span>
          </div>
        </div>

        {/* Validation flags */}
        <div style={card()}>
          <h3 style={cardTitle()}>Validation</h3>
          {errors.length === 0 && warns.length === 0 && (
            <p style={{ color: "var(--ok)", fontSize: 13, margin: 0 }}>✓ All checks passed.</p>
          )}
          {result.validation.flags.map((f: Flag, i) => (
            <div
              key={i}
              style={{
                fontSize: 12.5,
                padding: "6px 10px",
                marginBottom: 6,
                borderRadius: 8,
                background: f.severity === "error" ? "var(--err-soft)" : "var(--warn-soft)",
                color: f.severity === "error" ? "var(--err)" : "var(--warn)",
              }}
            >
              <strong>{f.severity === "error" ? "Error" : "Check"}</strong> · {f.field}: {f.message}
            </div>
          ))}
        </div>

        {/* Pflichtangaben */}
        <div style={card()}>
          <h3 style={cardTitle()}>§14 UStG Pflichtangaben</h3>
          <div style={{ display: "grid", gap: 4 }}>
            {Object.entries(result.validation.pflichtangaben).map(([key, present]) => (
              <div key={key} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13 }}>
                <span style={{ color: present ? "var(--ok)" : "var(--err)", fontWeight: 700, width: 14 }}>
                  {present ? "✓" : "✗"}
                </span>
                <span style={{ color: present ? "var(--ink)" : "var(--muted)" }}>
                  {PFLICHT_LABELS[key] ?? key}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function card(): React.CSSProperties {
  return {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: 14,
    padding: 18,
  };
}
function cardTitle(): React.CSSProperties {
  return {
    margin: "0 0 12px",
    fontSize: 12,
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    color: "var(--muted)",
    fontWeight: 600,
  };
}
function th(): React.CSSProperties {
  return { padding: "4px 6px", fontWeight: 500, fontSize: 12 };
}
function td(): React.CSSProperties {
  return { padding: "6px 6px", verticalAlign: "top" };
}
