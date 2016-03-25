# GeoServer 2.8.2
# Oracle JRE 1.7
# Tomcat 7

FROM ubuntu:14.04

MAINTAINER Nathan Swain nswain@aquaveo.com

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y wget sudo ssh unzip vim
RUN apt-get install -y software-properties-common python-software-properties
RUN apt-get install -y python-pip python-dev nginx supervisor

# Install Java and Tomcat ---------------------------------------------------------------------------------------------#
RUN echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    add-apt-repository -y ppa:webupd8team/java && \
    apt-get update && \
    apt-get install -y oracle-java7-installer && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/oracle-jdk7-installer

# JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-7-oracle

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

COPY apache-tomcat-7.tar.gz /tmp/
COPY geoserver* /tmp/
COPY generated/* /tmp/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
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
    mkdir -p $GEOSERVER_HOME/node/webapps/geoserver/ && \
    cp $CATALINA_HOME/conf/web.xml $GEOSERVER_HOME/node/conf/ && \
    mv geoserver.war $GEOSERVER_HOME/node/webapps/geoserver/ && \
    cd $GEOSERVER_HOME/node/webapps/geoserver && \
    jar -xvf geoserver.war && \
    rm geoserver.war && \
    cd /tmp && \
    mv geoserver-jms-cluster-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-css-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-control-flow-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-netcdf-out-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    mv geoserver-netcdf-plugin.zip $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    cd $GEOSERVER_HOME/node/webapps/geoserver/WEB-INF/lib && \
    unzip -o geoserver-jms-cluster-plugin.zip && \
    unzip -o geoserver-css-plugin.zip && \
    unzip -o geoserver-control-flow-plugin.zip && \
    unzip -o geoserver-netcdf-out-plugin.zip && \
    unzip -o geoserver-netcdf-plugin.zip && \
    rm geoserver-jms-cluster-plugin.zip && \
    rm geoserver-css-plugin.zip && \
    rm geoserver-control-flow-plugin.zip && \
    rm geoserver-netcdf-plugin.zip && \
    rm geoserver-netcdf-out-plugin.zip && \
    cd /tmp && \
    mv $GEOSERVER_HOME/node/webapps/geoserver/data/* $GEOSERVER_HOME/tmp_data/ && \
    python gen_build_time_dynamic_files.py && \
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
VOLUME  ["/var/log/supervisor", "/var/geoserver/data", "/var/geoserver"]

## Startup
CMD $GEOSERVER_HOME/startup.sh



