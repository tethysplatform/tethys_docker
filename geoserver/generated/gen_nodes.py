"""
********************************************************************************
* Name: gen_unique_files.py
* Author: nswain
* Created On: March 16, 2016
* Copyright: (c) Aquaveo 2016
* License: 
********************************************************************************
"""
import os
import sys
import shutil
from jinja2 import FileSystemLoader, Environment


def render_from_template(directory, template_name, **kwargs):
    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    template = env.get_template(template_name)
    return template.render(**kwargs)


if '__main__' in __name__:
    max_nodes = int(os.environ.get('MAX_NODES', '4'))
    data_dir = os.environ.get('GEOSERVER_DATA_DIR', '/')
    geoserver_home = os.environ.get('GEOSERVER_HOME', '/')
    template_node_dir = os.path.join(geoserver_home, 'node')

    default_shutdown_port = 8005
    default_http_port = 8080
    default_redirect_port = 8443
    default_ajp_port = 8009 + 100

    sys.stdout.write('\nCreating GeoServer Instances...\n')
    sys.stdout.write('MAX_NODES: {0}\n'.format(max_nodes))
    sys.stdout.write('GEOSERVER_DATA_DIR: {0}\n'.format(data_dir))
    sys.stdout.write('GEOSERVER_HOME: {0}\n\n'.format(geoserver_home))

    for node_id in range(1, max_nodes + 1):
        node_dir = os.path.join(geoserver_home, 'node{0}'.format(node_id))
        sys.stdout.write('Creating GeoServer instance {0} at location {1}.\n'.format(node_id, node_dir))

        shutil.copytree(template_node_dir, node_dir)

        # catalina.sh
        context = {
            'node_id': node_id,
        }

        template_directory = os.path.dirname(__file__)
        file_contents = render_from_template(template_directory, 'template_catalina.sh', **context)
        catalina_sh = os.path.join(node_dir, 'catalina.sh')

        with open(catalina_sh, 'w') as f:
            f.write(file_contents)

        os.chmod(catalina_sh, 555)

        sys.stdout.write('Successfully created catalina.sh for instance {0}.\n'.format(node_id))

        # server.xml
        context = {
            'shutdown_port': default_shutdown_port + node_id,
            'http_port': default_http_port + node_id,
            'redirect_port': default_redirect_port + node_id,
            'ajp_port': default_ajp_port + node_id,
        }

        file_contents = render_from_template(template_directory, 'template_server.xml', **context)

        with open(os.path.join(node_dir, 'conf', 'server.xml'), 'w') as f:
            f.write(file_contents)

        sys.stdout.write('Successfully created server.xml for instance {0} with ports:\n'.format(node_id))
        sys.stdout.write('    HTTP Port: {0}\n'.format(default_http_port + node_id))
        sys.stdout.write('    Redirect Port: {0}\n'.format(default_redirect_port + node_id))
        sys.stdout.write('    Shutdown Port: {0}\n'.format(default_shutdown_port + node_id))
        sys.stdout.write('    AJP Port: {0}\n'.format(default_ajp_port + node_id))

        # web.xml
        context = {
            'data_dir': data_dir,
            'node_id': node_id
        }

        file_contents = render_from_template(template_directory, 'template_web.xml', **context)

        with open(os.path.join(node_dir, 'webapps', 'geoserver', 'WEB-INF', 'web.xml'), 'w') as f:
            f.write(file_contents)

        sys.stdout.write('Successfully created web.xml for instance {0}.\n'.format(node_id))
        sys.stdout.write('Successfully created GeoServer instance {0}.\n\n'.format(node_id))
