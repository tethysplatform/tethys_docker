# CI Water Dockerfile
# CKAN Extensions:
# tethys_apps
# ciwater_theme
#
# VERSION 1.0

FROM swainn/ckan_base:dev

MAINTAINER Nathan Swain nathan.swain@byu.net

# Variables ------------------------------------------------------------------#
ENV TETHYS_DEV_HOME $CKAN_HOME/tethys_dev
ENV APPS_PROJECTS_DEV $CKAN_HOME/apps_projects
ENV CKANEXT $CKAN_HOME/default/src/ckan/ckanext
ENV CKANAPP $CKANEXT/tethys_apps/ckanapp
ENV TETHYS_INI /usr/lib/ckan/default/src/ckan/ckanext/tethys_apps/tethys_apps.ini

ENV APP_MANAGER_DATABASE tethys_db_manager
ENV APP_MANAGER_USER tethys_db_manager
ENV APP_MANAGER_PASS pass

# Make dev directory ---------------------------------------------------------#
RUN mkdir -p $TETHYS_DEV_HOME
RUN mkdir -p $APPS_PROJECTS_DEV

# Get plugin source ----------------------------------------------------------#
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

# Update configuration file --------------------------------------------------#
RUN sed "s/ckan.plugins =.*/ckan.plugins = stats text_preview recline_preview pdf_preview tethys_apps ciwater_theme/g" -i $CKAN_INI

# Add instruction to startup.sh that will modify the tethys apps config
RUN sed -i '1i sed "s/tethys.database_manager_url =.*/tethys.database_manager_url = postgresql:\\\/\\\/$APP_MANAGER_USER:$APP_MANAGER_PASS@$DATA_PORT_5432_TCP_ADDR:$DATA_PORT_5432_TCP_PORT\\\/$APP_MANAGER_DATABASE/g" -i $TETHYS_INI' /usr/lib/ckan/startup.sh

# Add instruction in startup.sh to add_apps.py script ------------------------#
RUN sed -i '1i python $APPS_PROJECTS_DEV/link_apps.py $CKANAPP' /usr/lib/ckan/startup.sh

# Add the link_apps python script
ADD link_apps.py $APPS_PROJECTS_DEV/
ADD createapp /usr/lib/ckan/

# Handle permissions
RUN chmod 755 /usr/lib/ckan/createapp

# Change the working directory
WORKDIR /usr/lib/ckan/





