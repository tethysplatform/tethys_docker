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
    nginx_config = '/etc/nginx/sites-available/default'

    default_http_port = 8080

    http_ports = []

    for node_id in range(1, max_nodes + 1):
        http_port = default_http_port + node_id
        http_ports.append(str(http_port))

    sys.stdout.write("\nConfiguring NGINX load balancer for the following ports: {0}\n".format(', '.join(http_ports)))

    template_directory = os.path.dirname(__file__)
    file_contents = render_from_template(template_directory, 'template_nginx_config', http_ports=http_ports)

    with open(nginx_config, 'w') as f:
        f.write(file_contents)

    sys.stdout.write("Successfully generated NGINX load balancer config.\n\n")
