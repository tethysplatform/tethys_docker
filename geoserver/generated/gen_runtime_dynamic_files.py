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


def gen_supervisord(enabled_nodes, supervisor_config):
    context = {'nodes': [i for i in range(1, enabled_nodes + 1)]}
    sys.stdout.write("\nConfiguring supervisord for {0} nodes.\n".format(enabled_nodes))
    render_and_write_to_file(context=context, template='template_supervisord.conf', filename=supervisor_config)
    sys.stdout.write("Successfully configured supervisord for {0} nodes.\n\n".format(enabled_nodes))


def gen_nginx(max_nodes, default_http_port):
    """
    Generate the NGINX configuration file, such that it load balances the clustered GeoServers.
    """
    nginx_config = '/etc/nginx/sites-available/default'
    http_ports = []

    for node_id in range(1, max_nodes + 1):
        http_port = default_http_port + node_id
        http_ports.append(str(http_port))

    context = {'http_ports': http_ports}

    sys.stdout.write("\nConfiguring NGINX load balancer for the following ports: {0}\n".format(', '.join(http_ports)))
    render_and_write_to_file(context=context, template='template_nginx_config', filename=nginx_config)
    sys.stdout.write("Successfully generated NGINX load balancer config.\n\n")


if '__main__' in __name__:
    MAX_NODES = int(os.environ.get('MAX_NODES', '4'))
    NODES_ENABLED = int(os.environ.get('NODES_ENABLED', '2'))
    GEOSERVER_HOME = os.environ.get('GEOSERVER_HOME', '/')
    GEOSERVER_DATA_DIR = os.environ.get('GEOSERVER_DATA_DIR', '/')
    DEFAULT_HTTP_PORT = 8080
    supervisor_config = os.path.join(GEOSERVER_HOME, 'supervisord.conf')

    if NODES_ENABLED <= 1:
        nodes_to_enable = 1
    elif NODES_ENABLED <= MAX_NODES:
        nodes_to_enable = NODES_ENABLED
    else:
        nodes_to_enable = MAX_NODES

    # Create files that are dynamic at runtime
    if not os.path.isfile(supervisor_config):
        gen_supervisord(enabled_nodes=nodes_to_enable, supervisor_config=supervisor_config)
        gen_nginx(max_nodes=nodes_to_enable, default_http_port=DEFAULT_HTTP_PORT)

