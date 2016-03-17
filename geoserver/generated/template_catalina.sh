export CATALINA_BASE=$GEOSERVER_HOME/node{{ node_id }}
export CATALINA_TMPDIR=$CATALINA_BASE/temp
export JRE_HOME=$JAVA_HOME/jre
export CLUSTER_CONFIG_DIR=$GEOSERVER_DATA_DIR/cluster/{{ node_id }}

# Heap Settings for Tomcat
# See: http://docs.geoserver.org/stable/en/user/production/container.html
export CATALINA_OPTS="-Xmx2048m -Xms1024m -XX:SoftRefLRUPolicyMSPerMB=36000 -XX:MaxPermSize=1024m"

$CATALINA_HOME/bin/catalina.sh start