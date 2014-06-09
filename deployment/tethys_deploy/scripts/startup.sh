#!/bin/bash
# Startup message ------------------------------------------------------------#
echo "Starting Tethys..."

# Declare variables ----------------------------------------------------------#
cd /tmp/
CKAN_DATABASE=$(grep -Po "(?<=^CKAN_DATABASE ).*" tethys_deploy.conf)
CKAN_USER=$(grep -Po "(?<=^CKAN_USER ).*" tethys_deploy.conf)
CKAN_PASS=$(grep -Po "(?<=^CKAN_PASS ).*" tethys_deploy.conf)
DATASTORE_DATABASE=$(grep -Po "(?<=^DATASTORE_DATABASE ).*" tethys_deploy.conf)
DATASTORE_USER=$(grep -Po "(?<=^DATASTORE_USER ).*" tethys_deploy.conf)
DATASTORE_PASS=$(grep -Po "(?<=^DATASTORE_PASS ).*" tethys_deploy.conf)
APPS_MANAGER_DATABASE=$(grep -Po "(?<=^APPS_MANAGER_DATABASE ).*" tethys_deploy.conf)
APPS_MANAGER_USER=$(grep -Po "(?<=^APPS_MANAGER_USER ).*" tethys_deploy.conf)
APPS_MANAGER_PASS=$(grep -Po "(?<=^APPS_MANAGER_PASS ).*" tethys_deploy.conf)
rm /tmp/tethys_deploy.conf

# Modify the CKAN config file to reflect linked ports ------------------------#
sed "s/#solr_url.*/solr_url = http:\/\/$DATA_PORT_8080_TCP_ADDR:$DATA_PORT_8080_TCP_PORT\/solr/g" -i $CKAN_INI
sed "s/sqlalchemy.url.*/sqlalchemy.url = postgresql:\/\/$CKAN_USER:$CKAN_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$CKAN_DATABASE/g" -i $CKAN_INI
sed "s/#ckan.datastore.write_url.*/ckan.datastore.write_url = postgresql:\/\/$CKAN_USER:$CKAN_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$DATASTORE_DATABASE/g" -i $CKAN_INI
sed "s/#ckan.datastore.read_url.*/ckan.datastore.read_url = postgresql:\/\/$DATASTORE_USER:$DATASTORE_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$DATASTORE_DATABASE/g" -i $CKAN_INI

# Modify the Tethys Apps config file to reflect linked ports -----------------#
sed "s/tethys.database_manager_url =.*/tethys.database_manager_url = postgresql:\/\/$APPS_MANAGER_USER:$APPS_MANAGER_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\/$APPS_MANAGER_DATABASE/g" -i $TETHYS_INI

# Activate the virtual environment -------------------------------------------#
. $VENV_ACTIVATE

# Install apps ---------------------------------------------------------------#
/usr/lib/ckan/scripts/install_apps.sh

Activate initialize the database -------------------------------------------#
echo "Initializing CKAN Database..."
cd $VENV_HOME/src/ckan
paster db init -c $CKAN_INI

# Permissions
chown www-data:www-data /var/lib/ckan/default
chmod u+rwx /var/lib/ckan/default
chown -R www-data:www-data /usr/lib/ckan/default/

# Start apache
/etc/init.d/apache2 start

# Start nginx (with supervisor)
/usr/bin/supervisord

bash
