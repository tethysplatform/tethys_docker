# 52 North WPS 3.3.1
# Tomcat 7
# PROJ4 4.8
# GEOS 3.4.2
# GDAL 1.11
# GRASS 7.0.0
# Sextante
# R 3.2.1
# Rserve
# R Spatial packages

FROM ubuntu:14.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y \
	  wget \
	  sudo \
	  ssh \
	  unzip \
	  vim \
	  software-properties-common \
	  openjdk-7-jre \
	  tomcat7 \
	  supervisor \
	  && rm -r /var/lib/tomcat7/webapps/ROOT
	  

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
	  netcdf-bin libnetcdf-dev \
	  libgeos-dev libgeos++-dev \
	  libv8-dev \ 
	  libxml2-dev \
	  pandoc \
	  qpdf \
	  xauth \
	  xfonts-base \
	  xvfb


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
#	rm geos-3.4.2.tar && \
	cd /usr/local/src/proj && \
	./configure && make -j$PROCESSORS && make install && ldconfig && \
	cd /usr/local/src/geos-3.4.2 && \
#	rm -rf /usr/local/src/proj && \
	./configure && make -j$PROCESSORS && make install && ldconfig && \
	cd /usr/local/src/gdal_stable && \
#	rm -rf /usr/local/src/geos-3.4.2 && \
	CFLAGS="-g -Wall" LDFLAGS="-s" ./configure \
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
	cd /usr/local/src && \
#	rm -rf /usr/local/src/gdal_stable && \
	apt-get install -y python-gdal && \
	cd /usr/local/src/grass70_release && \
	CFLAGS="-O2 -Wall" LDFLAGS="-s" ./configure \
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
	make -j$PROCESSORS && make install && ldconfig && \
	cd /usr/local/src # && \
#    rm -rf /usr/local/src/grass70_release
	
# Install R Dependencies from latest version debian repository --------------------------------------------------------#

## Configure default locale, see https://github.com/rocker-org/rocker/issues/19
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
  && locale-gen en_US.utf8 \
  && /usr/sbin/update-locale LANG=en_US.UTF-8

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

## Now install R and littler, and create a link for littler in /usr/local/bin
## Also set a default CRAN repo, and make sure littler knows about it too
RUN add-apt-repository ppa:marutter/rrutter \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
	littler \
	r-base \
	r-base-dev \
	r-recommended \
		&& echo 'options(repos = list(CRAN = "https://cran.rstudio.com/"), download.file.method = "libcurl")' >> /etc/R/Rprofile.site \
		&& echo 'source("/etc/R/Rprofile.site")' >> /etc/littler.r \
  && ln -s /usr/share/doc/littler/examples/install.r /usr/local/bin/install.r \
  && ln -s /usr/share/doc/littler/examples/install2.r /usr/local/bin/install2.r \
  && ln -s /usr/share/doc/littler/examples/installGithub.r /usr/local/bin/installGithub.r \
  && ln -s /usr/share/doc/littler/examples/testInstalled.r /usr/local/bin/testInstalled.r \
  && install.r docopt \
  && rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
  && rm -rf /var/lib/apt/lists/*

RUN R --version

# Install R Spatial Packages ------------------------------------------------------------------------------------------#
RUN install.r Rserve \
	  install.r Rcpp \
	  install.r geoR \
	  install.r mapdata \
	  install.r maps \
	  install.r maptools \
	  install.r RandomFields \
	  install.r plotKML \
	  install.r rgdal \
	  install.r rgeos \
	  install.r shapefiles \
	  install.r sp \
	  install.r spatstat \
	  install.r raster \
	  install.r rts \
	  install.r sos4R \
	  install.r plyr \
	  install.r reshape2 \
	  install.r ggplot2 \
	  install.r scales \
	  install.r WaterML \
	  install.r dataRetrieval \
	  install.r fields \
	  install.r xtable \
	  install.r rLakeAnalyzer \
	  install.r ncdf \
	  install.r RNetCDF && \
	  rm -rf /tmp/downloaded_packages/ /tmp/*.rds

# Setup supervisor ----------------------------------------------------------------------------------------------------#
COPY supervisord.conf /etc/supervisor/conf.d/

# 52North Version
ENV WPS_VERSION 3.3.1

# Download 52 North WPS and configure ---------------------------------------------------------------------------------#
COPY wps/$WPS_VERSION/wps.war /tmp/
RUN mkdir -p /usr/share/tomcat7-wps && \
	unzip -d /usr/share/tomcat7-wps/wps /tmp/wps.war && \
	rm /tmp/wps.war

# GeoTools
COPY wps/$WPS_VERSION/wps-$WPS_VERSION-geotools-package.zip /usr/share/tomcat7-wps/wps/
WORKDIR /usr/share/tomcat7-wps/wps
RUN unzip -o wps-$WPS_VERSION-geotools-package.zip

# Custom config
COPY wps/$WPS_VERSION/wps_config_geotools.xml /usr/share/tomcat7-wps/wps/config/wps_config_geotools.xml
COPY wps/$WPS_VERSION/wps_config.xml /usr/share/tomcat7-wps/wps/config/wps_config.xml

# Setup the Tomcat context
COPY wps.xml /etc/tomcat7/Catalina/localhost/wps.xml

# WPS Grass Bridge ----------------------------------------------------------------------------------------------------#
RUN mkdir /usr/local/wps_grass_bridge
WORKDIR /usr/local/wps_grass_bridge
COPY wps/wps-grass-bridge-patched.zip /usr/local/wps_grass_bridge/
RUN unzip wps-grass-bridge-patched.zip && \
	rm wps-grass-bridge-patched.zip && \
	mkdir -p /var/grass/tmp

# Bug fix for Ubuntu Python
# see: http://stackoverflow.com/questions/15608236/eclipse-and-google-app-engine-importerror-no-module-named-sysconfigdata-nd-u
RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

# Set Permissions
RUN mkdir -p /usr/local/grass-7.0.0svn/demolocation && \
	mkdir -p /usr/local/grass-7.0.0svn/demolocation/PERMANENT && \
	chown tomcat7:tomcat7 /usr/local/grass-7.0.0svn/demolocation && \
	chown tomcat7:tomcat7 /usr/local/grass-7.0.0svn/demolocation/PERMANENT && \
	chown -R tomcat7:tomcat7 /usr/local/wps_grass_bridge && \
	chown tomcat7:tomcat7 /var/grass/tmp && \
	chown -R tomcat7:tomcat7 /usr/share/tomcat7-wps/wps

# For debugging
COPY wps/logback_debug.xml /usr/share/tomcat7-wps/wps/WEB-INF/classes/logback.xml

# Hack to fix 3.3.1
RUN cd /usr/share/tomcat7-wps/ && \
	mv wps wpshome

# Set Heap Settings for Tomcat
ENV CATALINA_OPTS -Xmx2048m -Xms48m -XX:MaxPermSize=512m

WORKDIR /var/grass/tmp

# Ports
EXPOSE 8080

# Add VOLUMES for inspection, data storage, and backup ----------------------------------------------------------------#
VOLUME  ["/var/log/tomcat7", "/var/log/supervisor", "/var/grass/tmp"]

# Initialize
COPY startup.sh /usr/share/tomcat7-wps/startup.sh
RUN chmod +x /usr/share/tomcat7-wps/startup.sh

CMD ["/usr/share/tomcat7-wps/startup.sh"]





