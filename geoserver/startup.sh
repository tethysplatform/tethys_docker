#!/bin/bash

# Generate the geoserver_startup.sh
python /tmp/gen_runtime_dynamic_files.py

# Start with supervisor -----------------------------------------------------------------------------------------------#
/usr/bin/supervisord -c $GEOSERVER_HOME/supervisord.conf