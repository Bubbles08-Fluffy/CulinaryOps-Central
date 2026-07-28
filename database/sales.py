"""Database operations for the Sales module."""

import sqlite3
from datetime import datetime

from database.database import connect_database


def _ensure_sales_table():
    """Create or upgrade the sales_records table for the current Sales page."""
    connection = connect_database()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name = 'sales_records'
            """
        )
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            cursor.execute(
                """
                CREATE TABLE sales_records (
                    salesID INTEGER PRIMARY KEY AUTOINCREMENT,
                    salesDate TEXT NOT NULL,
                    mealsSold INTEGER NOT NULL,
                    totalRevenue REAL NOT NULL
                )
                """
            )
            connection.commit()
            return

        cursor.execute("PRAGMA table_info(sales_records)")
        columns = {row[1] for row in cursor.fetchall()}

        required_columns = {
            "salesID",
            "salesDate",
            "mealsSold",
            "totalRevenue",
        }

        if required_columns.issubset(columns):
            return

        # Preserve records from the project's original sales table structure.
        cursor.execute("ALTER TABLE sales_records RENAME TO sales_records_old")
        cursor.execute(
            """
            CREATE TABLE sales_records (
                salesID INTEGER PRIMARY KEY AUTOINCREMENT,
                salesDate TEXT NOT NULL,
                mealsSold INTEGER NOT NULL,
                totalRevenue REAL NOT NULL
            )
            """
        )

        old_columns = columns

        if {"salesID", "salesDate", "mealID", "totalSales"}.issubset(old_columns):
            cursor.execute(
                """
                INSERT INTO sales_records (
                    salesID,
                    salesDate,
                    mealsSold,
                    totalRevenue
                )
                SELECT
                    s.salesID,
                    s.salesDate,
                    COALESCE(
                        m.breakfastCount + m.lunchCount + m.dinnerCount,
                        0
                    ),
                    s.totalSales
                FROM sales_records_old AS s
                LEFT JOIN meal_counts AS m
                    ON s.mealID = m.mealID
                """
            )
        elif {"salesID", "salesDate", "mealsSold", "totalSales"}.issubset(old_columns):
            cursor.execute(
                """
                INSERT INTO sales_records (
                    salesID,
                    salesDate,
                    mealsSold,
                    totalRevenue
                )
                SELECT salesID, salesDate, mealsSold, totalSales
                FROM sales_records_old
                """
            )

        cursor.execute("DROP TABLE sales_records_old")
        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_all_sales():
    """Return all sales records ordered by newest date and ID."""
    _ensure_sales_table()

    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT salesID, salesDate, mealsSold, totalRevenue
        FROM sales_records
        ORDER BY salesDate DESC, salesID DESC
        """
    )
    sales = cursor.fetchall()
    connection.close()
    return sales


def add_sale(sales_date, meals_sold, total_revenue):
    """Add a sales record and return (success, message)."""
    valid, result = _validate_sales_values(
        sales_date,
        meals_sold,
        total_revenue,
    )

    if not valid:
        return False, result

    sales_date, meals_sold, total_revenue = result
    connection = None

    try:
        _ensure_sales_table()
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO sales_records (
                salesDate,
                mealsSold,
                totalRevenue
            )
            VALUES (?, ?, ?)
            """,
            (
                sales_date,
                meals_sold,
                total_revenue,
            ),
        )
        connection.commit()
        return True, "Sales record added successfully."

    except sqlite3.Error as error:
        return False, f"Unable to add sales record: {error}"

    finally:
        if connection is not None:
            connection.close()


def update_sale(sales_id, sales_date, meals_sold, total_revenue):
    """Update a sales record and return (success, message)."""
    valid, result = _validate_sales_values(
        sales_date,
        meals_sold,
        total_revenue,
    )

    if not valid:
        return False, result

    sales_date, meals_sold, total_revenue = result
    connection = None

    try:
        _ensure_sales_table()
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE sales_records
            SET salesDate = ?,
                mealsSold = ?,
                totalRevenue = ?
            WHERE salesID = ?
            """,
            (
                sales_date,
                meals_sold,
                total_revenue,
                sales_id,
            ),
        )

        if cursor.rowcount == 0:
            return False, "Sales record was not found."

        connection.commit()
        return True, "Sales record updated successfully."

    except sqlite3.Error as error:
        return False, f"Unable to update sales record: {error}"

    finally:
        if connection is not None:
            connection.close()


def delete_sale(sales_id):
    """Delete a sales record and return (success, message)."""
    connection = None

    try:
        _ensure_sales_table()
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM sales_records WHERE salesID = ?",
            (sales_id,),
        )

        if cursor.rowcount == 0:
            return False, "Sales record was not found."

        connection.commit()
        return True, "Sales record deleted successfully."

    except sqlite3.Error as error:
        return False, f"Unable to delete sales record: {error}"

    finally:
        if connection is not None:
            connection.close()


def search_sales(keyword):
    """Search sales by ID, date, meals sold, or revenue."""
    _ensure_sales_table()

    keyword = keyword.strip()

    if not keyword:
        return get_all_sales()

    connection = connect_database()
    cursor = connection.cursor()
    search_value = f"%{keyword}%"

    cursor.execute(
        """
        SELECT salesID, salesDate, mealsSold, totalRevenue
        FROM sales_records
        WHERE CAST(salesID AS TEXT) LIKE ?
           OR salesDate LIKE ?
           OR CAST(mealsSold AS TEXT) LIKE ?
           OR CAST(totalRevenue AS TEXT) LIKE ?
        ORDER BY salesDate DESC, salesID DESC
        """,
        (
            search_value,
            search_value,
            search_value,
            search_value,
        ),
    )

    sales = cursor.fetchall()
    connection.close()
    return sales


def count_sales():
    """Return the number of sales records."""
    _ensure_sales_table()

    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales_records")
    row = cursor.fetchone()
    total = row[0] if row is not None else 0
    connection.close()
    return total


def get_total_sales():
    """Return the sum of all recorded revenue."""
    _ensure_sales_table()

    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(totalRevenue), 0) FROM sales_records"
    )
    row = cursor.fetchone()
    total = float(row[0]) if row is not None else 0.0
    connection.close()
    return total


def get_total_meals_sold():
    """Return the sum of meals sold across all sales records."""
    _ensure_sales_table()

    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COALESCE(SUM(mealsSold), 0) FROM sales_records"
    )
    row = cursor.fetchone()
    total = int(row[0]) if row is not None else 0
    connection.close()
    return total


def _validate_sales_values(sales_date, meals_sold, total_revenue):
    sales_date = sales_date.strip()

    if not sales_date:
        return False, "Sale date is required."

    try:
        datetime.strptime(sales_date, "%Y-%m-%d")
    except ValueError:
        return False, "Sale date must use the YYYY-MM-DD format."

    meals_sold = str(meals_sold).strip()

    if not meals_sold:
        return False, "Meals sold is required."

    try:
        meals_sold_number = int(meals_sold)
    except ValueError:
        return False, "Meals sold must be a whole number."

    if meals_sold_number < 0:
        return False, "Meals sold cannot be negative."

    revenue_text = str(total_revenue).strip().replace("$", "").replace(",", "")

    if not revenue_text:
        return False, "Total revenue is required."

    try:
        revenue_number = float(revenue_text)
    except ValueError:
        return False, "Total revenue must be a valid number."

    if revenue_number < 0:
        return False, "Total revenue cannot be negative."

    return True, (
        sales_date,
        meals_sold_number,
        round(revenue_number, 2),
    )


# Make sure the table is ready when this module is imported.
_ensure_sales_table()
