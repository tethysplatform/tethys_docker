import os, sys

print "LINKING APPS"

# Get args or print help
if (len(sys.argv) < 2):
    sys.exit("USAGE: python link_apps.py [/path/to/ckanapp]")
    
CKANAPP_HOME = sys.argv[1]

if not os.path.isdir(CKANAPP_HOME):
    sys.exit("LINK APPS ERROR:", CKANAPP_HOME, "is not a directory")
    
app_projects_directory = os.path.abspath(os.path.dirname(__file__))
project_links = dict()

# Find projects to link
for app_project_thing in os.listdir(app_projects_directory):
    directory_path = os.path.join(app_projects_directory, app_project_thing)
    
    # Must be a valid ckanapp package
    if ('ckanapp' in app_project_thing and os.path.isdir(directory_path)):
        ckanapp_directory = os.path.join(directory_path, 'ckanapp')
        app_source_directory = ''
        
        try:
            # Find the source directory that needs to be linked
            for ckanapp_thing in os.listdir(ckanapp_directory):
                thing_path = os.path.join(ckanapp_directory, ckanapp_thing)
                
                # Must be a directory and not __init__ file
                if (os.path.isdir(thing_path) and not '__init__' in ckanapp_thing):
                    project_links[ckanapp_thing] = thing_path
                    break
        except:
            pass

for project, source_directory in project_links.iteritems():    
    try:
        source_link = os.path.join(CKANAPP_HOME, project)
        os.symlink(source_directory, source_link)
        print "TETHYS APPS: Creating symbolic link to", project
    except:
        pass
    