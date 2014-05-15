# PostgreSQL for CKAN
# Ubuntu 12.04
# PostgreSQL 9.3
# PostGIS 2.1
# Jetty
# CREDITS: Based on example here http://docs.docker.io/examples/postgresql_service/
# VERSION 1.0

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

# Variables ------------------------------------------------------------------#
ENV PGVERSION 9.3
ENV PGHOST localhost
ENV PGPORT 5432

# CKAN db and user
ENV PGDATABASE ckan_default
ENV PGUSER ckan_default
ENV PGPASS pass

# Datastore db and user
ENV DSDATABASE datastore_default
ENV DSUSER datastore_default
ENV DSPASS pass

# Home directories
ENV JAVA_HOME /usr/lib/jvm/java-6-openjdk-amd64/

# Create default users and dbs -----------------------------------------------#
# User docker for maintenance
# CKAN main db & datastore db
RUN /etc/init.d/postgresql start && \
    sudo -u postgres psql --command "CREATE USER tethys WITH SUPERUSER PASSWORD 'tethys';" && \
    sudo -u postgres createdb tethys -E utf8 -T template0 -O tethys && \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d tethys && \
	sudo -u postgres psql -c "CREATE USER $PGUSER WITH CREATEROLE SUPERUSER PASSWORD '$PGPASS';" && \
    sudo -u postgres createdb $PGDATABASE -E utf8 -T template0 -O $PGUSER; \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d $PGDATABASE && \
    sudo -u postgres psql -c "CREATE USER $DSUSER PASSWORD '$DSPASS';" && \
    sudo -u postgres createdb $DSDATABASE -E utf8 -T template0 -O $DSUSER && \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d $DSDATABASE

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

# Add the supervisor conf file to appropriate place -------------------------#
ADD supervisord.conf /etc/supervisor/conf.d/

# Add the CKAN schema.xml file -----------------------------------------------#
RUN mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml_bak
ADD schema.xml /etc/solr/conf/

# Expose the PostgreSQL port -------------------------------------------------#
EXPOSE 5432
EXPOSE 8080

# Add VOLUMEs to for inspection, datastorage, and backup ---------------------#
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/var/lib/ckan/default", "/etc/solr/conf", "/var/log/supervisor"]

CMD ["/usr/bin/supervisord"]

