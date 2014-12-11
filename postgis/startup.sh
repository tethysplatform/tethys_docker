#!/bin/bash

WPS_ROOT=/usr/share/tomcat7-wps/wps
WPS_USERS=$WPS_ROOT/WEB-INF/classes/users.xml
SERVICE_SKELETON=$WPS_ROOT/config/wpsCapabilitiesSkeleton.xml

# Make sure we have a user set up
if [ -z "$DEFAULT_PASS" ]; then
  TETHYS_DEFAULT_PASS=wps
fi

if [ -z "$DB_MANAGER_PASS" ]; then
  DB_MANAGER_PASS=wps
fi

if [ -z "$SUPER_PASS" ]; then
  SUPER_PASS=wps
fi

# Init Database Users Here

/usr/bin/supervisord