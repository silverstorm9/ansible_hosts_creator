import sqlite3

"""
Databasse structures:

Example : wlan10
_______________________________________________
|       IP        | HOSTNAME  | OS  |   DIST  |
-----------------------------------------------
|   192.168.10.1  | hostname1 | os1 | CentOS7 |
|   192.168.10.2  | hostname2 | os2 | Debian9 |
|      ...        |     ...   | ... |   ...   |
|  192.168.10.xxx | hostnameN | osN |  DistN  |
-----------------------------------------------
"""

def create_table(table_name):
    """
    Create a table in the DB, ex: wlan10
    """
    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    query = """CREATE TABLE IF NOT EXISTS {} (ip TEXT PRIMARY KEY NOT NULL, hostname TEXT, os TEXT, dist TEXT)""".format(table_name)

    # Try to execute the query a table
    try:
        cursor.execute(query)
        # Save (commit) the changes
        conn.commit()

        # Close the connection with the DB
        conn.close()
    except Exception as e:
        print(e)

def insert(table_name, machines, db_file='DB.db'):
    """
    Insert a list of machines into a table
    Ensure that machines = [(ip1, hostname1, os, dist),
                            (ip2, hostname2, os, dist),
                            ...
                            (ipN, hostnameN, os, dist),
                           ]
    Parameters ip, hostname and os are strings
    """
    # Connect to the DB
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    query = """INSERT INTO {} VALUES (?,?,?,?)""".format(table_name)
    cursor.executemany(query, machines)

    # Save (commit) the changes
    conn.commit()

    # Close the connection with the DB
    conn.close()

def insert_sql_query(db_file='DB.db'):
    """
    Allow the user to insert SQL query
    """
    # Connect to the DB
    conn = sqlite3.connect(db_file)
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

def update(table_name, machines, db_file='DB.db'):
    """
    Insert a line into the DB if the line does not exist in here or update the line if it exists
    Ensure that machines = [(ip1, hostname1, os, dist),
                            (ip2, hostname2, os, dist),
                            ...
                            (ipN, hostnameN, os, dist),
                           ]
    Parameters ip, hostname, os and dist are strings
    """
    # Connect to the DB
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    #query = """INSERT OR REPLACE INTO {} (ip,hostname,os,dist) VALUES (?,?,?,?)""".format(table_name)
    #cursor.executemany(query, machines)
    for machine in machines:
        try:
            actual_os = [row[0] for row in cursor.execute("""SELECT os FROM {} WHERE ip=\'{}\'""".format(table_name, machine[0]))][0] # ne pas remettre en cause l'existance de cette ligne / don't question the existance of this line
        except:
            actual_os = ''
        new_os = machine[2]
        if actual_os and actual_os != 'no_os' and new_os == 'no_os':
            query = """UPDATE {} SET hostname =\'{}\', dist=\'{}\' WHERE ip==\'{}\'""".format(table_name, machine[1], machine[3], machine[0])
            cursor.execute(query)
        else:
            query = """INSERT OR REPLACE INTO {} (ip,hostname,os,dist) VALUES (?,?,?,?)""".format(table_name)
            cursor.execute(query, machine)

    # Save (commit) the changes
    conn.commit()

    # Close the connection with the DB
    conn.close()

def select_all_from(db_file='DB.db'):
    # Connect to the DB
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Ask the user to pull ip from database by inserting SQL query
    query = 'SELECT * FROM ' + input('(sql)>SELECT ip,hostname,os,dist FROM ')

    try:
        cursor.execute(query)
    except Exception as e:
        print('Error:', e)

    buffer = str()
    for row in cursor:
        buffer += '\n{} # {} {} {}'.format(row[0], row[1], row[2], row[3])

    # Close the connection with the DB
    conn.close()

    return buffer

def show_table(table_name, db_file='DB.db'):
    # Connect to the DB
    conn = sqlite3.connect(db_file)
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


def export_to_txt(db_file='DB.db', txt_file='DB.txt'):
    # Connect to the DB
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    buffer = '' # to contains all database information

    query = 'SELECT name FROM sqlite_master WHERE type = "table"'

    try:
        cursor.execute(query)
        tables = [elmt[0] for elmt in list(cursor)]

        for table_name in tables:
            query = 'SELECT * FROM {}'.format(table_name)

            cursor.execute(query)
            buffer += table_name + '\n'
            for row in cursor:
                buffer += ' '.join([elmt for elmt in list(row)]) + '\n'
    except Exception as e:
        print('Error:', e)
        conn.close()
        return

    # Close the connection with the DB
    conn.close()

    file = open(txt_file, 'w')
    file.write(buffer)
    file.close()

def import_from_txt(db_file='DB.db', txt_file='DB.txt'):

    # Read DB.txt
    try:
        file = open(txt_file, 'r')
        buffer = file.readlines()
        file.close()
    except Exception as e:
        print(e)
        return

    # Clear DB.db
    try:
        file = open(db_file, 'w')
        file.write('')
        file.close()
    except Exception as e:
        print(e)
        return

    # Write in DB.db

    table_name = ''
    for line in buffer:
        data = line[:-1].split(' ') # data is a list with one element
        if len(data) == 1:
            table_name = data[0]
            create_table(table_name)
        elif len(data) == 4:
            insert(table_name=table_name, machines=[tuple(data)])