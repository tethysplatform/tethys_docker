#!/bin/bash
# Notify
echo "Installing Apps..."

# Activate virtual environment
. $VENV_ACTIVATE

# Loop through diretories in APPS_PROJECTS_DEV
for directory in $APPS_PROJECTS_DEV/*/ ; do

    # Check for appropriately named directories (only "ckanapp-" prefix)
    if [[ "$directory" != ckanapp-* ]]
    then
        # Run the installation script
        cd "$directory"
        python setup.py develop

        # Toggle virtualenv activation
        deactivate
        . $VENV_ACTIVATE
    fi

done