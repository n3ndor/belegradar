export type VatEntry = { rate: string; base: string; amount: string };
export type LineItem = {
  description: string;
  quantity: string;
  unit_price: string;
  total: string;
};

export type Extraction = {
  vendor_name: string;
  vendor_address: string | null;
  vendor_vat_id: string | null;
  invoice_number: string;
  invoice_date: string | null;
  due_date: string | null;
  customer_name: string | null;
  line_items: LineItem[];
  net_total: string | null;
  vat_breakdown: VatEntry[];
  gross_total: string | null;
  currency: string;
  iban: string | null;
  bic: string | null;
  payment_terms: string | null;
  confidence: Record<string, "high" | "medium" | "low">;
};

export type Flag = { field: string; severity: "error" | "warn"; message: string };

export type Result = {
  ok: true;
  extraction: Extraction;
  validation: {
    ok: boolean;
    flags: Flag[];
    pflichtangaben: Record<string, boolean>;
  };
  raw_text: string;
  tokens: number;
};

export type ApiError = { ok: false; error: string; kind: string };
