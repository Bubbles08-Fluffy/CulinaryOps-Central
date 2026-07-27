import sqlite3

from database.database import connect_database


def get_all_vendors():
    """
    Returns every vendor ordered alphabetically by vendor name.
    """

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT vendorID, vendorName, contactName, phoneNumber, email
        FROM vendors
        ORDER BY vendorName
        """
    )

    vendors = cursor.fetchall()
    connection.close()

    return vendors


def add_vendor(vendor_name, contact_name="", phone_number="", email=""):
    """
    Adds a new vendor to the database.

    Returns:
        tuple: (success, message)
    """

    vendor_name = vendor_name.strip()
    contact_name = contact_name.strip()
    phone_number = phone_number.strip()
    email = email.strip()

    if not vendor_name:
        return False, "Vendor name is required."

    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO vendors (
                vendorName,
                contactName,
                phoneNumber,
                email
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                vendor_name,
                contact_name,
                phone_number,
                email,
            ),
        )

        connection.commit()

        return True, "Vendor added successfully."

    except sqlite3.Error as error:
        return False, f"Unable to add vendor: {error}"

    finally:
        if connection is not None:
            connection.close()


def update_vendor(
    vendor_id,
    vendor_name,
    contact_name="",
    phone_number="",
    email="",
):
    """
    Updates an existing vendor.

    Returns:
        tuple: (success, message)
    """

    vendor_name = vendor_name.strip()
    contact_name = contact_name.strip()
    phone_number = phone_number.strip()
    email = email.strip()

    if not vendor_name:
        return False, "Vendor name is required."

    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE vendors
            SET vendorName = ?,
                contactName = ?,
                phoneNumber = ?,
                email = ?
            WHERE vendorID = ?
            """,
            (
                vendor_name,
                contact_name,
                phone_number,
                email,
                vendor_id,
            ),
        )

        if cursor.rowcount == 0:
            return False, "Vendor was not found."

        connection.commit()

        return True, "Vendor updated successfully."

    except sqlite3.Error as error:
        return False, f"Unable to update vendor: {error}"

    finally:
        if connection is not None:
            connection.close()


def delete_vendor(vendor_id):
    """
    Deletes a vendor using its vendor ID.

    Returns:
        tuple: (success, message)
    """

    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM vendors
            WHERE vendorID = ?
            """,
            (vendor_id,),
        )

        if cursor.rowcount == 0:
            return False, "Vendor was not found."

        connection.commit()

        return True, "Vendor deleted successfully."

    except sqlite3.IntegrityError:
        return (
            False,
            "This vendor cannot be deleted because it is connected "
            "to one or more invoices.",
        )

    except sqlite3.Error as error:
        return False, f"Unable to delete vendor: {error}"

    finally:
        if connection is not None:
            connection.close()


def search_vendors(keyword):
    """
    Searches vendor name, contact name, phone number, and email.
    """

    keyword = keyword.strip()

    if not keyword:
        return get_all_vendors()

    connection = connect_database()
    cursor = connection.cursor()

    search_value = f"%{keyword}%"

    cursor.execute(
        """
        SELECT vendorID, vendorName, contactName, phoneNumber, email
        FROM vendors
        WHERE vendorName LIKE ?
           OR contactName LIKE ?
           OR phoneNumber LIKE ?
           OR email LIKE ?
        ORDER BY vendorName
        """,
        (
            search_value,
            search_value,
            search_value,
            search_value,
        ),
    )

    vendors = cursor.fetchall()
    connection.close()

    return vendors


def get_vendor_by_id(vendor_id):
    """
    Returns one vendor by ID.
    """

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT vendorID, vendorName, contactName, phoneNumber, email
        FROM vendors
        WHERE vendorID = ?
        """,
        (vendor_id,),
    )

    vendor = cursor.fetchone()
    connection.close()

    return vendor


def count_vendors():
    """
    Returns the total number of vendors.
    """

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM vendors")

    total = cursor.fetchone()[0]
    connection.close()

    return total