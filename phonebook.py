import psycopg2
import csv

def run_query(sql, params=None, is_select=False):
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="12345678",
        host="127.0.0.1",
        port="5432"
    )
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    
    result = None
    if is_select:
        result = cursor.fetchall()
    else:
        conn.commit()
        result = cursor.rowcount
        
    cursor.close()
    conn.close()
    return result

def init_db():
    run_query("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            name TEXT,
            phone TEXT
        )
    """)

def insert_from_csv(file_path):
    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)
            reader = csv.reader(f, dialect)
            for row in reader:
                if len(row) >= 2:
                    run_query("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (row[0], row[1]))
        print("Import successful.")
    except Exception as e:
        print(f"Error: {e}")

def add_contact():
    name = input("Enter Name: ")
    phone = input("Enter Phone: ")
    run_query("INSERT INTO phonebook (name, phone) VALUES (%s, %s)", (name, phone))
    print("Added.")

def show_all():
    rows = run_query("SELECT id, name, phone FROM phonebook ORDER BY id", is_select=True)
    if not rows:
        print("Empty.")
    for r in rows:
        print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")

def query_contacts():
    print("1. Name | 2. Phone Prefix")
    choice = input("> ")
    if choice == "1":
        val = input("Name: ")
        rows = run_query("SELECT id, name, phone FROM phonebook WHERE name ILIKE %s", (f"%{val}%",), True)
    else:
        val = input("Prefix: ")
        rows = run_query("SELECT id, name, phone FROM phonebook WHERE phone LIKE %s", (f"{val}%",), True)
    
    for r in rows:
        print(f"ID: {r[0]} | Name: {r[1]} | Phone: {r[2]}")

def delete_contact():
    print("1. Name | 2. Phone")
    choice = input("> ")
    field = "name" if choice == "1" else "phone"
    val = input("Value: ")
    count = run_query(f"DELETE FROM phonebook WHERE {field} = %s", (val,))
    print(f"Deleted: {count}")

def main():
    init_db()
    while True:
        print("\n1. CSV | 2. Add | 3. Search | 4. Delete | 5. Show All | 6. Exit")
        c = input("Choice: ")
        if c == "1": insert_from_csv(input("Path: "))
        elif c == "2": add_contact()
        elif c == "3": query_contacts()
        elif c == "4": delete_contact()
        elif c == "5": show_all()
        elif c == "6": break

if __name__ == "__main__":
    main()