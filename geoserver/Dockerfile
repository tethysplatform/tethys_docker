# GeoServer 2.6.1

FROM ubuntu:14.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y wget sudo curl ssh vim unzip supervisor

# Install Tomcat Dependencies -----------------------------------------------------------------------------------------#
RUN apt-get install -y openjdk-7-jre
RUN apt-get install -y tomcat7 tomcat7-admin

# Download GeoServer and Configure ------------------------------------------------------------------------------------#
WORKDIR /tmp
RUN wget "http://sourceforge.net/projects/geoserver/files/GeoServer/2.6.1/geoserver-2.6.1-war.zip"
RUN unzip geoserver-2.6.1-war.zip && \
    mv geoserver.war /var/lib/tomcat7/webapps

# Setup supervisor ----------------------------------------------------------------------------------------------------#
COPY supervisor/supervisord.conf /etc/supervisor/conf.d/

# Ports
EXPOSE 8080

# Add VOLUMEs to for inspection, datastorage, and backup --------------------------------------------------------------#
VOLUME  ["/var/log/tomcat7", "/var/log/supervisor"]

# Startup command
#CMD ["/usr/bin/supervisord"]

CMD ["bash"]



