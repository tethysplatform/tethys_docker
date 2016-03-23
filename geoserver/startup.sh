# Generate the geoserver_startup.sh
python generate_geoserver_startup.py

# Start up geoserver nodes
$GEOSERVER_HOME/geoserver_startup.sh

# Start with supervisor -----------------------------------------------------------------------------------------------#
/usr/bin/supervisord -c $GEOSERVER_HOME/supervisord.conf