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
    rm -rf /var/cache/oracle-jdk7-installer

RUN apt-get update && apt-get install -y tomcat7

# JAVA_HOME variable
ENV JAVA_HOME /usr/lib/jvm/java-7-oracle

# Install JAI and JAI Image I/O ---------------------------------------------------------------------------------------#
WORKDIR /usr/lib
RUN wget http://download.java.net/media/jai/builds/release/1_1_3/jai-1_1_3-lib-linux-amd64.tar.gz && \
    wget http://download.java.net/media/jai-imageio/builds/release/1.1/jai_imageio-1_1-lib-linux-amd64.tar.gz && \
    gunzip -c jai-1_1_3-lib-linux-amd64.tar.gz | tar xf - && \
    gunzip -c jai_imageio-1_1-lib-linux-amd64.tar.gz | tar xf - && \
    rm jai-1_1_3-lib-linux-amd64.tar.gz && \
    rm jai_imageio-1_1-lib-linux-amd64.tar.gz

ENV JAIHOME /usr/lib/jai-1_1_3/lib
ENV JIOHOME /usr/lib/jai_imageio-1_1/lib
ENV CLASSPATH $JAIHOME/jai_core.jar:$JAIHOME/jai_codec.jar:$JAIHOME/mlibwrapper_jai.jar:$JIOHOME/jai_imageio.jar:$JIOHOME/clibwrapper_jiio.jar:$CLASSPATH
ENV LD_LIBRARY_PATH .:$JAIHOME:$CLASSPATH:$JIOHOME

# Download GeoServer and Configure ------------------------------------------------------------------------------------#
WORKDIR /tmp
COPY geoserver.war /var/lib/tomcat7/webapps/

# Setup supervisor ----------------------------------------------------------------------------------------------------#
RUN apt-get -y install supervisor
COPY supervisord.conf /etc/supervisor/conf.d/

# Ports
EXPOSE 8080



# Add VOLUMEs to for inspection, datastorage, and backup --------------------------------------------------------------#
VOLUME  ["/var/log/tomcat7", "/var/log/supervisor"]

# Startup command
#CMD ["/usr/bin/supervisord"]

# VIM for debugging
CMD ["bash"]



