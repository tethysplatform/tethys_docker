#!/bin/bash
echo "Starting GeoServer Node {{ node_id }}"
export CATALINA_BASE=$GEOSERVER_HOME/node{{ node_id }}
export CATALINA_TMPDIR=$CATALINA_BASE/temp
export JRE_HOME=$JAVA_HOME/jre
export CLUSTER_CONFIG_DIR=$GEOSERVER_DATA_DIR/cluster/log/{{ node_id }}
export GEOSERVER_NODE_OPTS="id:node{{ node_id }}"

# Heap Settings for Tomcat
# See: http://docs.geoserver.org/stable/en/user/production/container.html
export CATALINA_OPTS="-server -Xmx${MAX_MEMORY}m -Xms${MIN_MEMORY}m -XX:SoftRefLRUPolicyMSPerMB=36000 -XX:MaxPermSize=256m -XX:+UseParallelGC"

$CATALINA_HOME/bin/catalina.sh run
