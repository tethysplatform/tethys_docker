# Modify the CKAN config file to reflect linked ports ------------------------#
sed "s/#solr_url.*/solr_url = http:\/\/$DATA_PORT_8080_TCP_ADDR:$DATA_PORT_8080_TCP_PORT\/solr/g" -i $CKAN_INI
sed "s/sqlalchemy.url.*/sqlalchemy.url = postgresql:\/\/$CKAN_USER:$CKAN_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$CKAN_DATABASE/g" -i $CKAN_INI
sed "s/#ckan.datastore.write_url.*/ckan.datastore.write_url = postgresql:\/\/$CKAN_USER:$CKAN_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$DATASTORE_DATABASE/g" -i $CKAN_INI
sed "s/#ckan.datastore.read_url.*/ckan.datastore.read_url = postgresql:\/\/$DATASTORE_USER:$DATASTORE_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$DATASTORE_DATABASE/g" -i $CKAN_INI

# Modify the Tethys Apps config file to reflect linked ports -----------------#
sed "s/tethys.database_manager_url =.*/tethys.database_manager_url = postgresql:\/\/$APPS_MANAGER_USER:$APPS_MANAGER_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$APPS_MANAGER_DATABASE/g" -i $TETHYS_INI
sed "s/tethys.superuser_url =.*/tethys.superuser_url = postgresql:\/\/TETHYS_SUPER_USER:$TETHYS_SUPER_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$TETHYS_SUPER_DATABASE/g" -i $TETHYS_INI

# Activate the virtual environment -------------------------------------------#
. $VENV_ACTIVATE

# Update the Tethys Apps plugin ----------------------------------------------#
cd $TETHYS_DEV_HOME/ckanext-tethys_apps
git pull

# Install apps ---------------------------------------------------------------#
/usr/lib/ckan/scripts/develop_apps.sh

# Activate initialize the database -------------------------------------------#
cd $VENV_HOME/src/ckan
paster db init -c $CKAN_INI

# Start the development server (paster) --------------------------------------#
paster serve --reload $CKAN_INI
