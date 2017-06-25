# stdlib imports
import copy
from datetime import datetime


def prepare_app_definition(app_definition, old_app_definition=None, app_states=None):
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
        _rotate_colour(new_app_definition, old_app_definition)
        _rotate_port(new_app_definition, old_app_definition)
    else:
        _set_app_colour(new_app_definition, 'blue')
        _init_service_ports(new_app_definition, app_states)

    new_app_definition = _set_service_port(new_app_definition, next_port)
    new_app_definition['id'] = new_app_definition['id'] + '-' + _get_app_colour(new_app_definition)
    new_app_definition['labels']['HAPROXY_APP_ID'] = app_definition['id']
    new_app_definition['labels']['HAPROXY_DEPLOYMENT_STARTED_AT'] = datetime.now().isoformat()
    new_app_definition['labels']['HAPROXY_DEPLOYMENT_TARGET_INSTANCES'] = str(new_app_definition['instances'])
    return new_app_definition


def _init_service_ports(app_definition, app_states):
    """Determines that start port for the application and updates the application state.
    This works for both Dockerised and non-Dockerised applications.
    """
    next_service_port = 0
    for app_state in app_states:
      next_service_port = max(next_service_port + 1, int(app_state["labels"]["HAPROXY_0_PORT"]))

    app_definition['labels']['HAPROXY_0_PORT'] = next_service_port
    app_definition['labels']['HAPROXY_1_PORT'] = next_service_port + 1 
    return next_service_port

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

def _rotate_port(new_app_definition, old_app_definition):
    """Given a currently deployed app definition, return the service port to use
    for the next blue/green deployment.
    """
    next_port = old_app_definition['labels']['HAPROXY_1_PORT']
    new_app_definition['labels']['HAPROXY_1_PORT'] = old_app_defintiion['labels']['HAPROXY_0_PORT']
    new_app_definition['labels']['HAPROXY_0_PORT'] = next_port
    return new_app_definition

def _rotate_colour(new_app_definition, old_app_definition):
    """Given a currently deployed app definition, return the "color" to use for
    the next blue/green deployment.

    Right now this simply swaps the colors used, but could be extended in future
    to allow for more complex behaviour.
    """
    colours = {"blue": "green", "green": "blue"}
    old_colour = _get_app_colour(old_app_definition)
    return _set_app_colour(new_app_definition, colors[old_colour])

def _get_app_colour(app_definition):
  return app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR']

def _set_app_colour(app_definition, colour):
    app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR'] = colour
    return app_definition
