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

# Start with supervisor -----------------------------------------------------------------------------------------------#
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf