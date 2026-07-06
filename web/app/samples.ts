import type { Lang } from "./i18n";

export type Sample = {
  id: string;
  label: string;
  flag: string;
  note: Record<Lang, string>;
};

// The sample gallery: fake invoices bundled so visitors never need to upload
// anything real. PDFs live in /public/samples (from extractor/samples/generate.py);
// their extraction results are pre-computed in /public/samples/results.json.
export const SAMPLES: Sample[] = [
  { id: "01_de_simple", label: "Schreiner & Sohn", flag: "🇩🇪", note: { de: "Standard 19%", en: "Standard 19% invoice" } },
  { id: "02_de_7pct", label: "Buchhandlung Lesezeit", flag: "🇩🇪", note: { de: "Bücher, 7% ermäßigt", en: "Books, 7% reduced rate" } },
  { id: "03_de_mixed_rates", label: "Gasthaus zur Linde", flag: "🇩🇪", note: { de: "Gemischt 7% + 19%", en: "Mixed 7% + 19% (catering)" } },
  { id: "04_de_discount", label: "BüroTech Handels", flag: "🇩🇪", note: { de: "Mit Rabattzeile", en: "With a discount line" } },
  { id: "05_de_kleinunternehmer", label: "Fotografie Bergmann", flag: "🇩🇪", note: { de: "Kleinunternehmer, 0% (§19)", en: "Kleinunternehmer, 0% VAT (§19)" } },
  { id: "06_de_gutschrift", label: "BüroTech Gutschrift", flag: "🇩🇪", note: { de: "Gutschrift, negative Beträge", en: "Credit note, negative amounts" } },
  { id: "07_de_no_iban", label: "Nachhilfe Institut Klug", flag: "🇩🇪", note: { de: "Keine IBAN (Lastschrift)", en: "No IBAN (SEPA direct debit)" } },
  { id: "08_at_20pct", label: "Alpenblick Software", flag: "🇦🇹", note: { de: "Österreich, 20% + ATU", en: "Austrian, 20% + ATU VAT id" } },
  { id: "09_en_nl_vat", label: "Windmill Digital B.V.", flag: "🇳🇱", note: { de: "Englisch, NL 21%", en: "English, Dutch 21% VAT" } },
  { id: "10_en_uk", label: "Thames Analytics Ltd", flag: "🇬🇧", note: { de: "Englisch, UK 20%", en: "English, UK 20% VAT" } },
  { id: "11_en_usd_novat", label: "Prairie Cloud Services", flag: "🇺🇸", note: { de: "USD, Reverse Charge", en: "USD, reverse charge (no VAT)" } },
  { id: "12_de_thousands", label: "Stahlbau Krämer AG", flag: "🇩🇪", note: { de: "Große Beträge, 1.234,56", en: "Large amounts, 1.234,56 format" } },
  { id: "13_de_freelancer", label: "Jonas Winter IT", flag: "🇩🇪", note: { de: "Freelancer, Stundensatz", en: "Freelancer, hourly billing" } },
  { id: "14_en_fractions", label: "Beacon Legal Translations", flag: "🇧🇪", note: { de: "Teilmengen", en: "Fractional quantities" } },
  { id: "15_de_utility", label: "Stadtwerke Sonnenfeld", flag: "🇩🇪", note: { de: "Versorger, kleine Preise", en: "Utility bill, small unit prices" } },
  { id: "16_en_mixed", label: "Fjord Consulting ApS", flag: "🇩🇰", note: { de: "Englisch, DK 25%", en: "English, Danish 25% VAT" } },
];
