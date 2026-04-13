"""Helpers for normalizing flight identifiers across the application."""

import re


def normalize_flight_id(raw_id):
    """Normalize a flight identifier so all comparisons use integers.

    Accepted inputs include numeric values, numeric strings, and codes such as
    "SB800". The function always returns the numeric portion as an integer.
    """
    if raw_id is None:
        raise ValueError("Flight ID is required")

    if isinstance(raw_id, (int, float)):
        return int(raw_id)

    raw_text = str(raw_id).strip()
    if not raw_text:
        raise ValueError("Flight ID is required")

    if raw_text.isdigit():
        return int(raw_text)

    match = re.search(r"(\d+)$", raw_text)
    if match:
        return int(match.group(1))

    raise ValueError(f"Invalid flight ID format: {raw_id}")
