# CKAN Docker
# CKAN 2.2

FROM ubuntu:12.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup ------------------------------------------------------------------#
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y wget sudo curl ssh vim

# Install CKAN dependencies --------------------------------------------------#
RUN apt-get install -y python-dev python-pip python-virtualenv git-core

# Install Production Servers -------------------------------------------------#
RUN apt-get install -y \
    apache2 libapache2-mod-wsgi libapache2-mod-rpaf \
    nginx \
    postfix \
    openjdk-6-jdk solr-jetty \
    supervisor

# Home directories
ENV JAVA_HOME /usr/lib/jvm/java-6-openjdk-amd64/

# Install PostgreSQL libraries ----------------------------------------------------------------------------------------#
RUN apt-get install -y postgresql-9.1 postgresql-client-9.1 postgresql-contrib-9.1 libpq-dev postgresql-server-dev-9.1
RUN apt-get -y -q install python-software-properties software-properties-common sudo

# Add some temporary scripts -------------------------------------------------#
ADD tethys_deploy.conf /tmp/
ADD datastore/datastore_setup.py /tmp/
ADD datastore/set_permissions.sql /tmp/

# Variables ------------------------------------------------------------------#
ENV PGVERSION 9.1
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
    sudo -u postgres psql -c "CREATE USER $DATASTORE_USER PASSWORD '$DATASTORE_PASS';" && \
    sudo -u postgres createdb $DATASTORE_DATABASE -E utf8 -T template0 -O $DATASTORE_USER && \
    python datastore_setup.py $CKAN_DATABASE $DATASTORE_DATABASE $CKAN_USER $CKAN_USER $DATASTORE_USER -p postgres && \
    rm /tmp/datastore_setup.py && \
    rm /tmp/set_permissions.sql

# Modify config files --------------------------------------------------------#
# Allow remote connections to the database
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.1/main/pg_hba.conf

# Listen to all addresses
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.1/main/postgresql.conf

# Jetty
RUN sed 's/NO_START=1/NO_START=0/g' -i /etc/default/jetty && \
    sed "s=#JAVA_HOME\==JAVA_HOME\=$JAVA_HOME=g" -i /etc/default/jetty && \
    sed "s/#JETTY_HOST.*/JETTY_HOST=0.0.0.0/g" -i /etc/default/jetty && \
    sed "s/#JETTY_PORT.*/JETTY_PORT=8983/g" -i /etc/default/jetty

# Modification to fix bug with jetty
# see: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=637961
RUN sed 's=\^\[\:space\:\]=\^\[\[\:space\:\]\]=g' -i /etc/init.d/jetty

# Setup supervisor -----------------------------------------------------------#
RUN mkdir -p /var/log/supervisor
RUN locale-gen en_US en_US.UTF-8

# Add the CKAN schema.xml file -----------------------------------------------#
RUN mv /etc/solr/conf/schema.xml /etc/solr/conf/schema.xml_bak
COPY schema.xml /etc/solr/conf/schema.xml

# Home dirs
ENV CKAN_HOME /usr/lib/ckan
ENV TETHYS_DEV_HOME $CKAN_HOME/tethys_dev
ENV CKANEXT $CKAN_HOME/default/src/ckan/ckanext
ENV VENV_HOME /usr/lib/ckan/default
ENV VENV_ACTIVATE /usr/lib/ckan/default/bin/activate

# Make Tethys dev directories ------------------------------------------------#
RUN mkdir -p $TETHYS_DEV_HOME

# Configuration files
ENV CKAN_INI /etc/ckan/default/production.ini

# Create virtual environment -------------------------------------------------#
RUN mkdir -p $VENV_HOME; \
    chown `whoami` $VENV_HOME; \
    virtualenv --no-site-packages /usr/lib/ckan/default

# Install CKAN 2.2 from source -----------------------------------------------#
RUN . $VENV_ACTIVATE && \
    pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.2.1#egg=ckan' && \
    pip install -r /usr/lib/ckan/default/src/ckan/requirements.txt && \
    deactivate

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
    PLUGINS="ckan.plugins = stats text_preview recline_preview pdf_preview" && \
    CKAN_DATABASE=$(grep -Po "(?<=^CKAN_DATABASE ).*" /tmp/tethys_deploy.conf) && \
    CKAN_USER=$(grep -Po "(?<=^CKAN_USER ).*" /tmp/tethys_deploy.conf) && \
    CKAN_PASS=$(grep -Po "(?<=^CKAN_PASS ).*" /tmp/tethys_deploy.conf) && \
    DATASTORE_DATABASE=$(grep -Po "(?<=^DATASTORE_DATABASE ).*" /tmp/tethys_deploy.conf) && \
    DATASTORE_USER=$(grep -Po "(?<=^DATASTORE_USER ).*" /tmp/tethys_deploy.conf) && \
    DATASTORE_PASS=$(grep -Po "(?<=^DATASTORE_PASS ).*" /tmp/tethys_deploy.conf) && \
    sed "s/ckan.site_url.*/ckan.site_url = http:\/\/SERVER_ADDRESS/g" -i $CKAN_INI && \
    sed "s/#ckan.storage_path.*/ckan.storage_path = \/var\/lib\/ckan\/default/g" -i $CKAN_INI && \
    sed "s/ckan.plugins =.*/$PLUGINS\n$EXTRA_RESOURCE_FIELDS/g" -i $CKAN_INI && \
    sed "s/#solr_url.*/solr_url = http:\/\/127.0.0.1:8983\/solr/g" -i $CKAN_INI && \
    sed "s/sqlalchemy.url.*/sqlalchemy.url = postgresql:\/\/$CKAN_USER:$CKAN_PASS@127.0.0.1:5432\/$CKAN_DATABASE/g" -i $CKAN_INI && \
    sed "s/#ckan.datastore.write_url.*/ckan.datastore.write_url = postgresql:\/\/$CKAN_USER:$CKAN_PASS@127.0.0.1:5432\/$DATASTORE_DATABASE/g" -i $CKAN_INI && \
    sed "s/#ckan.datastore.read_url.*/ckan.datastore.read_url = postgresql:\/\/$DATASTORE_USER:$DATASTORE_PASS@127.0.0.1:5432\/$DATASTORE_DATABASE/g" -i $CKAN_INI

# Init CKAN Databases
RUN /etc/init.d/postgresql start && \
    . $VENV_ACTIVATE && \
    cd $VENV_HOME/src/ckan && \
    paster db init -c $CKAN_INI

# Link who.ini
RUN ln -sf $CKAN_HOME/default/src/ckan/who.ini /etc/ckan/default/who.ini

# Create filestore directory -------------------------------------------------#
RUN mkdir -p /var/lib/ckan/default

# Create a directory for scripts ---------------------------------------------#
RUN mkdir /usr/lib/ckan/scripts

# Add scripts
COPY scripts/startup.sh /usr/lib/ckan/scripts/startup.sh
RUN chmod -R 755 /usr/lib/ckan/scripts

# Add server scripts
COPY apache/apache.wsgi /etc/ckan/default/apache.wsgi
COPY apache/ckan_default /etc/apache2/sites-available/ckan_default
COPY nginx/ckan_default /etc/nginx/sites-available/ckan_default

# Apply server name to apache config
RUN SERVER_ADDRESS=$(grep -Po "(?<=^SERVER_ADDRESS ).*" /tmp/tethys_deploy.conf) && \
    sed "s/    ServerName 127.0.0.1/    ServerName $SERVER_ADDRESS/g" -i /etc/apache2/sites-available/ckan_default && \
    sed "s/    ServerAlias 127.0.0.1/    ServerAlias $SERVER_ADDRESS/g" -i /etc/apache2/sites-available/ckan_default && \
    rm /tmp/tethys_deploy.conf

# Add the supervisor conf file to appropriate place --------------------------#
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

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
    ln -s /etc/nginx/sites-available/ckan_default /etc/nginx/sites-enabled/ckan_default && \
    /etc/init.d/apache2 reload && \
    /etc/init.d/nginx reload

# Handle Apache Permissions
RUN chmod 644 /etc/ckan/default/apache.wsgi

# Other permissions
RUN chown www-data:www-data /var/lib/ckan/default && \
    chmod u+rwx /var/lib/ckan/default && \
    chown -R www-data:www-data /usr/lib/ckan/default/

# Change the working directory
WORKDIR /usr/lib/ckan/scripts

# Add VOLUMEs to for inspection, datastorage, and backup ---------------------#
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/var/lib/ckan/default", "/etc/solr/conf", "/var/log/supervisor"]

EXPOSE 80 5432 5000 8983

CMD ["/usr/lib/ckan/scripts/startup.sh"]


