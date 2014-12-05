# PyWPS 3.2
# PROJ4 4.8
# GEOS 3.4.2
# GDAL 1.11
# GRASS 7.0.0
# MapServer

FROM ubuntu:14.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y wget sudo curl ssh vim unzip supervisor

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
      libmysqlclient-dev \
      netcdf-bin libnetcdf-dev

# Build and Install GRASS and Dependencies from Source ----------------------------------------------------------------#

# Vars
ENV PROCESSORS 4

# Get source
WORKDIR /usr/local/src
RUN svn co http://svn.osgeo.org/metacrs/proj/branches/4.8/proj/ && \
    wget http://download.osgeo.org/proj/proj-datumgrid-1.5.zip && \
    unzip -d proj/nad -o proj-datumgrid-1.5.zip && \
    rm proj-datumgrid-1.5.zip && \
    svn co https://svn.osgeo.org/grass/grass/branches/releasebranch_7_0 grass70_release && \
    svn co https://svn.osgeo.org/gdal/branches/1.11/gdal gdal_stable && \
    wget http://download.osgeo.org/geos/geos-3.4.2.tar.bz2 && \
    bunzip2 geos-3.4.2.tar.bz2 && \
    tar xvf geos-3.4.2.tar && \
    rm geos-3.4.2.tar

# PROJ4
WORKDIR /usr/local/src/proj
RUN ./configure && make -j$PROCESSORS && make install && ldconfig

# GEOS
WORKDIR /usr/local/src/geos-3.4.2
RUN ./configure && make -j$PROCESSORS && make install && ldconfig

# GDAL
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
        --with-xerces=yes && \
    make -j$PROCESSORS && make install && ldconfig && \
    apt-get install -y python-gdal

# Configure GRASS
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
        --with-netcdf="/usr/bin/nc-config" && \
    make -j$PROCESSORS && make install && ldconfig

# Download PyWPS and Configure ----------------------------------------------------------------------------------------#
RUN apt-get install -y apache2 python-pip python-lxml libapache2-mod-python
WORKDIR /usr/local
RUN wget https://github.com/geopython/PyWPS/archive/pywps-3.2.2.tar.gz && \
    tar xvzf pywps-3.2.2.tar.gz && \
    rm pywps-3.2.2.tar.gz && \
    mv PyWPS-pywps-3.2.2 pywps-3.2.2 && \
    chmod 777 /usr/local/pywps-3.2.2/pywps/Templates/1_0_0 && \
    mkdir -p /var/www/pywps/ && \
    mkdir -p /usr/local/wps/processes && \
    mkdir -p /etc/pywps/ && \
    cp pywps-3.2.2/wps.py /var/www/pywps/

WORKDIR /usr/local/pywps-3.2.2
RUN python setup.py install

COPY wps/pywps.cfg /etc/pywps/
COPY apache/pywps_default.conf /etc/apache2/sites-available/

# COPY apache/apache2.conf /etc/apache2/apache2.conf

RUN a2dissite 000-default && \
    a2ensite pywps_default




# Startup command
#CMD ["/usr/bin/supervisord"]

CMD ["bash"]



