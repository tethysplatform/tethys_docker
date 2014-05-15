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

# Add instruction in startup.sh to add_apps.py script ------------------------#
RUN sed -i '1i python $APPS_PROJECTS_DEV/link_apps.py $CKANAPP' /usr/lib/ckan/startup.sh

# Add the link_apps python script
ADD link_apps.py $APPS_PROJECTS_DEV/





