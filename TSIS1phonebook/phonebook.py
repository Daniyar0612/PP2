from connect import get_connection

def execute_query(query, params=None, fetch=False):
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        if fetch:
            result = cur.fetchall()
            cur.close()
            conn.close()
            return result
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e

def get_contacts_paginated(limit, offset, sort_by='name'):
    query = f"""
        SELECT c.name, c.email, c.birthday, g.name AS group_name, c.date_added
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        ORDER BY c.{sort_by}
        LIMIT %s OFFSET %s;
    """
    return execute_query(query, (limit, offset), fetch=True)

def filter_by_group(group_name):
    query = """
        SELECT c.name, c.email, c.birthday, g.name AS group_name
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        WHERE g.name = %s;
    """
    return execute_query(query, (group_name,), fetch=True)

def search_by_email(email_query):
    query = """
        SELECT c.name, c.email, g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE c.email ILIKE %s;
    """
    return execute_query(query, ('%' + email_query + '%',), fetch=True)

def call_add_phone(contact_name, phone, p_type):
    query = "CALL add_phone(%s, %s, %s);"
    execute_query(query, (contact_name, phone, p_type))

def call_move_to_group(contact_name, group_name):
    query = "CALL move_to_group(%s, %s);"
    execute_query(query, (contact_name, group_name))

def call_search_contacts(search_query):
    query = "SELECT * FROM search_contacts(%s);"
    return execute_query(query, (search_query,), fetch=True)

def insert_contact(name, email, birthday, group_name):
    query_group = "SELECT id FROM groups WHERE name = %s;"
    group_res = execute_query(query_group, (group_name,), fetch=True)
    
    if not group_res:
        query_insert_group = "INSERT INTO groups (name) VALUES (%s) RETURNING id;"
        group_id = execute_query(query_insert_group, (group_name,), fetch=True)[0][0]
    else:
        group_id = group_res[0][0]
        
    query_contact = "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) RETURNING id;"
    return execute_query(query_contact, (name, email, birthday, group_id), fetch=True)[0][0]

def contact_exists(name):
    query = "SELECT id FROM contacts WHERE name = %s;"
    res = execute_query(query, (name,), fetch=True)
    return len(res) > 0

def update_contact(name, email, birthday, group_name):
    query_group = "SELECT id FROM groups WHERE name = %s;"
    group_res = execute_query(query_group, (group_name,), fetch=True)
    
    if not group_res:
        query_insert_group = "INSERT INTO groups (name) VALUES (%s) RETURNING id;"
        group_id = execute_query(query_insert_group, (group_name,), fetch=True)[0][0]
    else:
        group_id = group_res[0][0]

    query = "UPDATE contacts SET email = %s, birthday = %s, group_id = %s WHERE name = %s;"
    execute_query(query, (email, birthday, group_id, name))

def get_all_data_for_export():
    query = """
        SELECT c.name, c.email, TO_CHAR(c.birthday, 'YYYY-MM-DD'), g.name,
               (SELECT json_agg(json_build_object('phone', p.phone, 'type', p.type))
                FROM phones p WHERE p.contact_id = c.id) AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id;
    """
    return execute_query(query, fetch=True)