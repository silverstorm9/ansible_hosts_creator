import sqlite3
import analyse_nmap
import DB_functions

def display_menu():
    logo = """
    _              _  _     _        _  _           _          ___                  _             
   /_\   _ _   ___(_)| |__ | | ___  | || | ___  ___| |_  ___  / __| _ _  ___  __ _ | |_  ___  _ _ 
  / _ \ | ' \ (_-<| || '_ \| |/ -_) | __ |/ _ \(_-<|  _|(_-< | (__ | '_|/ -_)/ _` ||  _|/ _ \| '_|
 /_/ \_\|_||_|/__/|_||_.__/|_|\___| |_||_|\___//__/ \__|/__/  \___||_|  \___|\__,_| \__|\___/|_|  
                                                                                                  
    """
    print(logo)
    print('Enter help command to show all commands.\n')

def display_help():
    print('AHC (ANSIBLE HOSTS CREATOR) 1.0 powered by Python 3.8.3, 01/07/2020')
    print('First, this tool is used to extract results of nmap contained in XML file and push them to the Database (DB.db).')
    print('Secondly, it permit for user to select elements from the database to generate a hosts file containing IP addresses using by Ansible for tests.')
    print('\nCommands:')
    print('\nhelp : show help')
    print('create [-t tableName|-h hostsPath] : create a table (-t) in the database')
    print('                                     create a hosts file (-h) -> don\'t forget to set .txt extension')
    print('edit [-t tableName xmlFile|-h hostsPath] : (-t) extract and push data from XML file and push them to the table in the database')
    print('                                           (-h) edit hosts file (TXT) by inserting SQL query')
    print('show [-t tableName|-h hostsPath] : (-t) display the content of the table (use * or all to show content for all tables in the database)')
    print('                                 : (-h) display the content of the hosts file')
    print('sql : permit for the user to insert SQL query')
    print('exit|quit')
    print('\nExample :')
    print('\ncreate -t wlan10')
    print('create -h ./hosts.txt')
    print('\nedit -t wlan10 ./nmap_wlan10.xml')
    print('edit -h ./hosts.txt')
    print('\nshow -t wlan10')
    print('show -h ./hosts.txt')
    print('\nExample of common SQL command :')
    print('\nSELECT * FROM wlan10 WHERE os!=\'Windows\'')
    print('INSERT INTO wlan10 VALUES (\'192.168.10.1\',\'machine1\',\'Linux\')')
    print('DELETE FROM wlan10 WHERE ip==\'192.168.10.1\'')
    print('UPDATE wlan10 SET hostname = \'machine1\', os = \'Windows\' WHERE ip==\'192.168.10.1\'')
    print('INSERT OR REPLACE INTO wlan10 (ip,hostname,os) VALUES (\'192.168.10.1\',\'machine1\',\'no_os\')')
    print('\nSee also : https://sql.sh/cours')
    print('\n')

def edit_hosts(hosts_path):
    while True:
        show_hosts(hosts_path) # Show hosts file one time before inserting something in it
        file = open(hosts_path, 'a')
        buffer = str() # buffer to insert in hosts file
        # Add group name
        choice = '-1'
        while choice not in ['Y','n']:
            choice = input('Add a group name ? [Y/n]')
        if choice == 'Y':
            group_name = input('Enter group name >')
            buffer += '\n\n[{}]'.format(group_name)

        # Connect to the DB
        conn = sqlite3.connect('DB.db')
        cursor = conn.cursor()

        # Ask the user to pull ip from database by inserting SQL query
        query = 'SELECT * FROM ' + input('(sql)>SELECT ip,hostname,os FROM ')

        try:
            cursor.execute(query)
        except Exception as e:
            print('Error:', e)

        for row in cursor:
            buffer += '\n{} # {} {}'.format(row[0], row[1], row[2])

        # Close the connection with the DB
        conn.close()

        # Ask to add the buffer to the hosts file
        print(buffer)
        choice = '-1'
        while choice not in ['Y','n']:
            choice = input('Push to {} ? [Y/n]'.format(hosts_path))
        if choice == 'Y':
            file.write(buffer)
        elif choice == 'n':
            pass

        file.close()

        # Ask to continue editing hosts file
        choice = '-1'
        while choice not in ['Y','n']:
            choice = input('Continue ? [Y/n]') 
        if choice == 'Y':
            pass
        elif choice == 'n':
            break

def edit_table(table_name, nmap_path):
    # Extract nmap info
    extracted_info = analyse_nmap.extractNmapInfo(verbose=True, path=nmap_path) # nmap_file must be a XML file

    if not(extracted_info):
        print('{}: select a existing path'.format(nmap_path))
        return

    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    # Push data to the DB
    try:
        DB_functions.update(table_name, extracted_info, cursor=cursor)
    except Exception as e:
        print(e)
        if str(e) == 'no such table: {}'.format(str(e).split()[-1]):
            choice = '-1'
            while choice not in ['Y','n']:
                choice = input('Would you want to create the table {} ? [Y/n]'.format(str(e).split()[-1]))
            if choice == 'Y':
                DB_functions.create_table(table_name=str(e).split()[-1], cursor=cursor)
                DB_functions.update(table_name, extracted_info, cursor=cursor)
            elif choice == 'n':
                pass

    # Save (commit) the changes
    conn.commit()

    # Close the connection with the DB
    conn.close()

def generate_hosts(hosts_path):
    # Comment lines at the top of the hosts file
    banner = '# {} created with Ansible Hosts Creator (01/07/2020) powered by python 3.8.3'.format(hosts_path)
    # Try to create a file
    try:
        file = open(hosts_path, 'x')
        file.write(banner)
        file.close()
    except Exception as e:
        print(e)
        if str(e) == '[Errno 17] File exists: \'{}\''.format(hosts_path):
            choice = '-1'
            while choice not in ['Y','n']:
                choice = input('Would you want to overwrite {} ? [Y/n]'.format(hosts_path))
            if choice == 'Y':
                file = open(hosts_path, 'w')
                file.write(banner)
                file.close()
            elif choice == 'n':
                pass

def generate_table(table_name):
    # Connect to the DB
    conn = sqlite3.connect('DB.db')
    cursor = conn.cursor()

    # Try to create a table
    try:
        DB_functions.create_table(table_name, cursor)
    except Exception as e:
        print(e)

    # Save (commit) the changes
    conn.commit()

    # Close the connection with the DB
    conn.close()

def insert_sql_query():
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

def show_hosts(hosts_path):
    # Try to read a file if it exists
    try:
        file = open(hosts_path, 'r')
        print(file.read())
        file.close()
    except Exception as e:
        print(e)
        if str(e) == '[Errno 2] No such file or directory: \'{}\''.format(hosts_path):
            choice = '-1'
            while choice not in ['Y','n']:
                choice = input('Would you want to create {} ? [Y/n]'.format(hosts_path))
            if choice == 'Y':
                generate_hosts(hosts_path) # create a file if it doesn't exist
            elif choice == 'n':
                pass

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
    

if __name__ == "__main__":
    display_menu()
    while True:
        choice = '-1'
        while not(choice.split()) or choice.split()[0] not in ['create','edit','exit','help','show','sql','quit']:
            try:
                choice = input('(ahc)>')
            except Exception as e:
                print(e)
            if choice.split() and choice.split()[0] not in ['create','edit','exit','help','show','sql','quit']:
                print('{}: command not found'.format(choice.split()[0]))

        # exit|quit
        if choice.split()[0] in ['exit', 'quit']:
            print('QUITTING')
            break

        # create [table|hosts] [table_name|hosts_path] 
        elif choice.split()[0] == 'create':
            if len(choice.split()) == 3:
                # create table [table_name]
                if choice.split()[1] == '-t':
                    generate_table(table_name=choice.split()[2])
                # create hosts [hosts_path]
                elif choice.split()[1] == '-h':
                    generate_hosts(hosts_path=choice.split()[2])
                else:
                    print('{}: args error'.format(choice))
            else:
                print('{}: args error'.format(choice))

        # edit [table|hosts] [table_name|hosts_path] [*nmap_path]
        elif choice.split()[0] == 'edit':
            if len(choice.split()) in [3,4]:
                # edit table [table_name] [nmap_path]
                if choice.split()[1] == '-t' and len(choice.split()) == 4:
                    edit_table(table_name=choice.split()[2], nmap_path=choice.split()[3])
                # edit hosts [hosts_path]
                elif choice.split()[1] == '-h' and len(choice.split()) == 3:
                    edit_hosts(hosts_path=choice.split()[2])
                else:
                    print('{}: args error'.format(choice))
            else:
                print('{}: args error'.format(choice))

        # help
        elif choice.split()[0] == 'help':
            display_help()

        # show [table|hosts] [table_name|hosts_path]
        elif choice.split()[0] == 'show':
            if len(choice.split()) == 3:
                # show table [table_name]
                if choice.split()[1] == '-t':
                    show_table(table_name=choice.split()[2])
                # show hosts [hosts_path]
                elif choice.split()[1] == '-h':
                    show_hosts(hosts_path=choice.split()[2])
                else:
                    print('{}: args error'.format(choice))
            else:
                print('{}: args error'.format(choice))

        # sql
        elif choice == 'sql':
            insert_sql_query()