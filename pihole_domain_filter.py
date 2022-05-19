# encoding utf-8
# created: 03 May 2022 - Duaine Alderman


import pathlib
import sqlite3

# Store the query here for ease of use
SQL_QUERY = """SELECT domain FROM queries WHERE CLIENT IN ({}) GROUP BY DOMAIN;"""

# The hardcoded text that starts the exclusion lines in the conf file
API_DOMAIN_LINE = "API_EXCLUDE_DOMAINS="
API_CLIENT_LINE = "API_EXCLUDE_CLIENTS="


class PiHoleDomainFilter():
    def __init__(self):
        # SQL
        self.sql_connection = None
        self.sql_cursor = None

        # Filter storage
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
            # Close the connection if possible in case we hit ANY error
            if self.sql_connection:
                self.sql_connection.close()

    def backup_settings(self):
        """
        Backup the settings file to ensure that if anything happens we will have a restore point.

        :return: None
        """

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
        """
        Fetch the needed domains from the Sqlite3 database (assuming standard install locations for
        Pi-Hole at this time) using the provided exclusion client IPs.

        :return: None
        """

        print('Fetching information from SQL...')
        self.sql_connection = sqlite3.connect("/etc/pihole/pihole-FTL.db")
        self.sql_cursor = self.sql_connection.cursor()
        self.sql_cursor.execute(SQL_QUERY.format(",".join(self.filter_clients)))
        sql_results = self.sql_cursor.fetchall()
        for item in sql_results:
            self.filter_domains.add(str(item[0]))
        self.sql_connection.close()

    def rebuild_settings(self):
        """
        Rebuilds the settings file based upon the backup file, the stored filter information, and
        the new information parsed from the Sqlite3 DB file.

        The backup file is only opened for reading and will not be modified in any way. Only the
        original file will be changed.

        :return: None
        """

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
