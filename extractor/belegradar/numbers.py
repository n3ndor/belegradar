"""Deterministic number normalization.

German invoices write 1.234,56; English ones write 1,234.56. The LLM is
never trusted with arithmetic or locale conversion: amounts are normalized
here, before and after extraction, with plain rules.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

_CLEAN_RE = re.compile(r"[^\d,.\-]")


def parse_amount(value: str | int | float | Decimal | None) -> Decimal | None:
    """Parse an amount in German (1.234,56) or English (1,234.56) format.

    The last separator wins as the decimal mark; the other is treated as a
    thousands separator. A single separator followed by exactly two digits
    is a decimal mark; followed by exactly three digits it is ambiguous and
    treated as thousands only for '.', matching German conventions.
    """
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))

    text = _CLEAN_RE.sub("", value.strip())
    if not text or text in {"-", ",", "."}:
        return None

    has_comma, has_dot = "," in text, "." in text
    try:
        if has_comma and has_dot:
            # Last separator is the decimal mark.
            if text.rfind(",") > text.rfind("."):
                text = text.replace(".", "").replace(",", ".")
            else:
                text = text.replace(",", "")
        elif has_comma:
            if text.count(",") > 1:
                text = text.replace(",", "")  # 1,234,567 English thousands
            else:
                head, _, tail = text.rpartition(",")
                if len(tail) == 3 and head:
                    text = text.replace(",", "")  # 1,234 English thousands
                else:
                    text = text.replace(",", ".")  # 12,34 German decimal
        elif has_dot:
            if text.count(".") > 1:
                text = text.replace(".", "")  # 1.234.567 German thousands
            else:
                head, _, tail = text.rpartition(".")
                if len(tail) == 3 and head:
                    text = text.replace(".", "")  # 1.234 German thousands
                # else: decimal dot, leave as is
        return Decimal(text)
    except InvalidOperation:
        return None
