"""
Database operations for the Invoices module.

This file manages invoice records and connects invoices to vendors
through the vendorID foreign-key field.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


DATABASE_PATH = Path(__file__).resolve().parent.parent / "culinaryops.db"
VALID_STATUSES = {"Pending", "Paid"}


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _validate_invoice_date(invoice_date: str) -> str:
    """Validate and return a date in YYYY-MM-DD format."""
    cleaned_date = invoice_date.strip()

    try:
        datetime.strptime(cleaned_date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(
            "Invoice date must use the YYYY-MM-DD format."
        ) from exc

    return cleaned_date


def _validate_amount(amount: Any) -> float:
    """Validate and return a positive invoice amount."""
    try:
        cleaned_amount = float(amount)
    except (TypeError, ValueError) as exc:
        raise ValueError("Invoice amount must be a valid number.") from exc

    if cleaned_amount <= 0:
        raise ValueError("Invoice amount must be greater than zero.")

    return round(cleaned_amount, 2)


def _validate_status(status: str) -> str:
    """Validate and return an approved invoice status."""
    cleaned_status = status.strip().title()

    if cleaned_status not in VALID_STATUSES:
        raise ValueError("Status must be either Pending or Paid.")

    return cleaned_status


def _vendor_exists(connection: sqlite3.Connection, vendor_id: int) -> bool:
    """Return True when the selected vendor exists."""
    row = connection.execute(
        "SELECT 1 FROM Vendors WHERE vendorID = ?",
        (vendor_id,),
    ).fetchone()

    return row is not None


def get_vendor_options() -> list[tuple[int, str]]:
    """
    Return vendor IDs and names for the invoice vendor dropdown.

    Example:
        [(1, "Fresh Foods LLC"), (2, "Metro Supply")]
    """
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT vendorID, vendorName
            FROM Vendors
            ORDER BY vendorName COLLATE NOCASE
            """
        ).fetchall()

    return [(int(row["vendorID"]), str(row["vendorName"])) for row in rows]


def get_all_invoices() -> list[dict[str, Any]]:
    """Return every invoice with its related vendor name."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                i.invoiceID,
                i.vendorID,
                v.vendorName,
                i.invoiceDate,
                i.amount,
                i.status
            FROM Invoices AS i
            INNER JOIN Vendors AS v
                ON i.vendorID = v.vendorID
            ORDER BY i.invoiceDate DESC, i.invoiceID DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_invoice_by_id(invoice_id: int) -> dict[str, Any] | None:
    """Return one invoice by ID, including the vendor name."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                i.invoiceID,
                i.vendorID,
                v.vendorName,
                i.invoiceDate,
                i.amount,
                i.status
            FROM Invoices AS i
            INNER JOIN Vendors AS v
                ON i.vendorID = v.vendorID
            WHERE i.invoiceID = ?
            """,
            (invoice_id,),
        ).fetchone()

    return dict(row) if row else None


def add_invoice(
    vendor_id: int,
    invoice_date: str,
    amount: Any,
    status: str,
) -> int:
    """Add an invoice and return the newly created invoice ID."""
    cleaned_date = _validate_invoice_date(invoice_date)
    cleaned_amount = _validate_amount(amount)
    cleaned_status = _validate_status(status)

    with get_connection() as connection:
        if not _vendor_exists(connection, vendor_id):
            raise ValueError("Please select a valid vendor.")

        cursor = connection.execute(
            """
            INSERT INTO Invoices (
                vendorID,
                invoiceDate,
                amount,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                vendor_id,
                cleaned_date,
                cleaned_amount,
                cleaned_status,
            ),
        )

        connection.commit()
        return int(cursor.lastrowid)


def update_invoice(
    invoice_id: int,
    vendor_id: int,
    invoice_date: str,
    amount: Any,
    status: str,
) -> bool:
    """Update an existing invoice and return True when successful."""
    cleaned_date = _validate_invoice_date(invoice_date)
    cleaned_amount = _validate_amount(amount)
    cleaned_status = _validate_status(status)

    with get_connection() as connection:
        if not _vendor_exists(connection, vendor_id):
            raise ValueError("Please select a valid vendor.")

        cursor = connection.execute(
            """
            UPDATE Invoices
            SET
                vendorID = ?,
                invoiceDate = ?,
                amount = ?,
                status = ?
            WHERE invoiceID = ?
            """,
            (
                vendor_id,
                cleaned_date,
                cleaned_amount,
                cleaned_status,
                invoice_id,
            ),
        )

        connection.commit()
        return cursor.rowcount > 0


def delete_invoice(invoice_id: int) -> bool:
    """Delete an invoice and return True when successful."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM Invoices WHERE invoiceID = ?",
            (invoice_id,),
        )

        connection.commit()
        return cursor.rowcount > 0


def search_invoices(search_term: str) -> list[dict[str, Any]]:
    """
    Search invoices by ID, vendor, date, amount, or status.
    """
    cleaned_term = search_term.strip()

    if not cleaned_term:
        return get_all_invoices()

    wildcard = f"%{cleaned_term}%"

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                i.invoiceID,
                i.vendorID,
                v.vendorName,
                i.invoiceDate,
                i.amount,
                i.status
            FROM Invoices AS i
            INNER JOIN Vendors AS v
                ON i.vendorID = v.vendorID
            WHERE
                CAST(i.invoiceID AS TEXT) LIKE ?
                OR v.vendorName LIKE ?
                OR i.invoiceDate LIKE ?
                OR CAST(i.amount AS TEXT) LIKE ?
                OR i.status LIKE ?
            ORDER BY i.invoiceDate DESC, i.invoiceID DESC
            """,
            (
                wildcard,
                wildcard,
                wildcard,
                wildcard,
                wildcard,
            ),
        ).fetchall()

    return [dict(row) for row in rows]


def count_invoices() -> int:
    """Return the total number of invoice records."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT COUNT(*) AS total FROM Invoices"
        ).fetchone()

    return int(row["total"])


def count_pending_invoices() -> int:
    """Return the number of invoices currently marked Pending."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM Invoices
            WHERE LOWER(status) = 'pending'
            """
        ).fetchone()

    return int(row["total"])


def total_invoice_amount() -> float:
    """Return the combined value of all invoices."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM Invoices
            """
        ).fetchone()

    return float(row["total"])
