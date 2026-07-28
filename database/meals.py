import sqlite3
from datetime import datetime

from database.database import connect_database


def get_all_meals():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT mealID, mealDate, breakfastCount, lunchCount, dinnerCount
        FROM meal_counts
        ORDER BY mealDate DESC, mealID DESC
        """
    )
    meals = cursor.fetchall()
    connection.close()
    return meals


def add_meal(meal_date, breakfast_count, lunch_count, dinner_count):
    valid, result = _validate_meal_values(
        meal_date,
        breakfast_count,
        lunch_count,
        dinner_count,
    )
    if not valid:
        return False, result

    meal_date, breakfast_count, lunch_count, dinner_count = result
    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO meal_counts (
                mealDate,
                breakfastCount,
                lunchCount,
                dinnerCount
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                meal_date,
                breakfast_count,
                lunch_count,
                dinner_count,
            ),
        )
        connection.commit()
        return True, "Meal count record added successfully."

    except sqlite3.IntegrityError as error:
        return False, f"Unable to add meal count record: {error}"
    except sqlite3.Error as error:
        return False, f"Unable to add meal count record: {error}"
    finally:
        if connection is not None:
            connection.close()


def update_meal(meal_id, meal_date, breakfast_count, lunch_count, dinner_count):
    valid, result = _validate_meal_values(
        meal_date,
        breakfast_count,
        lunch_count,
        dinner_count,
    )
    if not valid:
        return False, result

    meal_date, breakfast_count, lunch_count, dinner_count = result
    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE meal_counts
            SET mealDate = ?,
                breakfastCount = ?,
                lunchCount = ?,
                dinnerCount = ?
            WHERE mealID = ?
            """,
            (
                meal_date,
                breakfast_count,
                lunch_count,
                dinner_count,
                meal_id,
            ),
        )

        if cursor.rowcount == 0:
            return False, "Meal count record was not found."

        connection.commit()
        return True, "Meal count record updated successfully."

    except sqlite3.Error as error:
        return False, f"Unable to update meal count record: {error}"
    finally:
        if connection is not None:
            connection.close()


def delete_meal(meal_id):
    connection = None

    try:
        connection = connect_database()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM meal_counts WHERE mealID = ?",
            (meal_id,),
        )

        if cursor.rowcount == 0:
            return False, "Meal count record was not found."

        connection.commit()
        return True, "Meal count record deleted successfully."

    except sqlite3.IntegrityError:
        return (
            False,
            "This meal count record cannot be deleted because it is connected "
            "to a sales record.",
        )
    except sqlite3.Error as error:
        return False, f"Unable to delete meal count record: {error}"
    finally:
        if connection is not None:
            connection.close()


def search_meals(keyword):
    keyword = keyword.strip()
    if not keyword:
        return get_all_meals()

    connection = connect_database()
    cursor = connection.cursor()
    search_value = f"%{keyword}%"

    cursor.execute(
        """
        SELECT mealID, mealDate, breakfastCount, lunchCount, dinnerCount
        FROM meal_counts
        WHERE CAST(mealID AS TEXT) LIKE ?
           OR mealDate LIKE ?
           OR CAST(breakfastCount AS TEXT) LIKE ?
           OR CAST(lunchCount AS TEXT) LIKE ?
           OR CAST(dinnerCount AS TEXT) LIKE ?
        ORDER BY mealDate DESC, mealID DESC
        """,
        (
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
        ),
    )

    meals = cursor.fetchall()
    connection.close()
    return meals


def count_meals():
    connection = connect_database()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM meal_counts")
    row = cursor.fetchone()
    total = row[0] if row is not None else 0
    connection.close()
    return total


def _validate_meal_values(
    meal_date,
    breakfast_count,
    lunch_count,
    dinner_count,
):
    meal_date = meal_date.strip()

    if not meal_date:
        return False, "Meal date is required."

    try:
        datetime.strptime(meal_date, "%Y-%m-%d")
    except ValueError:
        return False, "Meal date must use the YYYY-MM-DD format."

    count_values = []
    for label, value in (
        ("Breakfast count", breakfast_count),
        ("Lunch count", lunch_count),
        ("Dinner count", dinner_count),
    ):
        value = value.strip()
        if not value:
            return False, f"{label} is required."

        try:
            number = int(value)
        except ValueError:
            return False, f"{label} must be a whole number."

        if number < 0:
            return False, f"{label} cannot be negative."

        count_values.append(number)

    return True, (
        meal_date,
        count_values[0],
        count_values[1],
        count_values[2],
    )
