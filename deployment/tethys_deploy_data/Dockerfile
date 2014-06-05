# PostgreSQL for CKAN
# Ubuntu 12.04
# PostgreSQL 9.3
# PostGIS 2.1
# Jetty
# CREDITS: Based on example here http://docs.docker.io/examples/postgresql_service/
# VERSION 1.0.0

FROM ubuntu:12.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Add the PostgreSQL PGP key to verify their Debian packages -----------------#
# It should be the same key as https://www.postgresql.org/media/keys/ACCC4CF8.asc 
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8

# Add PostgreSQL's repository ------------------------------------------------#
#     of PostgreSQL, ``9.3``.
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list

# Update the Ubuntu and PostgreSQL repository indexes ------------------------#
RUN apt-get update

# Install ``python-software-properties``, ``software-properties-common`` and PostgreSQL 9.3
#  There are some warnings (in red) that show up during the build. You can hide
#  them by prefixing each apt-get statement with DEBIAN_FRONTEND=noninteractive
RUN apt-get -y -q install python-software-properties software-properties-common sudo
RUN apt-get -y -q install postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3
RUN apt-get -y -q install postgresql-9.3-postgis-2.1

# Install Solr ---------------------------------------------------------------#
RUN apt-get install -y openjdk-6-jdk solr-jetty

# Install supervisor ---------------------------------------------------------#
RUN apt-get install -y supervisor

# Add some temporary scripts -------------------------------------------------#
ADD tethys_deploy.conf /tmp/
ADD datastore/datastore_setup.py /tmp/
ADD datastore/set_permissions.sql /tmp/

# Variables ------------------------------------------------------------------#
ENV PGVERSION 9.3
ENV PGHOST localhost
ENV PGPORT 5432

# Home directories
ENV JAVA_HOME /usr/lib/jvm/java-6-openjdk-amd64/

# Create default db users and dbs with permissions set correctly -------------#
RUN /etc/init.d/postgresql start && \
    cd /tmp/ && \
    CKAN_DATABASE=$(grep -Po "(?<=^CKAN_DATABASE ).*" tethys_deploy.conf) && \
    CKAN_USER=$(grep -Po "(?<=^CKAN_USER ).*" tethys_deploy.conf) && \
    CKAN_PASS=$(grep -Po "(?<=^CKAN_PASS ).*" tethys_deploy.conf) && \
    DATASTORE_DATABASE=$(grep -Po "(?<=^DATASTORE_DATABASE ).*" tethys_deploy.conf) && \
    DATASTORE_USER=$(grep -Po "(?<=^DATASTORE_USER ).*" tethys_deploy.conf) && \
    DATASTORE_PASS=$(grep -Po "(?<=^DATASTORE_PASS ).*" tethys_deploy.conf) && \
    APPS_MANAGER_DATABASE=$(grep -Po "(?<=^APPS_MANAGER_DATABASE ).*" tethys_deploy.conf) && \
    APPS_MANAGER_USER=$(grep -Po "(?<=^APPS_MANAGER_USER ).*" tethys_deploy.conf) && \
    APPS_MANAGER_PASS=$(grep -Po "(?<=^APPS_MANAGER_PASS ).*" tethys_deploy.conf) && \
    TETHYS_SUPER_DATABASE=$(grep -Po "(?<=^TETHYS_SUPER_DATABASE ).*" tethys_deploy.conf) && \
    TETHYS_SUPER_USER=$(grep -Po "(?<=^TETHYS_SUPER_USER ).*" tethys_deploy.conf) && \
    TETHYS_SUPER_PASS=$(grep -Po "(?<=^TETHYS_SUPER_PASS ).*" tethys_deploy.conf) && \
    sudo -u postgres psql --command "CREATE USER $TETHYS_SUPER_USER WITH SUPERUSER PASSWORD '$TETHYS_SUPER_PASS';" && \
    sudo -u postgres createdb $TETHYS_SUPER_USER -E utf8 -T template0 -O $TETHYS_SUPER_DATABASE && \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d tethys && \
	sudo -u postgres psql -c "CREATE USER $CKAN_USER WITH CREATEROLE SUPERUSER PASSWORD '$CKAN_PASS';" && \
    sudo -u postgres createdb $CKAN_DATABASE -E utf8 -T template0 -O $CKAN_USER; \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d $CKAN_DATABASE && \
    sudo -u postgres psql -c "CREATE USER $DATASTORE_USER PASSWORD '$DATASTORE_PASS';" && \
    sudo -u postgres createdb $DATASTORE_DATABASE -E utf8 -T template0 -O $DATASTORE_USER && \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d $DATASTORE_DATABASE && \
    sudo -u postgres psql -c "CREATE USER $APPS_MANAGER_USER WITH CREATEDB PASSWORD '$APPS_MANAGER_PASS';" &&\
    sudo -u postgres createdb $APPS_MANAGER_DATABASE -E utf-8 -T template0 -O $APPS_MANAGER_USER && \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d $APPS_MANAGER_DATABASE && \
    python datastore_setup.py $CKAN_DATABASE $DATASTORE_DATABASE $CKAN_USER $CKAN_USER $DATASTORE_USER -p postgres && \
    rm /tmp/datastore_setup.py && \
    rm /tmp/set_permissions.sql && \
    rm /tmp/tethys_deploy.conf

# Modify config files --------------------------------------------------------#
# Allow remote connections to the database
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf

# Listen to all addresses
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

# Jetty
RUN sed 's/NO_START=1/NO_START=0/g' -i /etc/default/jetty && \
    sed "s=#JAVA_HOME\==JAVA_HOME\=$JAVA_HOME=g" -i /etc/default/jetty && \
    sed "s/#JETTY_HOST.*/JETTY_HOST=0.0.0.0/g" -i /etc/default/jetty

# Modification to fix bug with jetty
# see: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=637961
RUN sed 's=\^\[\:space\:\]=\^\[\[\:space\:\]\]=g' -i /etc/init.d/jetty

# Setup supervisor -----------------------------------------------------------#
RUN mkdir -p /var/log/supervisor
RUN locale-gen en_US en_US.UTF-8

# Add the supervisor conf file to appropriate place
ADD supervisord.conf /etc/supervisor/conf.d/

# Add the CKAN schema.xml file -----------------------------------------------#
RUN mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml_bak
ADD schema.xml /etc/solr/conf/

# Expose the PostgreSQL port -------------------------------------------------#
EXPOSE 5432 8080

# Add VOLUMEs to for inspection, datastorage, and backup ---------------------#
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/var/lib/ckan/default", "/etc/solr/conf", "/var/log/supervisor"]

CMD ["/usr/bin/supervisord"]

