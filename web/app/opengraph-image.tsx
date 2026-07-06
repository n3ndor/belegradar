import { ImageResponse } from "next/og";

export const alt = "BelegRadar — PDF invoice to validated data";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          background: "#f6f7f9",
          padding: "72px",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: 16,
              background: "#4f46e5",
              color: "#fff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 38,
              fontWeight: 700,
            }}
          >
            B
          </div>
          <div style={{ fontSize: 34, fontWeight: 700, color: "#1a1f2b" }}>BelegRadar</div>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 68, fontWeight: 800, color: "#1a1f2b", lineHeight: 1.05, letterSpacing: -2 }}>
            PDF-Rechnung rein,
          </div>
          <div style={{ fontSize: 68, fontWeight: 800, color: "#4f46e5", lineHeight: 1.05, letterSpacing: -2 }}>
            geprüfte Daten raus.
          </div>
          <div style={{ fontSize: 30, color: "#667085", marginTop: 28 }}>
            MwSt-Aufschlüsselung · IBAN-Prüfsumme · §14 UStG · JSON / CSV Export
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 600, color: "#4f46e5" }}>beleg.nagysolution.com</div>
          <div style={{ fontSize: 24, color: "#667085" }}>Nichts wird gespeichert · 0€/Monat</div>
        </div>
      </div>
    ),
    size,
  );
}
