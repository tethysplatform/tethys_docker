# GeoServer 2.6.1

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
    rm -rf /var/cache/oracle-jdk7-installer && \
    apt-get install -y tomcat7

# Download GeoServer and Configure ------------------------------------------------------------------------------------#
WORKDIR /tmp
RUN wget "http://sourceforge.net/projects/geoserver/files/GeoServer/2.6.1/geoserver-2.6.1-war.zip" && \
    unzip geoserver-2.6.1-war.zip && \
    mv geoserver.war /var/lib/tomcat7/webapps

# Setup supervisor ----------------------------------------------------------------------------------------------------#
RUN apt-get -y install supervisor
COPY supervisord.conf /etc/supervisor/conf.d/

# Ports
EXPOSE 8080

# JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-7-oracle

# Add VOLUMEs to for inspection, datastorage, and backup --------------------------------------------------------------#
VOLUME  ["/var/log/tomcat7", "/var/log/supervisor"]

# Startup command
#CMD ["/usr/bin/supervisord"]

# VIM for debugging
CMD ["bash"]



