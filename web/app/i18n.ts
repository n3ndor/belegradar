export type Lang = "de" | "en";

export interface Strings {
  tagline: string;
  intro: string;
  introStored: string;
  dropPrompt: string;
  dropHint: string;
  extracting: string; // "{name}" placeholder
  samplesPrompt: string;
  numbersOk: string;
  numbersWarn: string;
  tokensLabel: string;
  cached: string;
  copyJson: string;
  downloadJson: string;
  copyCsv: string;
  downloadCsv: string;
  copied: string;
  saved: string;
  rawText: string;
  extractedFields: string;
  vendor: string;
  address: string;
  vatId: string;
  invoiceNo: string;
  invoiceDate: string;
  dueDate: string;
  customer: string;
  iban: string;
  bic: string;
  checksumOk: string;
  checksumBad: string;
  lineItems: string;
  colDescription: string;
  colQty: string;
  colUnit: string;
  colTotal: string;
  vatTotals: string;
  colRate: string;
  colBase: string;
  colVat: string;
  noVat: string;
  netTotal: string;
  grossTotal: string;
  validation: string;
  allPassed: string;
  errorLabel: string;
  checkLabel: string;
  pflichtTitle: string;
  pflicht: Record<string, string>;
  footerPrivacy: string;
  footerEnginePrefix: string;
  footerEngineOnPypi: string;
  footerEngineSource: string;
  switchLabel: string; // shown on the toggle (the OTHER language)
  switchFlag: string;
}

export const STRINGS: Record<Lang, Strings> = {
  de: {
    tagline: "PDF-Rechnung rein, geprüfte Daten raus.",
    intro:
      "Laden Sie eine Rechnung als PDF hoch und erhalten Sie strukturierte Daten: Lieferant, Positionen, MwSt-Aufschlüsselung, Summen, IBAN. Jede Zahl wird im Code geprüft, nicht geraten.",
    introStored: "Nichts wird gespeichert.",
    dropPrompt: "PDF-Rechnung hier ablegen oder klicken zum Auswählen",
    dropHint: "PDFs mit Textebene, max. 4 MB. Scans werden höflich abgelehnt.",
    extracting: "Extrahiere {name}…",
    samplesPrompt: "Oder ein Beispiel testen (kein Upload nötig):",
    numbersOk: "✓ Zahlen stimmen",
    numbersWarn: "⚠ Prüfhinweise beachten",
    tokensLabel: "Tokens",
    cached: "Beispiel",
    copyJson: "JSON kopieren",
    downloadJson: ".json speichern",
    copyCsv: "CSV kopieren",
    downloadCsv: ".csv speichern",
    copied: "✓ Kopiert",
    saved: "✓ Gespeichert",
    rawText: "Roher PDF-Text",
    extractedFields: "Extrahierte Felder",
    vendor: "Lieferant",
    address: "Anschrift",
    vatId: "USt-IdNr.",
    invoiceNo: "Rechnungsnr.",
    invoiceDate: "Rechnungsdatum",
    dueDate: "Fällig bis",
    customer: "Kunde",
    iban: "IBAN",
    bic: "BIC",
    checksumOk: "✓ Prüfsumme",
    checksumBad: "✗ Prüfsumme",
    lineItems: "Positionen",
    colDescription: "Beschreibung",
    colQty: "Menge",
    colUnit: "Einzelpreis",
    colTotal: "Gesamt",
    vatTotals: "MwSt-Aufschlüsselung & Summen",
    colRate: "Satz",
    colBase: "Netto",
    colVat: "MwSt",
    noVat: "Keine MwSt ausgewiesen (Kleinunternehmer oder Reverse Charge).",
    netTotal: "Nettobetrag",
    grossTotal: "Bruttobetrag",
    validation: "Prüfung",
    allPassed: "✓ Alle Prüfungen bestanden.",
    errorLabel: "Fehler",
    checkLabel: "Hinweis",
    pflichtTitle: "§14 UStG Pflichtangaben",
    pflicht: {
      vendor_name_address: "Name und Anschrift des Leistenden",
      vat_id_or_tax_number: "USt-IdNr. oder Steuernummer",
      invoice_date: "Rechnungsdatum",
      invoice_number: "Fortlaufende Rechnungsnummer",
      line_items: "Menge und Art der Leistung",
      net_amount: "Nettobetrag (Entgelt)",
      vat_rate_and_amount: "Steuersatz und Steuerbetrag",
      gross_amount: "Bruttobetrag",
    },
    footerPrivacy:
      "Datenschutz: Uploads werden im Arbeitsspeicher verarbeitet und niemals gespeichert oder protokolliert. Beispielrechnungen sind fiktiv. Dies ist eine Demo, keine Steuerberatung.",
    footerEnginePrefix: "Extraktions-Engine:",
    footerEngineOnPypi: "auf PyPI",
    footerEngineSource: "Quellcode & Genauigkeits-Eval",
    switchLabel: "Read in English",
    switchFlag: "🌐",
  },
  en: {
    tagline: "PDF invoice in, validated data out.",
    intro:
      "Drop an invoice PDF and get structured data back: vendor, line items, VAT breakdown, totals, IBAN. Every number is checked in code, not guessed.",
    introStored: "Nothing is stored.",
    dropPrompt: "Drop a PDF invoice here, or click to choose",
    dropHint: "Text-layer PDFs, max 4 MB. Scans are politely rejected.",
    extracting: "Extracting {name}…",
    samplesPrompt: "Or try a sample (no upload needed):",
    numbersOk: "✓ numbers check out",
    numbersWarn: "⚠ see validation flags",
    tokensLabel: "tokens",
    cached: "sample",
    copyJson: "Copy JSON",
    downloadJson: "Download .json",
    copyCsv: "Copy CSV",
    downloadCsv: "Download .csv",
    copied: "✓ Copied",
    saved: "✓ Saved",
    rawText: "Raw PDF text",
    extractedFields: "Extracted fields",
    vendor: "Vendor",
    address: "Address",
    vatId: "VAT ID",
    invoiceNo: "Invoice no.",
    invoiceDate: "Invoice date",
    dueDate: "Due date",
    customer: "Customer",
    iban: "IBAN",
    bic: "BIC",
    checksumOk: "✓ checksum",
    checksumBad: "✗ checksum",
    lineItems: "Line items",
    colDescription: "Description",
    colQty: "Qty",
    colUnit: "Unit price",
    colTotal: "Total",
    vatTotals: "VAT breakdown & totals",
    colRate: "Rate",
    colBase: "Base",
    colVat: "VAT",
    noVat: "No VAT stated (Kleinunternehmer or reverse charge).",
    netTotal: "Net total",
    grossTotal: "Gross total",
    validation: "Validation",
    allPassed: "✓ All checks passed.",
    errorLabel: "Error",
    checkLabel: "Check",
    pflichtTitle: "§14 UStG mandatory fields",
    pflicht: {
      vendor_name_address: "Name and address of the supplier",
      vat_id_or_tax_number: "VAT ID or tax number",
      invoice_date: "Invoice date",
      invoice_number: "Sequential invoice number",
      line_items: "Quantity and type of goods/services",
      net_amount: "Net amount",
      vat_rate_and_amount: "Tax rate and tax amount",
      gross_amount: "Gross amount",
    },
    footerPrivacy:
      "Privacy: uploads are processed in memory and never stored or logged. Sample invoices are fictional. This is a demo, not tax advice.",
    footerEnginePrefix: "Extraction engine:",
    footerEngineOnPypi: "on PyPI",
    footerEngineSource: "source & accuracy eval",
    switchLabel: "Auf Deutsch lesen",
    switchFlag: "🌐",
  },
};
