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

def create_table(table_name, cursor):
    """
    Create a table in the DB, ex: wlan10
    """
    query = """CREATE TABLE IF NOT EXISTS {} (ip TEXT PRIMARY KEY NOT NULL, hostname TEXT, os TEXT)""".format(table_name)
    cursor.execute(query)

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
    query = """INSERT INTO {} VALUES (?,?,?)""".format(table_name)
    cursor.executemany(query, machines)

def update(table_name, machines, cursor):
    """
    Insert a line into the DB if the line does not exist in here or update the line if it exists
    Ensure that machines = [(ip1, hostname1, os,),
                            (ip2, hostname2, os,),
                            ...
                            (ipN, hostnameN, os,),
                           ]
    Parameters ip, hostname and os are strings
    """
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