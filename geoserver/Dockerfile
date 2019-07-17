FROM tomcat:9-jdk8-openjdk

MAINTAINER Nathan Swain nswain@aquaveo.com

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y software-properties-common
RUN apt-get install -y python-pip python-dev nginx supervisor

# Install JAI and JAI Image I/O ---------------------------------------------------------------------------------------#
WORKDIR /tmp
RUN wget http://download.java.net/media/jai/builds/release/1_1_3/jai-1_1_3-lib-linux-amd64.tar.gz && \
    wget http://download.java.net/media/jai-imageio/builds/release/1.1/jai_imageio-1_1-lib-linux-amd64.tar.gz && \
    gunzip -c jai-1_1_3-lib-linux-amd64.tar.gz | tar xf - && \
    gunzip -c jai_imageio-1_1-lib-linux-amd64.tar.gz | tar xf - && \
    mv /tmp/jai-1_1_3/COPYRIGHT-jai.txt $JAVA_HOME/jre && \
    mv /tmp/jai-1_1_3/UNINSTALL-jai $JAVA_HOME/jre && \
    mv /tmp/jai-1_1_3/LICENSE-jai.txt $JAVA_HOME/jre && \
    mv /tmp/jai-1_1_3/DISTRIBUTIONREADME-jai.txt $JAVA_HOME/jre && \
    mv /tmp/jai-1_1_3/THIRDPARTYLICENSEREADME-jai.txt $JAVA_HOME/jre && \
    mv /tmp/jai-1_1_3/lib/jai_core.jar $JAVA_HOME/jre/lib/ext/ && \
    mv /tmp/jai-1_1_3/lib/jai_codec.jar $JAVA_HOME/jre/lib/ext/ && \
    mv /tmp/jai-1_1_3/lib/mlibwrapper_jai.jar $JAVA_HOME/jre/lib/ext/ && \
    mv /tmp/jai-1_1_3/lib/libmlib_jai.so $JAVA_HOME/jre/lib/amd64/ && \
    mv /tmp/jai_imageio-1_1/COPYRIGHT-jai_imageio.txt $JAVA_HOME/jre && \
    mv /tmp/jai_imageio-1_1/UNINSTALL-jai_imageio $JAVA_HOME/jre && \
    mv /tmp/jai_imageio-1_1/LICENSE-jai_imageio.txt $JAVA_HOME/jre && \
    mv /tmp/jai_imageio-1_1/DISTRIBUTIONREADME-jai_imageio.txt $JAVA_HOME/jre && \
    mv /tmp/jai_imageio-1_1/THIRDPARTYLICENSEREADME-jai_imageio.txt $JAVA_HOME/jre && \
    mv /tmp/jai_imageio-1_1/lib/jai_imageio.jar $JAVA_HOME/jre/lib/ext/ && \
    mv /tmp/jai_imageio-1_1/lib/clibwrapper_jiio.jar $JAVA_HOME/jre/lib/ext/ && \
    mv /tmp/jai_imageio-1_1/lib/libclib_jiio.so $JAVA_HOME/jre/lib/amd64/ && \
    rm /tmp/jai-1_1_3-lib-linux-amd64.tar.gz && \
    rm -r /tmp/jai-1_1_3 && \
    rm /tmp/jai_imageio-1_1-lib-linux-amd64.tar.gz && \
    rm -r /tmp/jai_imageio-1_1

# Install the Unlimited Strength Jurisdiction Policy files ------------------------------------------------------------#
COPY local_policy.jar $JAVA_HOME/jre/lib/security/local_policy.jar
COPY US_export_policy.jar $JAVA_HOME/jre/lib/security/US_export_policy.jar

# Setup Tomcat, GeoServer Cluster, and NGINX Load Balance -------------------------------------------------------------#
ENV GEOSERVER_VERSION 2.15.2
ENV GEOSERVER_HOME /var/geoserver
ENV GEOSERVER_DATA_DIR /var/geoserver/data
ENV GEOSERVER_WEBAPPS /var/geoserver/node/webapps/geoserver
ENV GEOSERVER_WEBINF /var/geoserver/node/webapps/geoserver/WEB-INF/lib
ENV MAX_NODES 4
ENV ENABLED_NODES 2
ENV REST_NODES 1
ENV MAX_MEMORY 1024
ENV MIN_MEMORY 256
ENV GDAL_DATA /usr/local/lib/gdal-data
ENV LD_LIBRARY_PATH /usr/local/lib
#set to ignore parts requiring license
#http://demo.geo-solutions.it/share/github/imageio-ext/releases/1.1.X/1.1.12/native/gdal/linux/notes_on_ECW_and_JP2ECW.txt
ENV GDAL_SKIP JP2ECW

COPY geoserver* /tmp/
COPY geoserver-$GEOSERVER_VERSION-war/geoserver.war /tmp/
COPY generated/* $GEOSERVER_HOME/generated/

RUN echo "Setting Up Node Template Directory..." && \
    ls -al /tmp && ls -al $GEOSERVER_HOME && \
    mkdir -p $GEOSERVER_HOME/data/ && \
    mkdir -p $GEOSERVER_HOME/tmp_data/ && \
    mkdir -p $GEOSERVER_HOME/node/ && \
    mkdir -p $GEOSERVER_HOME/node/conf/ && \
    mkdir -p $GEOSERVER_HOME/node/logs/ && \
    mkdir -p $GEOSERVER_HOME/node/temp/ && \
    mkdir -p $GEOSERVER_HOME/node/work/ && \
    mkdir -p $GEOSERVER_WEBAPPS && \
    echo "Unpacking GeoServer WAR..." && \
    cp $CATALINA_HOME/conf/web.xml $GEOSERVER_HOME/node/conf/ && \
    mv geoserver.war $GEOSERVER_WEBAPPS/ && \
    cd $GEOSERVER_WEBAPPS && \
    jar -xvf geoserver.war && \
    cd /tmp && \
    echo "Installing Extensions..." && \
    unzip -o geoserver-$GEOSERVER_VERSION-jms-cluster-plugin.zip -d $GEOSERVER_WEBINF && \
    unzip -o geoserver-$GEOSERVER_VERSION-css-plugin.zip -d $GEOSERVER_WEBINF && \
    unzip -o geoserver-$GEOSERVER_VERSION-control-flow-plugin.zip -d $GEOSERVER_WEBINF && \
    unzip -o geoserver-$GEOSERVER_VERSION-netcdf-out-plugin.zip -d $GEOSERVER_WEBINF && \
    unzip -o geoserver-$GEOSERVER_VERSION-netcdf-plugin.zip -d $GEOSERVER_WEBINF && \
    unzip -o geoserver-$GEOSERVER_VERSION-gdal-plugin.zip -d $GEOSERVER_WEBINF && \
    unzip -o geoserver-$GEOSERVER_VERSION-pyramid-plugin.zip -d $GEOSERVER_WEBINF && \
    echo "Installing GDAL..." && \
    unzip -o geoserver-gdal-data.zip -d /usr/local/lib && \
    tar xf geoserver-gdal192-Ubuntu12-gcc4.6.3-x86_64.tar.gz -C /usr/local/lib && \
    echo "Backing Up Initial Data.." && \
    mv $GEOSERVER_WEBAPPS/data/* $GEOSERVER_HOME/tmp_data/ && \
    echo "Creating Build-Time Generated Files..." && \
    pip install -r $GEOSERVER_HOME/generated/requirements.txt && \
    python $GEOSERVER_HOME/generated/gen_build_time_dynamic_files.py && \
    echo "Cleaning Up..." && \
    rm -rf $GEOSERVER_HOME/node && \
    rm -rf /tmp/geoserver*

WORKDIR $GEOSERVER_HOME

# Add startup script --------------------------------------------------------------------------------------------------#
COPY startup.sh $GEOSERVER_HOME/
RUN chmod +x $GEOSERVER_HOME/startup.sh

## Ports
EXPOSE 8181 8081 8082 8083 8084

## Add VOLUMEs to for inspection, datastorage, and backup -------------------------------------------------------------#
VOLUME  ["/var/log/supervisor", "/var/geoserver/data", "/var/geoserver", "/etc"]

## Startup
CMD $GEOSERVER_HOME/startup.sh