#!/bin/bash

# Generate the geoserver_startup.sh
python3 /tmp/gen_runtime_dynamic_files.py

# Start with supervisor -----------------------------------------------------------------------------------------------#
/usr/bin/supervisord -c $GEOSERVER_HOME/supervisord.conf