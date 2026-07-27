import sqlite3

DATABASE_NAME = "culinaryops.db"


def inspect_database():
    try:
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """)

        tables = cursor.fetchall()

        if not tables:
            print("No tables were found in the database.")
            return

        for table in tables:
            table_name = table[0]

            print("\n" + "=" * 60)
            print(f"TABLE: {table_name}")
            print("=" * 60)

            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            for column in columns:
                column_id = column[0]
                column_name = column[1]
                data_type = column[2]
                required = column[3]
                default_value = column[4]
                primary_key = column[5]

                print(
                    f"Column {column_id}: "
                    f"name={column_name}, "
                    f"type={data_type}, "
                    f"required={required}, "
                    f"default={default_value}, "
                    f"primary_key={primary_key}"
                )

        connection.close()

    except sqlite3.Error as error:
        print(f"Database error: {error}")


if __name__ == "__main__":
    inspect_database()