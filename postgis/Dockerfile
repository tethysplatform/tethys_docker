# PostGIS 2.1.2
# Ubuntu 14.04
# PostgreSQL 9.3
# PostGIS 2.1
# GDAL 1.11.1
# GEOS 3.4.2
# CREDITS: Based on http://www.peterstratton.com/2014/04/how-to-install-postgis-2-dot-1-and-postgresql-9-dot-3-on-ubuntu-servers/

FROM ubuntu:14.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Update the Ubuntu and PostgreSQL repository indexes -----------------------------------------------------------------#
RUN apt-get update && apt-get upgrade -y

# Install dependencies ------------------------------------------------------------------------------------------------#
RUN apt-get install -y build-essential python-all-dev git vim python-dev python-pip\
    python-software-properties software-properties-common g++ gcc make libssl-dev libreadline6-dev\
    libaio-dev libbz2-dev zlib1g-dev libjpeg62-dev libpcre3-dev libexpat1-dev libxml2 libxml2-dev\
    libjson0 libjson0-dev liblzma-dev libevent-dev wget zip unzip supervisor sudo\
    binutils libproj-dev libgeoip1 libgtk2.0 xsltproc docbook-xsl docbook-mathml

# Install PostgreSQL libraries ----------------------------------------------------------------------------------------#
RUN apt-get install -y postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3 libpq-dev postgresql-server-dev-9.3

# Build GDAL and GEOS from source -------------------------------------------------------------------------------------#
ENV PROCESSORS 4

WORKDIR /usr/local/src
RUN wget http://download.osgeo.org/gdal/1.11.1/gdal-1.11.1.tar.gz && \
    tar xfz gdal-1.11.1.tar.gz && \
    wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2 && \
    bunzip2 geos-3.4.2.tar.bz2 && \
    tar xvf geos-3.4.2.tar && \
    rm geos-3.4.2.tar

# GEOS
WORKDIR /usr/local/src/geos-3.4.2
RUN ./configure && make -j$PROCESSORS && make install && ldconfig

# GDAL
WORKDIR /usr/local/src/gdal-1.11.1
RUN ./configure --with-python && \
    make -j$PROCESSORS && make install && ldconfig && \
    apt-get install -y python-gdal

# Install PostGIS -----------------------------------------------------------------------------------------------------#
RUN apt-get -y -q install postgresql-9.3-postgis-2.1

# Variables -----------------------------------------------------------------------------------------------------------#
ENV POSTGIS_GDAL_ENABLED_DRIVERS ENABLE_ALL
ENV POSTGIS_ENABLE_OUTDB_RASTERS 1

# Modify config files -------------------------------------------------------------------------------------------------#
# Allow remote connections to the database and listen to all addresses
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf && \
    echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

# Setup supervisor ----------------------------------------------------------------------------------------------------#
RUN mkdir -p /var/log/supervisor && \
    locale-gen en_US en_US.UTF-8
ADD supervisord.conf /etc/supervisor/conf.d/

# Add startup script --------------------------------------------------------------------------------------------------#
COPY startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh

# Expose the PostgreSQL port ------------------------------------------------------------------------------------------#
EXPOSE 5432

# Add VOLUMEs to for inspection, datastorage, and backup --------------------------------------------------------------#
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/var/lib/ckan/default", "/var/log/supervisor"]

CMD ["/usr/local/bin/startup.sh"]

