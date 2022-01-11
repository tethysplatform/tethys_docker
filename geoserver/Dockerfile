# GeoServer 2.8.2
# Oracle JDK 1.7
# Tomcat 7
# Ubuntu 21.04

FROM ubuntu:21.04

ENV TZ UTC

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update -y && apt-get upgrade -y && \
    apt-get install -y wget sudo ssh unzip vim software-properties-common python3-pip python3-dev nginx supervisor && \
    rm -rf /var/lib/apt/lists/*

# Install Java (Download tarball from https://www.oracle.com/java/technologies/javase/javase7-archive-downloads.html
ADD jdk-7u80-linux-x64.tar.gz /usr/lib/jvm/
ENV JAVA_HOME /usr/lib/jvm/jdk1.7.0_80
ENV PATH ${JAVA_HOME}/bin:${JAVA_HOME}/jre/bin:${PATH}

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
ENV GEOSERVER_HOME /var/geoserver
ENV CATALINA_HOME /var/tomcat
ENV GEOSERVER_DATA_DIR /var/geoserver/data
ENV MAX_NODES 4
ENV ENABLED_NODES 1
ENV REST_NODES 1
ENV MAX_MEMORY 1024
ENV MIN_MEMORY 1024
ENV GDAL_DATA /usr/local/lib/gdal-data
ENV LD_LIBRARY_PATH /usr/local/lib
#set to ignore parts requiring license
#http://demo.geo-solutions.it/share/github/imageio-ext/releases/1.1.X/1.1.12/native/gdal/linux/notes_on_ECW_and_JP2ECW.txt
ENV GDAL_SKIP JP2ECW

COPY apache-tomcat-7.tar.gz /tmp/
COPY log4j-1.2.17.norce.jar /tmp/
COPY geoserver* /tmp/
COPY generated/* /tmp/

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    rm requirements.txt && \
    tar zxf apache-tomcat-7.tar.gz && \
    mv apache-tomcat-7.0.68 $CATALINA_HOME && \
    rm apache-tomcat-7.tar.gz && \
    mkdir -p $GEOSERVER_HOME/data/ && \
    mkdir -p $GEOSERVER_HOME/tmp_data/ && \
    mkdir -p $GEOSERVER_HOME/node/ && \
    mkdir -p $GEOSERVER_HOME/node/conf/ && \
    mkdir -p $GEOSERVER_HOME/node/logs/ && \
    mkdir -p $GEOSERVER_HOME/node/temp/ && \
    mkdir -p $GEOSERVER_HOME/node/work/ && \
    mkdir -p $GEOSERVER_HOME/node/webapps/geoserver && \
    cp $CATALINA_HOME/conf/web.xml $GEOSERVER_HOME/node/conf/ && \
    mv geoserver.war $GEOSERVER_HOME/node/webapps/geoserver/ && \
    cd $GEOSERVER_HOME/node/webapps/geoserver && \
    jar -xvf geoserver.war && \
    rm geoserver.war && \
    cd /tmp && \
    # log4j vulnerability patch (see: http://geoserver.org/announcements/2021/12/13/logj4-rce-statement.html)
    rm $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib/log4j-1.2.14.jar && \
    mv log4j-1.2.17.norce.jar $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-jms-cluster-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-css-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-control-flow-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-netcdf-out-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-netcdf-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-2.8.2-gdal-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-gdal192-Ubuntu12-gcc4.6.3-x86_64.tar.gz /usr/local/lib && \
    mv geoserver-gdal-data.zip /usr/local/lib && \
    mv geoserver-2.8.2-pyramid-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    cd $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    unzip -o geoserver-jms-cluster-plugin.zip && \
    unzip -o geoserver-css-plugin.zip && \
    unzip -o geoserver-control-flow-plugin.zip && \
    unzip -o geoserver-netcdf-out-plugin.zip && \
    unzip -o geoserver-netcdf-plugin.zip && \
    unzip -o geoserver-2.8.2-gdal-plugin.zip && \
    unzip -o geoserver-2.8.2-pyramid-plugin.zip && \
    rm geoserver-jms-cluster-plugin.zip && \
    rm geoserver-css-plugin.zip && \
    rm geoserver-control-flow-plugin.zip && \
    rm geoserver-netcdf-plugin.zip && \
    rm geoserver-netcdf-out-plugin.zip && \
    rm geoserver-2.8.2-gdal-plugin.zip && \
    rm geoserver-2.8.2-pyramid-plugin.zip && \
    cd /usr/local/lib && \
    unzip -o geoserver-gdal-data.zip && \
    tar xf geoserver-gdal192-Ubuntu12-gcc4.6.3-x86_64.tar.gz && \
    rm geoserver-gdal-data.zip && \
    rm geoserver-gdal192-Ubuntu12-gcc4.6.3-x86_64.tar.gz && \
    cd /tmp && \
    mv $GEOSERVER_HOME/node/webapps/geoserver/data/* $GEOSERVER_HOME/tmp_data/ && \
    python3 gen_build_time_dynamic_files.py && \
    rm -rf $GEOSERVER_HOME/node && \
    rm template_catalina.sh && \
    rm template_server.xml && \
    rm template_web.xml && \
    rm gen_build_time_dynamic_files.py

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



