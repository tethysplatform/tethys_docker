#!/bin/bash

# Generate the supervisor configs
python $GEOSERVER_HOME/generated/gen_runtime_dynamic_files.py

# Start with supervisor -----------------------------------------------------------------------------------------------#
/usr/bin/supervisord -c $GEOSERVER_HOME/supervisord.conf