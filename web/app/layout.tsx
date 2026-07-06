import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BelegRadar — PDF-Rechnung zu geprüften Daten",
  description:
    "Drop a PDF invoice, get validated structured data back: VAT breakdown, IBAN checksum, USt-IdNr, and a §14 UStG Pflichtangaben check. Nothing is stored.",
  metadataBase: new URL("https://beleg.nagysolution.com"),
  openGraph: {
    title: "BelegRadar",
    description:
      "PDF-Rechnung rein, geprüfte JSON-Daten raus. MwSt-Aufschlüsselung, IBAN-Prüfung, §14 UStG. Nichts wird gespeichert.",
    url: "https://beleg.nagysolution.com",
    siteName: "BelegRadar",
    type: "website",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>{children}</body>
    </html>
  );
}
