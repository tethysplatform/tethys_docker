"""
********************************************************************************
* Name: gen_supervisord
* Author: nswain
* Created On: March 17, 2016
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


if '__main__' in __name__:
    max_nodes = int(os.environ.get('MAX_NODES', '4'))
    geoserver_home = os.environ.get('GEOSERVER_HOME', '/')
    supervisord_config = os.path.join(geoserver_home, 'supervisord.conf')

    nodes = [i for i in range(1, max_nodes + 1)]

    sys.stdout.write("\nConfiguring supervisord for geoserver {0} nodes.\n".format(max_nodes))

    template_directory = os.path.dirname(__file__)
    file_contents = render_from_template(template_directory, 'template_supervisord.conf', nodes=nodes)

    with open(supervisord_config, 'w') as f:
        f.write(file_contents)

    sys.stdout.write("Successfully configured supervisord for {0} nodes.\n\n".format(max_nodes))
