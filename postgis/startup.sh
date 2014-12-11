#!/bin/bash

# Set password variables ----------------------------------------------------------------------------------------------#
if [ -z "$TETHYS_DEFAULT_PASS" ]; then
  TETHYS_DEFAULT_PASS=pass
fi

if [ -z "$TETHYS_DB_MANAGER_PASS" ]; then
  TETHYS_DB_MANAGER_PASS=pass
fi

if [ -z "$TETHYS_SUPER_PASS" ]; then
  TETHYS_SUPER_PASS=pass
fi

# Init Database Users Here---------------------------------------------------------------------------------------------#
/etc/init.d/postgresql start

# Tethys Default
sudo -u postgres psql --command "CREATE USER tethys_default WITH NOCREATEDB NOCREATEROLE NOSUPERUSER PASSWORD '$TETHYS_DEFAULT_PASS';"
sudo -u postgres createdb -O tethys_default tethys_default -E utf-8 -T template0

# Tethys DB Manager
sudo -u postgres psql --command "CREATE USER tethys_db_manager WITH NOCREATEROLE NOSUPERUSER CREATEDB PASSWORD '$TETHYS_DB_MANAGER_PASS';"
sudo -u postgres createdb -O tethys_db_manager tethys_db_manager -E utf-8 -T template0

# Tethys Superuser
sudo -u postgres psql --command "CREATE USER tethys_super WITH CREATEDB NOCREATEROLE SUPERUSER PASSWORD '$TETHYS_SUPER_PASS';"
sudo -u postgres createdb -O tethys_super tethys_super -E utf-8 -T template0

/etc/init.d/postgresql stop

# Start with supervisor -----------------------------------------------------------------------------------------------#
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf