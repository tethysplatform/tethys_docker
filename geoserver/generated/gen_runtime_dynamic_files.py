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


def move_data_dir(geoserver_home, geoserver_data_dir):
    tmp_data_dir = os.path.join(geoserver_home, 'tmp_data')
    try:
        dir_list = os.listdir(tmp_data_dir)
        for item in dir_list:
            shutil.move(os.path.join(tmp_data_dir, item), geoserver_data_dir)
    except shutil.Error:
        sys.stdout.write('WARNING: Could not copy sample data into data dir because the data already exists.')
    try:
        shutil.rmtree(tmp_data_dir)
    except:
        pass


def gen_supervisord(num_enabled_nodes, supervisor_config):
    context = {'nodes': [node_id for node_id in range(1, num_enabled_nodes + 1)]}
    sys.stdout.write("\nConfiguring supervisord for {0} nodes.\n".format(num_enabled_nodes))
    render_and_write_to_file(context=context, template='template_supervisord.conf', filename=supervisor_config)
    sys.stdout.write("Successfully configured supervisord for {0} nodes.\n".format(num_enabled_nodes))


def gen_nginx(num_enabled_nodes, num_rest_nodes, default_http_port):
    """
    Generate the NGINX configuration file, such that it load balances the clustered GeoServers.
    """
    nginx_config = '/etc/nginx/sites-available/default'

    http_ports = [str(default_http_port + node_id) for node_id in range(1, num_enabled_nodes + 1)]
    rest_ports = [str(default_http_port + node_id) for node_id in range(1, num_rest_nodes + 1)]

    context = {'http_ports': http_ports,
               'rest_ports': rest_ports}

    sys.stdout.write("Configuring NGINX load balancer for HTTP endpoints at the following ports: {0}\n".
                     format(', '.join(http_ports)))
    sys.stdout.write("Configuring NGINX load balancer for REST endpoints at the following ports: {0}\n".
                     format(', '.join(rest_ports)))
    render_and_write_to_file(context=context, template='template_nginx_config', filename=nginx_config)
    sys.stdout.write("Successfully generated NGINX load balancer config.\n")


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
            num_cores, num_enabled_nodes
        ))

        # Requests per core
        ows_global_per_core = 25.0
        wms_getmap_per_core = 2.0
        ows_gwc_per_core = 4.0

        # Calculate limits based on cores
        ows_global = ows_global_per_core * num_cores
        wms_getmap = wms_getmap_per_core * num_cores
        ows_gwc = ows_gwc_per_core * num_cores

        # Factor in number of nodes running
        ows_global_per_inst = ows_global / enabled_nodes
        wms_getmap_per_inst = wms_getmap / enabled_nodes
        ows_gwc_per_inst = ows_gwc / enabled_nodes

        ows_global = int(ows_global_per_inst) if ows_global_per_inst >= 1 else 1
        wms_getmap = int(wms_getmap_per_inst) if wms_getmap_per_inst >= 1 else 1
        ows_gwc = int(ows_gwc_per_inst) if ows_gwc_per_inst >= 1 else 1

    # Otherwise derive from explicit environmental variables or use default 4 core configuration
    else:
        sys.stdout.write('Configuring controlflow.properties.\n')
        timeout = int(float(os.environ.get('MAX_TIMEOUT', 60)) / enabled_nodes)
        ows_global = int(float(os.environ.get('MAX_OWS_GLOBAL', 100)) / enabled_nodes)
        wms_getmap = int(float(os.environ.get('MAX_WMS_GETMAP', 10)) / enabled_nodes)
        ows_gwc = int(float(os.environ.get('MAX_OWS_GWC', 16)) / enabled_nodes)

    context = {'timeout': timeout,
               'ows_global': ows_global,
               'wms_getmap': wms_getmap,
               'ows_gwc': ows_gwc}

    sys.stdout.write('Writing controlflow.properties with the following settings:\n')
    sys.stdout.write('  timeout={0}\n'.format(timeout))
    sys.stdout.write('  ows.global={0}\n'.format(ows_global))
    sys.stdout.write('  ows.wms.getmap={0}\n'.format(wms_getmap))
    sys.stdout.write('  ows.gwc={0}\n'.format(ows_gwc))

    control_flow_props = os.path.join(geoserver_data_dir, 'controlflow.properties')
    render_and_write_to_file(context=context, template='template_controlflow.properties', filename=control_flow_props)
    sys.stdout.write("Successfully generated controlflow.properties.\n")


if '__main__' in __name__:
    MAX_NODES = int(os.environ.get('MAX_NODES', '4'))
    ENABLED_NODES = int(os.environ.get('ENABLED_NODES', '1'))
    REST_NODES = int(os.environ.get('REST_NODES', '1'))
    GEOSERVER_HOME = os.environ.get('GEOSERVER_HOME', '/')
    GEOSERVER_DATA_DIR = os.environ.get('GEOSERVER_DATA_DIR', '/')
    DEFAULT_HTTP_PORT = 8080
    supervisor_config = os.path.join(GEOSERVER_HOME, 'supervisord.conf')

    if ENABLED_NODES <= 1:
        num_enabled_nodes = 1
    elif ENABLED_NODES <= MAX_NODES:
        num_enabled_nodes = ENABLED_NODES
    else:
        num_enabled_nodes = MAX_NODES

    if REST_NODES <= 1:
        num_rest_nodes = 1
    elif REST_NODES <= num_enabled_nodes:
        num_rest_nodes = REST_NODES
    else:
        num_rest_nodes = num_enabled_nodes

    # Create files that are dynamic at runtime
    if not os.path.isfile(supervisor_config):
        move_data_dir(geoserver_data_dir=GEOSERVER_DATA_DIR, geoserver_home=GEOSERVER_HOME)
        gen_supervisord(num_enabled_nodes=num_enabled_nodes, supervisor_config=supervisor_config)
        gen_nginx(num_enabled_nodes=num_enabled_nodes, num_rest_nodes=num_rest_nodes,
                  default_http_port=DEFAULT_HTTP_PORT)
        gen_controlflow_properties(enabled_nodes=num_enabled_nodes, geoserver_data_dir=GEOSERVER_DATA_DIR)

