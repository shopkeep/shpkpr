# stdlib imports
import copy
from datetime import datetime


def prepare_app_definition(app_definition, old_app_definition=None):
    """Prepares ``app_definition`` for blue/green deployment by adding the
    necessary Marathon labels and setting the ID and service port.

    If an old app definition is passed in, it will be used to correctly pick the
    color and port for the new deployment, otherwise we default to "blue" and
    use the ports as defined in the new app definition.
    """
    # make a deep copy of the new app definition before we start mutating it so
    # we can refer back to properties of the original as needed.
    new_app_definition = copy.deepcopy(app_definition)

    if old_app_definition is not None:
        next_colour = _select_next_colour(old_app_definition)
        next_port = _select_next_port(old_app_definition)
    else:
        next_colour = 'blue'
        next_port = _get_service_port(new_app_definition)

    new_app_definition = _set_service_port(new_app_definition, next_port)
    new_app_definition['id'] = new_app_definition['id'] + '-' + next_colour
    new_app_definition['labels']['HAPROXY_APP_ID'] = app_definition['id']
    new_app_definition['labels']['HAPROXY_0_PORT'] = str(_get_service_port(app_definition))
    new_app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR'] = next_colour
    new_app_definition['labels']['HAPROXY_DEPLOYMENT_STARTED_AT'] = datetime.now().isoformat()
    new_app_definition['labels']['HAPROXY_DEPLOYMENT_TARGET_INSTANCES'] = str(new_app_definition['instances'])
    return new_app_definition


def _get_service_port(app_definition):
    """Extract the currently configured service port from an app definition.

    This works for both Dockerised and non-Dockerised applications.
    """
    try:
        port_mappings = app_definition['container']['docker']['portMappings']
        service_port = port_mappings[0]['servicePort']
    except (KeyError, IndexError):
        service_port = app_definition['ports'][0]
    return int(service_port)


def _set_service_port(app_definition, service_port):
    """Set the service port on the provided app definition.

    This works for both Dockerised and non-Dockerised applications.
    """
    try:
        port_mappings = app_definition['container']['docker']['portMappings']
        port_mappings[0]['servicePort'] = service_port
    except (KeyError, IndexError):
        app_definition['ports'][0] = service_port
    return app_definition


def _select_next_colour(app_definition):
    """Given a currently deployed app definition, return the "color" to use for
    the next blue/green deployment.

    Right now this simply swaps the colors used, but could be extended in future
    to allow for more complex behaviour.
    """
    colors = {"blue": "green", "green": "blue"}
    old_color = app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR']
    return colors[old_color]


def _select_next_port(app_definition):
    """Given a currently deployed app definition, return the service port to use
    for the next blue/green deployment.
    """
    current_port = _get_service_port(app_definition)
    default_port = int(app_definition['labels']['HAPROXY_0_PORT'])
    alternate_port = int(app_definition['labels']['HAPROXY_DEPLOYMENT_ALT_PORT'])

    if current_port == default_port:
        return alternate_port
    return default_port
