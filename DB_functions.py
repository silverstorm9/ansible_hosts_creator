import sqlite3

"""
Databasse structures:

Example : wlan10
_____________________________________
|       IP        | HOSTNAME  | OS  |
-------------------------------------
|   192.168.10.1  | hostname1 | os1 |
|   192.168.10.2  | hostname2 | os2 |
|      ...        |     ...   | ... |
|  192.168.10.xxx | hostnameN | osN |
-------------------------------------
"""

def create_table(table_name):
    """
    Create a table in the DB, ex: wlan10
    """
    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    query = """CREATE TABLE IF NOT EXISTS {} (ip TEXT PRIMARY KEY NOT NULL, hostname TEXT, os TEXT)""".format(table_name)

    # Try to execute the query a table
    try:
        cursor.execute(query)
        # Save (commit) the changes
        conn.commit()

        # Close the connection with the DB
        conn.close()
    except Exception as e:
        print(e)

def insert(table_name, machines, cursor):
    """
    Insert a list of machines into a table
    Ensure that machines = [(ip1, hostname1, os,),
                            (ip2, hostname2, os,),
                            ...
                            (ipN, hostnameN, os,),
                           ]
    Parameters ip, hostname and os are strings
    """
    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    query = """INSERT INTO {} VALUES (?,?,?)""".format(table_name)
    cursor.executemany(query, machines)

    # Save (commit) the changes
    conn.commit()

    # Close the connection with the DB
    conn.close()

def insert_sql_query():
    """
    Allow the user to insert SQL query 
    """
    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    query = input('(sql)>')

    try:
        cursor.execute(query)
    except Exception as e:
        print('Error:', e)

    for row in cursor:
        print(row)

    # Save (commit) the changes
    conn.commit()

    # Close the connection with the DB
    conn.close()

def update(table_name, machines):
    """
    Insert a line into the DB if the line does not exist in here or update the line if it exists
    Ensure that machines = [(ip1, hostname1, os,),
                            (ip2, hostname2, os,),
                            ...
                            (ipN, hostnameN, os,),
                           ]
    Parameters ip, hostname and os are strings
    """
    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    #query = """INSERT OR REPLACE INTO {} (ip,hostname,os) VALUES (?,?,?)""".format(table_name)
    #cursor.executemany(query, machines)
    for machine in machines:
        try:
            actual_os = [row[0] for row in cursor.execute("""SELECT os FROM {} WHERE ip=\'{}\'""".format(table_name, machine[0]))][0] # ne pas remettre en cause l'existance de cette ligne / don't question the existance of this line
        except:
            actual_os = ''
        new_os = machine[2]
        if actual_os and actual_os != 'no_os' and new_os == 'no_os':
            query = """UPDATE {} SET hostname =\'{}\' WHERE ip==\'{}\'""".format(table_name, machine[1], machine[0])
            cursor.execute(query)
        else:
            query = """INSERT OR REPLACE INTO {} (ip,hostname,os) VALUES (?,?,?)""".format(table_name)
            cursor.execute(query, machine)

    # Save (commit) the changes
    conn.commit()

    # Close the connection with the DB
    conn.close()

def select_all_from():
    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    # Ask the user to pull ip from database by inserting SQL query
    query = 'SELECT * FROM ' + input('(sql)>SELECT ip,hostname,os FROM ')

    try:
        cursor.execute(query)
    except Exception as e:
        print('Error:', e)

    buffer = str()
    for row in cursor:
        buffer += '\n{} # {} {}'.format(row[0], row[1], row[2])

    # Close the connection with the DB
    conn.close()

    return buffer

def show_table(table_name):
    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    if table_name in ['*','all']:
        query = 'SELECT name FROM sqlite_master WHERE type = "table"'

        try:
            cursor.execute(query)
            tables = [elmt[0] for elmt in list(cursor)]

            for table_name in tables:
                query = 'SELECT * FROM {}'.format(table_name)

                cursor.execute(query)
                print('\n{}'.format(table_name))
                for row in cursor:
                    print(' '.join([elmt for elmt in list(row)]))

        except Exception as e:
            print('Error:', e)

    else:
        query = 'SELECT * FROM {}'.format(table_name)

        try:
            cursor.execute(query)
            print('\n{}'.format(table_name))
            for row in cursor:
                print(' '.join([elmt for elmt in list(row)]))
        except Exception as e:
            print('Error:', e)

    # Close the connection with the DB
    conn.close()