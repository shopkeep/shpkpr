# stdlib imports
import copy
import random
from datetime import datetime


def prepare_app_definition(app_definition, old_app_definition=None, apps_state=None, marathon_info=None):
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
        _init_ports(new_app_definition, apps_state, marathon_info)

    new_app_definition['id'] = new_app_definition['id'] + '-' + _get_app_colour(new_app_definition)
    new_app_definition['labels']['HAPROXY_APP_ID'] = app_definition['id']
    new_app_definition['labels']['HAPROXY_DEPLOYMENT_STARTED_AT'] = datetime.now().isoformat()
    new_app_definition['labels']['HAPROXY_DEPLOYMENT_TARGET_INSTANCES'] = str(new_app_definition['instances'])
    return new_app_definition


def _init_ports(app_definition, apps_state, marathon_info):
    """Determines that start port for the application and updates the application state.
    This works for both Dockerised and non-Dockerised applications.
    """
    if _is_service_port_defined(app_definition):
        service_port = _get_service_port(app_definition)
        alt_port = _get_alt_port(app_definition)
    else:
        service_port = _select_next_port(apps_state, marathon_info, [])
        alt_port = _select_next_port(apps_state, marathon_info, [service_port])

    app_definition = _set_current_port(app_definition, service_port)
    app_definition = _set_service_port(app_definition, service_port)
    app_definition = _set_alt_port(app_definition, alt_port)
    return app_definition


def _select_next_port(apps_state, marathon_info, used_ports):
    """Given a currently deployed app definition, return the service port to use
    for the next blue/green deployment.
    """
    min_port = marathon_info['marathon_config']['local_port_min']
    max_port = marathon_info['marathon_config']['local_port_max']

    for app_definition in apps_state:
        used_ports.append(_get_service_port(app_definition))
        used_ports.append(_get_alt_port(app_definition))

    while True:
        port = random.randint(min_port, max_port)
        if port not in used_ports:
            return port


def _rotate_port(new_app_definition, old_app_definition):
    """Given a currently deployed app definition, return the service port to use
    for the next blue/green deployment.
    """
    primary_port = _get_service_port(old_app_definition)
    secondary_port = _get_alt_port(old_app_definition)
    current_port = _get_current_port(old_app_definition)
    if current_port == primary_port:
        new_app_definition = _set_current_port(new_app_definition, secondary_port)
    else:
        new_app_definition = _set_current_port(new_app_definition, primary_port)

    _set_service_port(new_app_definition, _get_service_port(old_app_definition))
    _set_alt_port(new_app_definition, _get_alt_port(old_app_definition))
    return new_app_definition


def _rotate_colour(new_app_definition, old_app_definition):
    """Given a currently deployed app definition, return the "color" to use for
    the next blue/green deployment.

    Right now this simply swaps the colors used, but could be extended in future
    to allow for more complex behaviour.
    """
    colours = {"blue": "green", "green": "blue"}
    old_colour = _get_app_colour(old_app_definition)
    return _set_app_colour(new_app_definition, colours[old_colour])


def _is_service_port_defined(app_definition):
    return _get_service_port(app_definition) is not None and 'HAPROXY_DEPLOYMENT_ALT_PORT' in app_definition['labels']


def _set_current_port(app_definition, service_port):
    """Set the service port on the provided app definition.

    This works for both Dockerised and non-Dockerised applications.
    """
    try:
        port_mappings = app_definition['container']['docker']['portMappings']
        port_mappings[0]['servicePort'] = service_port
    except (KeyError, IndexError):
        app_definition['ports'][0] = service_port

    return app_definition


def _set_service_port(app_definition, service_port):
    """Set the service port on the provided app definition.

    This works for both Dockerised and non-Dockerised applications.
    """
    app_definition['labels']['HAPROXY_0_PORT'] = str(service_port)
    return app_definition


def _set_alt_port(app_definition, alt_port):
    """Set the alt port on the provided app definition.

    This works for both Dockerised and non-Dockerised applications.
    """
    app_definition['labels']['HAPROXY_DEPLOYMENT_ALT_PORT'] = str(alt_port)
    return app_definition


def _get_current_port(app_definition):
    try:
        port_mappings = app_definition['container']['docker']['portMappings']
        service_port = port_mappings[0]['servicePort']
    except (KeyError, IndexError):
        if 'ports' in app_definition:
            service_port = app_definition['ports'][0]
        else:
            return None
    return int(service_port)


def _get_alt_port(app_definition):
    if 'HAPROXY_DEPLOYMENT_ALT_PORT' in app_definition['labels']:
        return int(app_definition['labels']['HAPROXY_DEPLOYMENT_ALT_PORT'])
    return None


def _get_service_port(app_definition):
    if 'HAPROXY_0_PORT' in app_definition['labels']:
        return int(app_definition['labels']['HAPROXY_0_PORT'])
    return _get_current_port(app_definition)


def _get_app_colour(app_definition):
    return app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR']


def _set_app_colour(app_definition, colour):
    app_definition['labels']['HAPROXY_DEPLOYMENT_COLOUR'] = colour
    return app_definition
