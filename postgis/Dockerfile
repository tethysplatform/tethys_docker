# PostGIS 2.1
# Ubuntu 12.04
# PostgreSQL 9.3
# PostGIS 2.1
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

# Install supervisor ---------------------------------------------------------#
RUN apt-get install -y supervisor

# Add some temporary scripts -------------------------------------------------#
ADD tethys_deploy.conf /tmp/

# Variables ------------------------------------------------------------------#
ENV PGVERSION 9.3
ENV PGHOST localhost
ENV PGPORT 5432

# Init databases here

# Modify config files --------------------------------------------------------#
# Allow remote connections to the database
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf

# Listen to all addresses
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

# Setup supervisor -----------------------------------------------------------#
RUN mkdir -p /var/log/supervisor
RUN locale-gen en_US en_US.UTF-8

# Add the supervisor conf file to appropriate place
ADD supervisord.conf /etc/supervisor/conf.d/

# Initialize
COPY startup.sh /usr/share/tomcat7-wps/startup.sh
RUN chmod +x /usr/share/tomcat7-wps/startup.sh

# Expose the PostgreSQL port -------------------------------------------------#
EXPOSE 5432

# Add VOLUMEs to for inspection, datastorage, and backup ---------------------#
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/var/lib/ckan/default", "/var/log/supervisor"]

CMD ["/usr/bin/supervisord"]

