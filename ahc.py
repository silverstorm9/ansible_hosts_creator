import os
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
    buffer = """
AHC (ANSIBLE HOSTS CREATOR) 1.0 powered by Python 3.8.3, 01/07/2020
First, this tool is used to extract results of nmap contained in XML file and push them to the Database (DB.db).
Secondly, it permit for user to select elements from the database to generate a hosts file containing IP addresses using by Ansible for tests.

COMMANDS:

help : show help
create [-t tableName|-h hostsPath] : create a table (-t) in the database
                                     create a hosts file (-h) -> don't forget to set .txt extension
edit [-t tableName xmlFile|-h hostsPath] : (-t) extract and push data from XML file and push them to the table in the database
                                           (-h) edit hosts file (TXT) by inserting SQL query
show [-t tableName|-h hostsPath] : (-t) display the content of the table (use * or all to show content for all tables in the database)
                                 : (-h) display the content of the hosts file
sql : permit for the user to insert SQL query
export : export the database from .db to .txt
import : import the database from .txt to .db
exit|quit

EXAMPLE OF COMMANDS USES:

create -t wlan10
create -h ./hosts.txt

edit -t wlan10 ./nmap_wlan10.xml
edit -h ./hosts.txt

show -t wlan10
show -h ./hosts.txt

export
import

EXAMPLE OF COMMON SQL QUERY USES :

SELECT * FROM wlan10 WHERE os!='Windows'
INSERT INTO wlan10 VALUES ('192.168.10.1','machine1','Linux','CentOS7')
DELETE FROM wlan10 WHERE ip=='192.168.10.1'
UPDATE wlan10 SET hostname = 'machine1', os = 'Linux', dist='Debian10' WHERE ip=='192.168.10.1'
INSERT OR REPLACE INTO wlan10 (ip,hostname,os,dist) VALUES ('192.168.10.1','machine1','no_os','no_dist')

See also : https://sql.sh/cours

    """
    print(buffer)

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

        buffer += DB_functions.select_all_from()

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

    # Push data to the DB
    try:
        DB_functions.update(table_name, extracted_info)
    except Exception as e:
        print(e)
        if str(e) == 'no such table: {}'.format(str(e).split()[-1]):
            choice = '-1'
            while choice not in ['Y','n']:
                choice = input('Would you want to create the table {} ? [Y/n]'.format(str(e).split()[-1]))
            if choice == 'Y':
                DB_functions.create_table(table_name=str(e).split()[-1])
                DB_functions.update(table_name, extracted_info)
            elif choice == 'n':
                pass

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
    

# Program begin here
if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__))) # Redirect the path into ..../ansible_hosts_creator
    display_menu()
    while True:
        choice = '-1'
        while not(choice.split()) or choice.split()[0] not in ['create','edit','exit','export','help','import','show','sql','quit']:
            try:
                choice = input('(ahc)>')
            except Exception as e:
                print(e)
            if choice.split() and choice.split()[0] not in ['create','edit','exit','export','help','import','show','sql','quit']:
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
                    DB_functions.create_table(table_name=choice.split()[2])
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
                    DB_functions.show_table(table_name=choice.split()[2])
                # show hosts [hosts_path]
                elif choice.split()[1] == '-h':
                    show_hosts(hosts_path=choice.split()[2])
                else:
                    print('{}: args error'.format(choice))
            else:
                print('{}: args error'.format(choice))

        # sql
        elif choice.split()[0] == 'sql':
            DB_functions.insert_sql_query()

        # export
        elif choice.split()[0] == 'export':
            DB_functions.export_to_txt()

        # import
        elif choice.split()[0] == 'import':
            DB_functions.import_from_txt()