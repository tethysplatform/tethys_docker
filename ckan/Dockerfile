# CKAN Docker
# CKAN 2.2
# Ubuntu 14.04 LTS
# PostgreSQL 9.3

FROM ubuntu:14.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup ------------------------------------------------------------------#
RUN apt-get update
RUN apt-get install -y wget sudo curl ssh vim

# Install CKAN dependencies --------------------------------------------------#
RUN apt-get install -y python-dev python-pip python-virtualenv git-core

# Install Production Servers -------------------------------------------------#
RUN apt-get install -y && \
    apache2 libapache2-mod-wsgi && \
    nginx && \
    postfix && \
    openjdk-6-jdk solr-jetty && \
    supervisor

# Home directories
ENV JAVA_HOME /usr/lib/jvm/java-6-openjdk-amd64/

# Install PostgreSQL libraries ----------------------------------------------------------------------------------------#
RUN apt-get install -y postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3 libpq-dev postgresql-server-dev-9.3
RUN apt-get -y -q install python-software-properties software-properties-common sudo

# Add some temporary scripts -------------------------------------------------#
ADD tethys_deploy.conf /tmp/
ADD datastore/datastore_setup.py /tmp/
ADD datastore/set_permissions.sql /tmp/

# Variables ------------------------------------------------------------------#
ENV PGVERSION 9.3
ENV PGHOST localhost
ENV PGPORT 5432

# Create default db users and dbs with permissions set correctly -------------#
RUN /etc/init.d/postgresql start && \
    cd /tmp/ && \
    CKAN_DATABASE=$(grep -Po "(?<=^CKAN_DATABASE ).*" tethys_deploy.conf) && \
    CKAN_USER=$(grep -Po "(?<=^CKAN_USER ).*" tethys_deploy.conf) && \
    CKAN_PASS=$(grep -Po "(?<=^CKAN_PASS ).*" tethys_deploy.conf) && \
    DATASTORE_DATABASE=$(grep -Po "(?<=^DATASTORE_DATABASE ).*" tethys_deploy.conf) && \
    DATASTORE_USER=$(grep -Po "(?<=^DATASTORE_USER ).*" tethys_deploy.conf) && \
    DATASTORE_PASS=$(grep -Po "(?<=^DATASTORE_PASS ).*" tethys_deploy.conf) && \
	sudo -u postgres psql -c "CREATE USER $CKAN_USER WITH CREATEROLE SUPERUSER PASSWORD '$CKAN_PASS';" && \
    sudo -u postgres createdb $CKAN_DATABASE -E utf8 -T template0 -O $CKAN_USER; \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d $CKAN_DATABASE && \
    sudo -u postgres psql -c "CREATE USER $DATASTORE_USER PASSWORD '$DATASTORE_PASS';" && \
    sudo -u postgres createdb $DATASTORE_DATABASE -E utf8 -T template0 -O $DATASTORE_USER && \
    sudo -u postgres psql -c "CREATE EXTENSION postgis" -d $DATASTORE_DATABASE && \
    python datastore_setup.py $CKAN_DATABASE $DATASTORE_DATABASE $CKAN_USER $CKAN_USER $DATASTORE_USER -p postgres && \
    rm /tmp/datastore_setup.py && \
    rm /tmp/set_permissions.sql && \
    rm /tmp/tethys_deploy.conf

# Modify config files --------------------------------------------------------#
# Allow remote connections to the database
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf

# Listen to all addresses
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

# Jetty
RUN sed 's/NO_START=1/NO_START=0/g' -i /etc/default/jetty && \
    sed "s=#JAVA_HOME\==JAVA_HOME\=$JAVA_HOME=g" -i /etc/default/jetty && \
    sed "s/#JETTY_HOST.*/JETTY_HOST=0.0.0.0/g" -i /etc/default/jetty

# Modification to fix bug with jetty
# see: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=637961
RUN sed 's=\^\[\:space\:\]=\^\[\[\:space\:\]\]=g' -i /etc/init.d/jetty

# Setup supervisor -----------------------------------------------------------#
RUN mkdir -p /var/log/supervisor
RUN locale-gen en_US en_US.UTF-8

# Add the CKAN schema.xml file -----------------------------------------------#
RUN mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml_bak
ADD schema.xml /etc/solr/conf/

# Home dirs
ENV CKAN_HOME /usr/lib/ckan
ENV CKANEXT $CKAN_HOME/default/src/ckan/ckanext
ENV CKANAPP $CKANEXT/tethys_apps/ckanapp
ENV VENV_HOME /usr/lib/ckan/default
ENV VENV_ACTIVATE /usr/lib/ckan/default/bin/activate

# Configuration files
ENV CKAN_INI /etc/ckan/default/production.ini
ENV TETHYS_INI /usr/lib/ckan/default/src/ckan/ckanext/tethys_apps/tethys_apps.ini

# Create virtual environment -------------------------------------------------#
RUN mkdir -p $VENV_HOME; \
    chown `whoami` $VENV_HOME; \
    virtualenv --no-site-packages /usr/lib/ckan/default

# Install CKAN 2.2 from source -----------------------------------------------#
RUN . $VENV_ACTIVATE && \
    pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.2#egg=ckan' && \
    pip install -r /usr/lib/ckan/default/src/ckan/requirements.txt && \
    deactivate

# Get Tethys plugin source ---------------------------------------------------#
RUN git clone https://swainn@bitbucket.org/swainn/ckanext-ciwater_theme.git $TETHYS_DEV_HOME/ckanext-ciwater_theme

# Install plugins into virtual environment -----------------------------------#
RUN . $VENV_ACTIVATE && \
    cd $TETHYS_DEV_HOME/ckanext-ciwater_theme && \
    python setup.py install && \
    deactivate
 
# Symbolically link the plugins ----------------------------------------------#
RUN cp -R $TETHYS_DEV_HOME/ckanext-ciwater_theme/ckanext/ciwater_theme $CKANEXT/

# Create config and edit -----------------------------------------------------#
RUN mkdir -p /etc/ckan/default && \
    chown -R `whoami` /etc/ckan/ && \
    . $VENV_ACTIVATE && cd $VENV_HOME/src/ckan && \
    paster make-config ckan $CKAN_INI && \
    deactivate

# Add config file ------------------------------------------------------------#
ADD tethys_deploy.conf /tmp/

# CKAN INI
RUN SERVER_ADDRESS=$(grep -Po "(?<=^SERVER_ADDRESS ).*" /tmp/tethys_deploy.conf) && \
    EXTRA_RESOURCE_FIELDS="ckan.extra_resource_fields = model" && \
    PLUGINS="ckan.plugins = stats text_preview recline_preview pdf_preview ciwater_theme" && \
    sed "s/ckan.site_url.*/ckan.site_url = http:\/\/SERVER_ADDRESS/g" -i $CKAN_INI && \
    sed "s/#ckan.storage_path.*/ckan.storage_path = \/var\/lib\/ckan\/default/g" -i $CKAN_INI && \
    sed "s/ckan.plugins =.*/$PLUGINS\n$EXTRA_RESOURCE_FIELDS/g" -i $CKAN_INI

# Link who.ini
RUN ln -sf $CKAN_HOME/default/src/ckan/who.ini /etc/ckan/default/who.ini

# Create filestore directory -------------------------------------------------#
RUN mkdir -p /var/lib/ckan/default

# Create a directory for scripts ---------------------------------------------#
RUN mkdir /usr/lib/ckan/scripts

# Add scripts
ADD scripts/startup.sh /usr/lib/ckan/scripts/
ADD scripts/install_apps.sh /usr/lib/ckan/scripts/

# Set permissions for scripts
RUN chmod -R 755 /usr/lib/ckan/scripts

# Add server scripts
ADD apache/apache.wsgi /etc/ckan/default/
ADD apache/ckan_default /etc/apache2/sites-available/
ADD nginx/ckan_default /etc/nginx/sites-available/

# Apply server name to apache config
RUN SERVER_ADDRESS=$(grep -Po "(?<=^SERVER_ADDRESS ).*" /tmp/tethys_deploy.conf) && \
    sed "s/    ServerName 127.0.0.1/    ServerName $SERVER_ADDRESS/g" -i /etc/apache2/sites-available/ckan_default && \
    sed "s/    ServerAlias 127.0.0.1/    ServerAlias $SERVER_ADDRESS/g" -i /etc/apache2/sites-available/ckan_default

# Add the supervisor conf file to appropriate place --------------------------#
ADD supervisord.conf /etc/supervisor/conf.d/

# Modify listening ports for apache
RUN sed "s/NameVirtualHost \*:80/#NameVirtualHost *:8080/g" -i /etc/apache2/ports.conf && \
    sed "s/Listen 80/Listen 8080/g" -i /etc/apache2/ports.conf && \
    echo "ServerName localhost" | sudo tee /etc/apache2/conf.d/fqdn && \
    echo "*               soft    nofile          8192" >> /etc/security/limits.conf && \
    echo "*               hard    nofile          8192" >> /etc/security/limits.conf && \
    echo "root            soft    nofile          8192" >> /etc/security/limits.conf && \
    echo "root            hard    nofile          8192" >> /etc/security/limits.conf

# Configure apache2 and nginx ------------------------------------------------#
RUN service nginx stop && \
    service apache2 stop

# Enable and disable appropriate sites
RUN a2dissite default && \
    a2ensite ckan_default && \
    ln -s /etc/nginx/sites-available/ckan_default /etc/nginx/sites-enabled/ckan_default

# Handle Apache Permissions
RUN chmod 644 /etc/ckan/default/apache.wsgi

# Change the working directory
WORKDIR /usr/lib/ckan/scripts

# Add VOLUMEs to for inspection, datastorage, and backup ---------------------#
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/var/lib/ckan/default", "/etc/solr/conf", "/var/log/supervisor"]

EXPOSE 80 5432

CMD ["/usr/lib/ckan/scripts/startup.sh"]


