import os, sys, subprocess

# Get args or print help
if (len(sys.argv) != 2):
    sys.exit("Usage: python link_apps.py [apps_projects_path]")
    
print "Installing Apps..."

APPS_PROJECTS = sys.argv[1]

# Validate path
if not os.path.isdir(APPS_PROJECTS):
    sys.exit("App Installation Error:", APPS_PROJECTS, "is not a directory")
    
project_dirs = []

# Find projects to link
for app_project_thing in os.listdir(APPS_PROJECTS):
    directory_path = os.path.join(APPS_PROJECTS, app_project_thing)
    
    # Must be a valid ckanapp package
    if ('ckanapp' in app_project_thing and os.path.isdir(directory_path)):
        setup_script = os.path.join(directory_path, 'setup.py')
        
        # Make sure the file exists
        if (os.path.isfile(setup_script)):
            project_dirs.append(directory_path)
            
# Run setup script for all apps
for project_dir in project_dirs:
    os.chdir(project_dir)
    subprocess.call(['python', 'setup.py', 'develop'])
    print project_dir