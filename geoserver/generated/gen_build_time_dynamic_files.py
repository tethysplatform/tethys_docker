"""
********************************************************************************
* Name: gen_dynamic_files.py
* Author: nswain
* Created On: March 22, 2016
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


def render_and_write_to_file(context, template, filename):
    template_directory = os.path.dirname(__file__)
    file_contents = render_from_template(template_directory, template, **context)
    with open(filename, 'w') as f:
        f.write(file_contents)


def gen_nodes(max_nodes, data_dir, geoserver_home, default_shutdown_port, default_http_port,
              default_redirect_port, default_ajp_port):
    template_node_dir = os.path.join(geoserver_home, 'node')

    sys.stdout.write('\nCreating GeoServer Instances...\n')
    sys.stdout.write('MAX_NODES: {0}\n'.format(max_nodes))
    sys.stdout.write('GEOSERVER_DATA_DIR: {0}\n'.format(data_dir))
    sys.stdout.write('GEOSERVER_HOME: {0}\n\n'.format(geoserver_home))

    for node_id in range(1, max_nodes + 1):
        node_dir = os.path.join(geoserver_home, 'node{0}'.format(node_id))
        sys.stdout.write('Creating GeoServer instance {0} at location {1}.\n'.format(node_id, node_dir))

        shutil.copytree(template_node_dir, node_dir)

        context = {
            'node_id': node_id,
            'child_node': (node_id != 1)
        }

        # catalina.sh
        catalina_sh = os.path.join(node_dir, 'catalina.sh')
        render_and_write_to_file(context=context, template='template_catalina.sh', filename=catalina_sh)
        os.chmod(catalina_sh, 0555)
        sys.stdout.write('Successfully created catalina.sh for instance {0}.\n'.format(node_id))

        # server.xml
        context = {
            'shutdown_port': default_shutdown_port + node_id,
            'http_port': default_http_port + node_id,
            'redirect_port': default_redirect_port + node_id,
            'ajp_port': default_ajp_port + node_id,
        }

        server_xml = os.path.join(node_dir, 'conf', 'server.xml')
        render_and_write_to_file(context=context, template='template_server.xml', filename=server_xml)
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

        web_xml = os.path.join(node_dir, 'webapps', 'geoserver', 'WEB-INF', 'web.xml')
        render_and_write_to_file(context=context, template='template_web.xml', filename=web_xml)
        sys.stdout.write('Successfully created web.xml for instance {0}.\n'.format(node_id))
        sys.stdout.write('Successfully created GeoServer instance {0}.\n\n'.format(node_id))


if '__main__' in __name__:
    MAX_NODES = int(os.environ.get('MAX_NODES', '4'))
    GEOSERVER_HOME = os.environ.get('GEOSERVER_HOME', '/')
    GEOSERVER_DATA_DIR = os.environ.get('GEOSERVER_DATA_DIR', '/')
    NODES_ENABLED = int(os.environ.get('NODES_ENABLED', '2'))

    DEFAULT_SHUTDOWN_PORT = 8005
    DEFAULT_HTTP_PORT = 8080
    DEFAULT_REDIRECT_PORT = 8443
    DEFAULT_AJP_PORT = 8009 + 100

    gen_nodes(max_nodes=MAX_NODES, data_dir=GEOSERVER_DATA_DIR, geoserver_home=GEOSERVER_HOME,
              default_http_port=DEFAULT_HTTP_PORT, default_ajp_port=DEFAULT_AJP_PORT,
              default_redirect_port=DEFAULT_REDIRECT_PORT, default_shutdown_port=DEFAULT_SHUTDOWN_PORT)




