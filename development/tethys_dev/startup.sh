# Modify the CKAN config file to reflect linked ports ------------------------#
sed "s/#solr_url.*/solr_url = http:\/\/$DATA_PORT_8080_TCP_ADDR:$DATA_PORT_8080_TCP_PORT\/solr/g" -i $CKAN_INI
sed "s/sqlalchemy.url.*/sqlalchemy.url = postgresql:\/\/$PGUSER:$PGPASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$PGDATABASE/g" -i $CKAN_INI
sed "s/#ckan.datastore.write_url.*/ckan.datastore.write_url = postgresql:\/\/$PGUSER:$PGPASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$DSDATABASE/g" -i $CKAN_INI
sed "s/#ckan.datastore.read_url.*/ckan.datastore.read_url = postgresql:\/\/$DSUSER:$DSPASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$DSDATABASE/g" -i $CKAN_INI

# Modify the Tethys Apps config file to reflect linked ports -----------------#
sed "s/tethys.database_manager_url =.*/tethys.database_manager_url = postgresql:\/\/$APP_MANAGER_USER:$APP_MANAGER_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$APP_MANAGER_DATABASE/g" -i $TETHYS_INI

# Activate the virtual environment -------------------------------------------#
. $VENV_ACTIVATE

# Install apps ---------------------------------------------------------------#
python /usr/lib/ckan/scripts/install_apps.py $APPS_PROJECTS_DEV

# Activate initialize the database -------------------------------------------#
cd $VENV_HOME/src/ckan
paster db init -c $CKAN_INI

# Start the development server (paster) --------------------------------------#
paster serve --reload $CKAN_INI
