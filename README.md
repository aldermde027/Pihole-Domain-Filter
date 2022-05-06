# pihole_domain_filter
 Automatically adds domains to the "Top Domains" based on Top Client entries in the API / Web Interface.

The program functions by taking a local backup of the configuration file that controls the web view of the API / Web Interface (just in case something happens), and in the process of taking this backup it will parse the needed clients out of the file.

Once the clients have been parsed out, it will then connect to the local PiHole Sqlite3 database that is used to store all connection history and data and parse out the domains of only the clients that were specified in the UI. Once these have been returned, we will recreate the configuration file, inserting the newly discovered domains into the already existing list.

All of the file and database locations are based upon a standard PiHole install. In order to run this, admin permissions are required. It is recommended to set this as a crontab action if frequent updating is required, otherwise the occassional manual update will work.
