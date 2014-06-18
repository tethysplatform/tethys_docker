# Development Environment for Tethys
# CKAN 2.2
# Ubuntu 12.04 LTS
# PostgreSQL 9.3
# PostGIS 2.1
#
# VERSION 1.0.0

FROM ubuntu:12.04

MAINTAINER Nathan Swain nathan.swain@byu.net

# Apt setup ------------------------------------------------------------------#
RUN apt-get update
RUN apt-get install -y wget sudo curl ssh vim

# Install CKAN dependencies --------------------------------------------------#
RUN apt-get install -y python-dev python-pip python-virtualenv git-core

# Drivers for PostgreSQL -----------------------------------------------------#
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --force-yes libpq-dev

# Environment variables ------------------------------------------------------#
ENV PGVERSION 9.3

# CKAN db and user
ENV CKAN_DATABASE ckan_default
ENV CKAN_USER ckan_default
ENV CKAN_PASS pass

# Datastore db and user
ENV DATASTORE_DATABASE datastore_default
ENV DATASTORE_USER datastore_default
ENV DATASTORE_PASS pass

# Tethys super db and user
ENV TETHYS_SUPER_DATABASE tethys_super
ENV TETHYS_SUPER_USER tethys_super
ENV TETHYS_SUPER_PASS pass

# Tethys app database manager
ENV APPS_MANAGER_DATABASE tethys_db_manager
ENV APPS_MANAGER_USER tethys_db_manager
ENV APPS_MANAGER_PASS pass

# Home dirs
ENV CKAN_HOME /usr/lib/ckan
ENV TETHYS_DEV_HOME $CKAN_HOME/tethys_dev
ENV APPS_PROJECTS_DEV $CKAN_HOME/apps_projects
ENV CKANEXT $CKAN_HOME/default/src/ckan/ckanext
ENV CKANAPP $CKANEXT/tethys_apps/ckanapp
ENV VENV_HOME /usr/lib/ckan/default
ENV VENV_ACTIVATE /usr/lib/ckan/default/bin/activate

# Configuration files
ENV CKAN_INI /etc/ckan/default/development.ini
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
    
# Make Tethys dev directories ------------------------------------------------#
RUN mkdir -p $TETHYS_DEV_HOME
RUN mkdir -p $APPS_PROJECTS_DEV

# Get Tethys plugin source ---------------------------------------------------#
RUN git clone https://swainn@bitbucket.org/swainn/ckanext-tethys_apps.git $TETHYS_DEV_HOME/ckanext-tethys_apps
RUN git clone https://swainn@bitbucket.org/swainn/ckanext-ciwater_theme.git $TETHYS_DEV_HOME/ckanext-ciwater_theme

# Install plugins into virtual environment -----------------------------------#
RUN . $VENV_ACTIVATE && \
	cd $TETHYS_DEV_HOME/ckanext-tethys_apps && \
    python setup.py develop && \
    cd $TETHYS_DEV_HOME/ckanext-ciwater_theme && \
    python setup.py develop && \
    deactivate
 
# Symbolically link the plugins ----------------------------------------------#
RUN ln -s $TETHYS_DEV_HOME/ckanext-tethys_apps/ckanext/tethys_apps $CKANEXT/tethys_apps && \
    ln -s $TETHYS_DEV_HOME/ckanext-ciwater_theme/ckanext/ciwater_theme $CKANEXT/ciwater_theme

# Create config and edit -----------------------------------------------------#
RUN mkdir -p /etc/ckan/default && \
    chown -R `whoami` /etc/ckan/ && \
    . $VENV_ACTIVATE && cd $VENV_HOME/src/ckan && \
    paster make-config ckan $CKAN_INI && \
    deactivate

# CKAN INI
RUN sed "s/#ckan.storage_path.*/ckan.storage_path = \/var\/lib\/ckan\/default/g" -i $CKAN_INI && \
    sed "s/ckan.plugins =.*/ckan.plugins = stats text_preview recline_preview pdf_preview tethys_apps ciwater_theme/g" -i $CKAN_INI && \
    sed "s/debug =.*/debug = true/g" -i $CKAN_INI

# Link who.ini
RUN ln -sf $CKAN_HOME/default/src/ckan/who.ini /etc/ckan/default/who.ini

# Make main.debug.css available for debugging --------------------------------#
RUN cp $CKAN_HOME/default/src/ckan/ckan/public/base/css/main.debug.min.css $CKAN_HOME/default/src/ckan/ckan/public/base/css/main.debug.css

# Create datastore directory -------------------------------------------------#
RUN mkdir -p /var/lib/ckan/default && \
    chown www-data /var/lib/ckan/default && \
    chmod u+rwx /var/lib/ckan/default

# Create a directory for scripts ---------------------------------------------#
RUN mkdir /usr/lib/ckan/scripts

# Add startup script  
ADD scripts/startup.sh /usr/lib/ckan/scripts/
ADD scripts/createapp /usr/lib/ckan/scripts/
ADD scripts/develop_apps.sh /usr/lib/ckan/scripts/

# Create user
RUN adduser tethys

# Handle permissions
RUN chmod -R 755 /usr/lib/ckan/scripts
RUN chown -R tethys /usr/lib/ckan/scripts

# Change the working directory
WORKDIR /usr/lib/ckan/scripts

EXPOSE 5000

CMD ["bash", "/usr/lib/ckan/scripts/startup.sh"]


