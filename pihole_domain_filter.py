# encoding utf-8
# created: 03 May 2022 - Duaine Alderman


import pathlib
import sqlite3


SQL_QUERY = """SELECT domain FROM queries WHERE CLIENT IN ({}) GROUP BY DOMAIN;"""

API_DOMAIN_LINE = "API_EXCLUDE_DOMAINS="
API_CLIENT_LINE = "API_EXCLUDE_CLIENTS="


class PiHoleDomainFilter():
    def __init__(self):
        # SQL
        self.sql_connection = None
        self.sql_cursor = None
        self.filter_domains = set()
        self.filter_clients = set()

        # Files
        self.setup_file = pathlib.Path('/etc/pihole/setupVars.conf')
        self.backup_file = pathlib.Path('/etc/pihole/setupVars.conf.bak')

        # Execute the script now
        try:
            self.backup_settings()
            self.fetch_sql()
            self.rebuild_settings()
        except:
            print("Exception raised, closing connection...")
            # Close the connection if possible if we hit ANY error
            if self.sql_connection:
                self.sql_connection.close()

    def backup_settings(self):
        print('Backing up settings file...')
        with open(self.setup_file, 'r') as orig_file:
            with open(self.backup_file, 'w') as out_file:
                for file_line in orig_file:
                    # Get the already filtered domains
                    if API_DOMAIN_LINE in file_line:
                        self.filter_domains = {item.replace('\n', '') for item in file_line.split(API_DOMAIN_LINE)[1].split(',')}
                    # Get the clients that control what we add to the filter
                    elif API_CLIENT_LINE in file_line:
                        self.filter_clients = {f"'{item.strip()}'" for item in file_line.split(API_CLIENT_LINE)[1].split(',')}
                    out_file.write(file_line)

    def fetch_sql(self):
        print('Fetching information from SQL...')
        self.sql_connection = sqlite3.connect("/etc/pihole/pihole-FTL.db")
        self.sql_cursor = self.sql_connection.cursor()
        self.sql_cursor.execute(SQL_QUERY.format(",".join(self.filter_clients)))
        sql_results = self.sql_cursor.fetchall()
        for item in sql_results:
            self.filter_domains.add(str(item[0]))
        self.sql_connection.close()

    def rebuild_settings(self):
        print('Rebuilding settings file from SQL...')
        with open(self.backup_file, 'r') as backup_file:
            with open(self.setup_file, 'w') as out_file:
                for file_line in backup_file:
                    # Get the already filtered domains
                    if API_DOMAIN_LINE in file_line:
                        file_line = f"{API_DOMAIN_LINE}{','.join(self.filter_domains)}"
                        file_line += '\n'
                    out_file.write(file_line)


if __name__ == '__main__':
    PiHoleDomainFilter()
