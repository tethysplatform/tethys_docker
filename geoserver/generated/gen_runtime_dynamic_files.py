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


def gen_controlflow_properties(enabled_nodes, geoserver_data_dir):
    """
    Generate the controlflow.properties file based on number of cores or explicit environmental variables.
    """
    # Automate based on number of cores if provided
    num_cores = os.environ.get('NUM_CORES', None)

    if num_cores is not None:
        # Timeout is not really calculated by cores...
        timeout = int(os.environ.get('MAX_TIMEOUT', 60))
        num_cores = int(num_cores)
        sys.stdout.write('Configuring controlflow.properties for {0} cores and {1} nodes.\n'.format(
            num_cores, nodes_to_enable
        ))

        # Requests per core
        ows_global_per_core = 25.0
        wms_getmap_per_core = 2.0
        ows_gwc_per_core = 4.0
        per_user_per_core = 2.0

        # Calculate limits based on cores
        ows_global = ows_global_per_core * num_cores
        wms_getmap = wms_getmap_per_core * num_cores
        ows_gwc = ows_gwc_per_core * num_cores
        per_user = per_user_per_core * num_cores

        # Factor in number of nodes running
        ows_global_per_inst = ows_global / enabled_nodes
        wms_getmap_per_inst = wms_getmap / enabled_nodes
        ows_gwc_per_inst = ows_gwc / enabled_nodes
        per_user_per_inst = per_user / enabled_nodes

        ows_global = int(ows_global_per_inst) if ows_global_per_inst >= 1 else 1
        wms_getmap = int(wms_getmap_per_inst) if wms_getmap_per_inst >= 1 else 1
        ows_gwc = int(ows_gwc_per_inst) if ows_gwc_per_inst >= 1 else 1
        per_user = int(per_user_per_inst) if per_user_per_inst >= 1 else 1

    # Otherwise derive from explicit environmental variables or use default 4 core configuration
    else:
        sys.stdout.write('Configuring controlflow.properties.\n')
        timeout = int(os.environ.get('MAX_TIMEOUT', 60))
        ows_global = int(os.environ.get('MAX_OWS_GLOBAL', 100))
        wms_getmap = int(os.environ.get('MAX_WMS_GETMAP', 10))
        ows_gwc = int(os.environ.get('MAX_OWS_GWC', 16))
        per_user = int(os.environ.get('MAX_PER_USER', 6))

    context = {'timeout': timeout,
               'ows_global': ows_global,
               'wms_getmap': wms_getmap,
               'ows_gwc': ows_gwc,
               'per_user': per_user}

    sys.stdout.write('Writing controlflow.properties with the following settings:\n')
    sys.stdout.write('  timeout={0}\n'.format(timeout))
    sys.stdout.write('  ows.global={0}\n'.format(ows_global))
    sys.stdout.write('  ows.wms.getmap={0}\n'.format(wms_getmap))
    sys.stdout.write('  ows.gwc={0}\n'.format(ows_gwc))
    sys.stdout.write('  user={0}\n'.format(per_user))

    control_flow_props = os.path.join(geoserver_data_dir, 'controlflow.properties')
    render_and_write_to_file(context=context, template='template_controlflow.properties', filename=control_flow_props)
    sys.stdout.write("Successfully generated controlflow.properties.\n\n")


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
        gen_controlflow_properties(enabled_nodes=nodes_to_enable, geoserver_data_dir=GEOSERVER_DATA_DIR)

