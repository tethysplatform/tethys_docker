#!/bin/bash
# Start apache, jetty, and postgresql
/etc/init.d/postgresql start
su jetty /etc/init.d/jetty start
/etc/init.d/apache2 start

# Start nginx (with supervisor)
/usr/bin/supervisord
