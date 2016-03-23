"""
********************************************************************************
* Name: startup.py
* Author: nswain
* Created On: March 22, 2016
* Copyright: (c) Aquaveo 2016
* License:
********************************************************************************
"""
import os
import sys
from jinja2 import FileSystemLoader, Environment


def render_from_template(directory, template_name, **kwargs):
    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    template = env.get_template(template_name)
    return template.render(**kwargs)


def render_and_write_to_file(context, template, filename):
    template_directory = os.path.dirname(__file__)
    file_contents = render_from_template(template_directory, template, **context)
    with open(filename, 'w') as f:
        f.write(file_contents)


def gen_startup_sh(enabled_nodes, geoserver_home):
    startup_sh = os.path.join(geoserver_home, 'geoserver_startup.sh')
    context = {'nodes': [i for i in range(1, enabled_nodes + 1)]}
    sys.stdout.write("\nCreating startup.sh for {0} nodes.\n".format(enabled_nodes))
    render_and_write_to_file(context=context, template='template_geoserver_startup.sh', filename=startup_sh)
    os.chmod(startup_sh, 0555)
    sys.stdout.write("Successfully created startup.sh for {0} nodes.\n\n".format(enabled_nodes))


if '__main__' in __name__:
    MAX_NODES = int(os.environ.get('MAX_NODES', '4'))
    NODES_ENABLED = int(os.environ.get('NODES_ENABLED', '2'))
    GEOSERVER_HOME = os.environ.get('GEOSERVER_HOME', '/')
    GEOSERVER_DATA_DIR = os.environ.get('GEOSERVER_DATA_DIR', '/')

    if NODES_ENABLED <= 1:
        nodes_to_enable = 1
    elif NODES_ENABLED <= MAX_NODES:
        nodes_to_enable = NODES_ENABLED
    else:
        nodes_to_enable = MAX_NODES

    # Create startup_geoserver.sh
    gen_startup_sh(enabled_nodes=nodes_to_enable, geoserver_home=GEOSERVER_HOME)

