# CKAN Development Environment for Tethys
# CKAN 2.2
# Ubuntu 12.04 LTS
# PostgreSQL 9.3
# PostGIS 2.1
#
# Credits: Based on same developed by Department of Parks and Wildlife <asi@dpaw.wa.gov.au>
#
# VERSION 1.0

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
ENV PGDATABASE ckan_default
ENV PGUSER ckan_default
ENV PGPASS pass

# Datastore db and user
ENV DSDATABASE datastore_default
ENV DSUSER datastore_default
ENV DSPASS pass

# Home dirs
ENV CKAN_HOME /usr/lib/ckan
ENV VENV_HOME /usr/lib/ckan/default
ENV VENV_ACTIVATE /usr/lib/ckan/default/bin/activate
ENV CKAN_INI /etc/ckan/default/development.ini

# Create virtual environment -------------------------------------------------#
RUN mkdir -p $VENV_HOME; \
    chown `whoami` $VENV_HOME; \
    virtualenv --no-site-packages /usr/lib/ckan/default

# Install CKAN 2.2 from source -----------------------------------------------#
RUN . $VENV_ACTIVATE && \
    pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.2#egg=ckan' && \
    pip install -r /usr/lib/ckan/default/src/ckan/requirements.txt && \
    deactivate

# Create config and edit -----------------------------------------------------#
RUN mkdir -p /etc/ckan/default && \
    chown -R `whoami` /etc/ckan/ && \
    . $VENV_ACTIVATE && cd $VENV_HOME/src/ckan && \
    paster make-config ckan $CKAN_INI && \
    deactivate

# CKAN INI
RUN sed "s/#ckan.storage_path.*/ckan.storage_path = \/var\/lib\/ckan\/default/g" -i $CKAN_INI && \
    sed "s/ckan.plugins =.*/ckan.plugins = stats text_preview recline_preview pdf_preview/g" -i $CKAN_INI && \
    sed "s/debug =.*/debug = true/g" -i $CKAN_INI

# Link who.ini
RUN ln -sf $CKAN_HOME/default/src/ckan/who.ini /etc/ckan/default/who.ini

# Make main.debug.css available for debugging --------------------------------#
RUN cp $CKAN_HOME/default/src/ckan/ckan/public/base/css/main.debug.min.css $CKAN_HOME/default/src/ckan/ckan/public/base/css/main.debug.css

# Create datastore directory -------------------------------------------------#
RUN mkdir -p /var/lib/ckan/default && \
    chown www-data /var/lib/ckan/default && \
    chmod u+rwx /var/lib/ckan/default
 
# Add startup script  
ADD startup.sh /usr/lib/ckan/

EXPOSE 5000

CMD ["bash", "/usr/lib/ckan/startup.sh"]

























