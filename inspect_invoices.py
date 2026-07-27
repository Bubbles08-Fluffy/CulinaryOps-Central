import sqlite3

connection = sqlite3.connect("culinaryops.db")
cursor = connection.cursor()

cursor.execute("PRAGMA table_info(Invoices)")
columns = cursor.fetchall()

print("\nInvoices table columns:\n")

for column in columns:
    print(column)

connection.close()