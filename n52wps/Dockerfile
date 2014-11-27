# 52 North Web Processing Service
#
# 52 North WPS 3.3.0
# Tomcat 7
# GRASS 7.0.0
# Sextante
#
# VERSION 1.0.0

FROM ubuntu:12.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup -----------------------------------------------------------------------------------------------------------#
RUN apt-get update
RUN apt-get install -y wget sudo curl ssh vim unzip

# Install dependencies ------------------------------------------------------------------------------------------------#
RUN apt-get install -y openjdk-7-jre
RUN apt-get install -y tomcat7 tomcat7-admin

# Download and explode 52 North WPS -----------------------------------------------------------------------------------#
WORKDIR /tmp
RUN wget http://52north.org/downloads/geoprocessing/wps/52-north-wps-3-3-0/download -O wps.war
RUN mkdir /usr/share/tomcat7-wps
RUN unzip -d /usr/share/tomcat7-wps/wps /tmp/wps.war

# Setup the Tomcat context
ADD tomcat/wps.xml /etc/tomcat7/Catalina/localhost/


EXPOSE 8080

CMD ["bash"]



