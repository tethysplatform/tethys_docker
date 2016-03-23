#!/bin/bash
{% for node_id in nodes %}
# Startup Tomcat for GeoServer Node {{ node_id }}
. /var/geoserver/node{{ node_id }}/catalina.sh
{% endfor %}