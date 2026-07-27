import sqlite3
from datetime import datetime

from database.database import connect_database


def get_all_employees():
    """
    Returns all employees ordered alphabetically by last name,
    then first name.
    """

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            employeeID,
            firstName,
            lastName,
            position,
            hireDate,
            phoneNumber
        FROM employees
        ORDER BY lastName, firstName
        """
    )

    employees = cursor.fetchall()
    connection.close()

    return employees


def add_employee(
    first_name,
    last_name,
    position="",
    hire_date="",
    phone_number="",
):
    """
    Adds a new employee.

    Returns:
        tuple: (success, message)
    """

    first_name = first_name.strip()
    last_name = last_name.strip()
    position = position.strip()
    hire_date = hire_date.strip()
    phone_number = phone_number.strip()

    if not first_name:
        return False, "First name is required."

    if not last_name:
        return False, "Last name is required."

    if hire_date and not _is_valid_date(hire_date):
        return False, "Hire date must use the YYYY-MM-DD format."

    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO employees (
                firstName,
                lastName,
                position,
                hireDate,
                phoneNumber
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                first_name,
                last_name,
                position,
                hire_date,
                phone_number,
            ),
        )

        connection.commit()

        return True, "Employee added successfully."

    except sqlite3.Error as error:
        return False, f"Unable to add employee: {error}"

    finally:
        if connection is not None:
            connection.close()


def update_employee(
    employee_id,
    first_name,
    last_name,
    position="",
    hire_date="",
    phone_number="",
):
    """
    Updates an existing employee.

    Returns:
        tuple: (success, message)
    """

    first_name = first_name.strip()
    last_name = last_name.strip()
    position = position.strip()
    hire_date = hire_date.strip()
    phone_number = phone_number.strip()

    if not first_name:
        return False, "First name is required."

    if not last_name:
        return False, "Last name is required."

    if hire_date and not _is_valid_date(hire_date):
        return False, "Hire date must use the YYYY-MM-DD format."

    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE employees
            SET firstName = ?,
                lastName = ?,
                position = ?,
                hireDate = ?,
                phoneNumber = ?
            WHERE employeeID = ?
            """,
            (
                first_name,
                last_name,
                position,
                hire_date,
                phone_number,
                employee_id,
            ),
        )

        if cursor.rowcount == 0:
            return False, "Employee was not found."

        connection.commit()

        return True, "Employee updated successfully."

    except sqlite3.Error as error:
        return False, f"Unable to update employee: {error}"

    finally:
        if connection is not None:
            connection.close()


def delete_employee(employee_id):
    """
    Deletes an employee by employee ID.

    Returns:
        tuple: (success, message)
    """

    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM employees
            WHERE employeeID = ?
            """,
            (employee_id,),
        )

        if cursor.rowcount == 0:
            return False, "Employee was not found."

        connection.commit()

        return True, "Employee deleted successfully."

    except sqlite3.IntegrityError:
        return (
            False,
            "This employee cannot be deleted because the record is "
            "connected to other database information.",
        )

    except sqlite3.Error as error:
        return False, f"Unable to delete employee: {error}"

    finally:
        if connection is not None:
            connection.close()


def search_employees(keyword):
    """
    Searches employee name, position, hire date, and phone number.
    """

    keyword = keyword.strip()

    if not keyword:
        return get_all_employees()

    connection = connect_database()
    cursor = connection.cursor()

    search_value = f"%{keyword}%"

    cursor.execute(
        """
        SELECT
            employeeID,
            firstName,
            lastName,
            position,
            hireDate,
            phoneNumber
        FROM employees
        WHERE firstName LIKE ?
           OR lastName LIKE ?
           OR (firstName || ' ' || lastName) LIKE ?
           OR position LIKE ?
           OR hireDate LIKE ?
           OR phoneNumber LIKE ?
        ORDER BY lastName, firstName
        """,
        (
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
        ),
    )

    employees = cursor.fetchall()
    connection.close()

    return employees


def get_employee_by_id(employee_id):
    """
    Returns one employee by employee ID.
    """

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            employeeID,
            firstName,
            lastName,
            position,
            hireDate,
            phoneNumber
        FROM employees
        WHERE employeeID = ?
        """,
        (employee_id,),
    )

    employee = cursor.fetchone()
    connection.close()

    return employee


def count_employees():
    """
    Returns the total number of employees.
    """

    connection = connect_database()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM employees")

    total = cursor.fetchone()[0]
    connection.close()

    return total


def _is_valid_date(date_text):
    """
    Checks whether a date uses the YYYY-MM-DD format.
    """

    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False
