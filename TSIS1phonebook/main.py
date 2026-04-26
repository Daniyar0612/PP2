import json
import csv
import sys
from phonebook import (
    get_contacts_paginated, filter_by_group, search_by_email,
    call_add_phone, call_move_to_group, call_search_contacts,
    insert_contact, contact_exists, update_contact, get_all_data_for_export
)

def pagination_menu():
    limit = 5
    offset = 0
    sort_by = 'name'
    
    while True:
        results = get_contacts_paginated(limit, offset, sort_by)
        print("\n--- Contacts ---")
        for r in results:
            print(r)
            
        cmd = input(f"\n[Page {offset//limit + 1}] Enter 'next', 'prev', 'sort <name|birthday|date_added>', or 'quit': ").strip().lower()
        
        if cmd == 'next':
            offset += limit
        elif cmd == 'prev':
            offset = max(0, offset - limit)
        elif cmd.startswith('sort'):
            parts = cmd.split()
            if len(parts) == 2 and parts[1] in ['name', 'birthday', 'date_added']:
                sort_by = parts[1]
                offset = 0
        elif cmd == 'quit':
            break

def export_to_json():
    data = get_all_data_for_export()
    export_list = []
    for row in data:
        export_list.append({
            "name": row[0],
            "email": row[1],
            "birthday": row[2],
            "group": row[3],
            "phones": row[4] if row[4] else []
        })
    with open('contacts_export.json', 'w') as f:
        json.dump(export_list, f, indent=4)
    print("Exported to contacts_export.json")

def import_from_json():
    try:
        with open('contacts_export.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return

    for item in data:
        name = item.get('name')
        email = item.get('email')
        birthday = item.get('birthday')
        group = item.get('group')
        phones = item.get('phones', [])

        if contact_exists(name):
            ans = input(f"Contact {name} exists. Overwrite? (y/n): ").lower()
            if ans == 'y':
                update_contact(name, email, birthday, group)
        else:
            insert_contact(name, email, birthday, group)
        
        for p in phones:
            call_add_phone(name, p.get('phone'), p.get('type'))
    print("Import complete.")

def import_csv():
    filename = input("Enter CSV filename: ")
    try:
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('name')
                email = row.get('email')
                birthday = row.get('birthday')
                group = row.get('group')
                phone = row.get('phone')
                ptype = row.get('type')
                
                if contact_exists(name):
                    update_contact(name, email, birthday, group)
                else:
                    insert_contact(name, email, birthday, group)
                
                if phone and ptype:
                    call_add_phone(name, phone, ptype)
        print("CSV Import complete.")
    except Exception as e:
        print(e)

def main():
    while True:
        print("\n1. Filter by group")
        print("2. Search by email")
        print("3. Paginated View")
        print("4. Add phone to contact")
        print("5. Move contact to group")
        print("6. Global search")
        print("7. Export to JSON")
        print("8. Import from JSON")
        print("9. Import from CSV")
        print("0. Exit")
        
        choice = input("Choice: ")
        
        if choice == '1':
            g = input("Group name: ")
            res = filter_by_group(g)
            for r in res: print(r)
        elif choice == '2':
            e = input("Email partial: ")
            res = search_by_email(e)
            for r in res: print(r)
        elif choice == '3':
            pagination_menu()
        elif choice == '4':
            n = input("Contact name: ")
            p = input("Phone: ")
            t = input("Type (home/work/mobile): ")
            call_add_phone(n, p, t)
        elif choice == '5':
            n = input("Contact name: ")
            g = input("New group name: ")
            call_move_to_group(n, g)
        elif choice == '6':
            q = input("Search query: ")
            res = call_search_contacts(q)
            for r in res: print(r)
        elif choice == '7':
            export_to_json()
        elif choice == '8':
            import_from_json()
        elif choice == '9':
            import_csv()
        elif choice == '0':
            sys.exit()

if __name__ == '__main__':
    main()