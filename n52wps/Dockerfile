# 52 North Web Processing Service
#
# 52 North WPS 3.3.0
# Tomcat 7
# GRASS 7.0.0
# Sextante
#
# VERSION 1.0.0

FROM ubuntu:14.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y wget sudo curl ssh vim unzip

# Install Tomcat Dependencies -----------------------------------------------------------------------------------------#
RUN apt-get install -y openjdk-7-jre
RUN apt-get install -y tomcat7 tomcat7-admin

# Install GRASS Dependencies ------------------------------------------------------------------------------------------#
RUN apt-get install -y \
      build-essential \
      flex make bison gcc libgcc1 g++ cmake ccache \
      python python-dev \
      python-opengl \
      python-wxversion python-wxtools python-wxgtk2.8 \
      python-dateutil libgsl0-dev python-numpy \
      wx2.8-headers wx-common libwxgtk2.8-dev libwxgtk2.8-dbg \
      libwxbase2.8-dev  libwxbase2.8-dbg \
      libncurses5-dev \
      zlib1g-dev gettext \
      libtiff-dev libpnglite-dev \
      libcairo2 libcairo2-dev \
      sqlite3 libsqlite3-dev \
      libpq-dev \
      libreadline6 libreadline6-dev libfreetype6-dev \
      libfftw3-3 libfftw3-dev \
      libboost-thread-dev libboost-program-options-dev liblas-c-dev \
      resolvconf \
      libjasper-dev \
      subversion \
      libav-tools libavutil-dev ffmpeg2theora \
      libffmpegthumbnailer-dev \
      libavcodec-dev \
      libxmu-dev \
      libavformat-dev libswscale-dev \
      checkinstall \
      libglu1-mesa-dev libxmu-dev \
      netcdf-bin libnetcdf-dev

# Download and explode 52 North WPS -----------------------------------------------------------------------------------#
ADD wps/wps.war /tmp/wps.war
RUN mkdir /usr/share/tomcat7-wps
RUN unzip -d /usr/share/tomcat7-wps/wps /tmp/wps.war
RUN rm /tmp/wps.war

# Setup the Tomcat context
ADD tomcat/wps.xml /etc/tomcat7/Catalina/localhost/

# Build and Install GRASS from Source ---------------------------------------------------------------------------------#
# RUN mkdir /usr/local/src # File exists
RUN sudo chmod ug+rwx /usr/local/src
# Get Source
WORKDIR /usr/local/src
RUN svn co https://svn.osgeo.org/grass/grass/branches/releasebranch_7_0 grass70_release
RUN svn co http://svn.osgeo.org/metacrs/proj/branches/4.8/proj/


# Install PROJ4, GEOS, and GDAL

# PROJ4
WORKDIR /tmp
RUN wget http://download.osgeo.org/proj/proj-datumgrid-1.5.zip && \
    mv proj-datumgrid-1.5.zip /usr/local/src/proj/nad
WORKDIR /usr/local/src/proj/nad
RUN unzip -o proj-datumgrid-1.5.zip
WORKDIR /usr/local/src/proj
RUN ./configure && make -j4 && make install
RUN ldconfig

# GEOS
WORKDIR /tmp
RUN wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2 && \
    mv geos-3.4.2.tar.bz2 /usr/local/src
WORKDIR /usr/local/src
RUN bunzip2 geos-3.4.2.tar.bz2
RUN tar xvf geos-3.4.2.tar
WORKDIR /usr/local/src/geos-3.4.2
RUN ./configure && make -j4 && make install
RUN ldconfig

# GDAL
WORKDIR /usr/local/src
RUN svn co https://svn.osgeo.org/gdal/branches/1.11/gdal gdal_stable
WORKDIR /usr/local/src/gdal_stable
RUN CFLAGS="-g -Wall" LDFLAGS="-s" ./configure \
        --with-png=internal \
        --with-libtiff=internal \
        --with-geotiff=internal \
        --with-jpeg=internal \
        --with-gif=internal \
        --with-ecw=no \
        --with-expat=yes \
        --with-sqlite3=yes \
        --with-geos=yes \
        --with-python \
        --with-libz=internal \
        --with-netcdf \
        --with-threads=yes \
        --without-grass  \
        --without-ogdi \
        --with-pg=/usr/bin/pg_config \
        --with-xerces=yes
RUN make -j4 && make install && ldconfig
RUN apt-get install -y python-gdal

# Configure
RUN apt-get install -y libmysqlclient-dev
WORKDIR /usr/local/src/grass70_release
RUN CFLAGS="-O2 -Wall" LDFLAGS="-s" ./configure \
        --enable-largefile=yes \
        --with-nls \
        --with-cxx \
        --with-readline \
        --with-pthread \
        --with-proj-share="/usr/local/share/proj/" \
        --with-geos="/usr/local/bin/geos-config" \
        --with-wxwidgets \
        --with-cairo \
        --with-opengl-libs=/usr/include/GL \
        --with-freetype=yes --with-freetype-includes="/usr/include/freetype2/" \
        --with-postgres=yes --with-postgres-includes="/usr/include/postgresql" \
        --with-sqlite=yes \
        --with-mysql=yes --with-mysql-includes="/usr/include/mysql" \
        --with-odbc=no \
        --with-liblas=yes --with-liblas-config="/usr/bin/liblas-config" \
        --with-netcdf="/usr/bin/nc-config"

# Build and install
RUN make -j4 && make install && ldconfig

# WPS Grass Bridge
WORKDIR /tmp
RUN wget "http://52north.org/files/geoprocessing/GRASS/wps-grass-bridge-patched.zip"
RUN mkdir /usr/local/wps_grass_bridge && \
    cp /tmp/wps-grass-bridge-patched.zip /usr/local/wps_grass_bridge
WORKDIR /usr/local/wps_grass_bridge
RUN unzip wps-grass-bridge-patched.zip && \
    rm wps-grass-bridge-patched.zip && \
    mkdir -p /var/grass/tmp

# Configure 52 North Processes
RUN rm /usr/share/tomcat7-wps/wps/config/wps_config.xml
ADD wps/wps_config.xml /usr/share/tomcat7-wps/wps/config/

# Set Permissions
RUN chown tomcat7:tomcat7 /usr/local/grass-7.0.0svn/demolocation && \
    chown tomcat7:tomcat7 /usr/local/grass-7.0.0svn/demolocation/PERMANENT && \
    chown tomcat7:tomcat7 /usr/local/wps_grass_bridge && \
    chown tomcat7:tomcat7 /usr/local/wps_grass_bridge/gms && \
    chown tomcat7:tomcat7 /var/grass/tmp && \
    chmod 777 -R /var/grass/tmp

WORKDIR /tmp

# Ports
EXPOSE 8080

CMD ["bash"]



