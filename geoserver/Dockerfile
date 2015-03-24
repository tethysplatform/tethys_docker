# GeoServer 2.7.0
# Oracle JRE 1.7


FROM ubuntu:14.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y wget sudo ssh unzip vim
RUN apt-get install -y software-properties-common python-software-properties

# Install Java and Tomcat ---------------------------------------------------------------------------------------------#
RUN echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    add-apt-repository -y ppa:webupd8team/java && \
    apt-get update && \
    apt-get install -y oracle-java7-installer && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/oracle-jdk7-installer

# JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-7-oracle

RUN apt-get update && apt-get install -y tomcat7

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

# Setup supervisor ----------------------------------------------------------------------------------------------------#
RUN apt-get update && apt-get install -y supervisor
COPY supervisord.conf /etc/supervisor/conf.d/

# Download GeoServer and Configure ------------------------------------------------------------------------------------#
ENV GEOSERVER_DATA_DIR /var/lib/geoserver/data
ENV GEOSERVER_HOME /var/lib/tomcat7/webapps/geoserver

# Unpack the war and make a new data directory
COPY geoserver.war /var/lib/tomcat7/webapps/geoserver/geoserver.war
WORKDIR /var/lib/tomcat7/webapps/geoserver
RUN jar -xvf geoserver.war && \
    mv geoserver.war ../ && \
    mkdir -p /var/lib/geoserver/ && \
    cp -r data /var/lib/geoserver && \
    chown -R tomcat7:tomcat7 $GEOSERVER_DATA_DIR

# Custom GeoServer Web Config
COPY web.xml /var/lib/tomcat7/webapps/geoserver/WEB-INF/web.xml

# Set Heap Settings for Tomcat
# See: http://docs.geoserver.org/stable/en/user/production/container.html
ENV CATALINA_OPTS -Xmx2048m -Xms48m -XX:SoftRefLRUPolicyMSPerMB=36000 -XX:MaxPermSize=512m

# Add startup script --------------------------------------------------------------------------------------------------#
COPY startup.sh /usr/local/bin/startup.sh
RUN chmod +x /usr/local/bin/startup.sh

# Ports
EXPOSE 8080

# Add VOLUMEs to for inspection, datastorage, and backup --------------------------------------------------------------#
VOLUME  ["/var/log/tomcat7", "/var/log/supervisor", "/var/lib/geoserver/data", "/var/lib/tomcat7/webapps/geoserver"]

# Startup
CMD ["/usr/local/bin/startup.sh"]



