# stdlib imports
import logging


logger = logging.getLogger(__name__)


def resolve_secrets(vault_client, rendered_template):
    """Parse a rendered template, extract any secret definitions, retrieve them
    from vault and return them to the caller.

    This is used in situations where direct Vault support is not available e.g.
    Chronos.
    """
    resolved_secrets = {}

    secrets = rendered_template.get("secrets", {})
    for name, definition in secrets.items():
        # parse the secret source and retrieve from vault
        path, key = definition["source"].split(":")
        secret = vault_client.read(path)
        if secret:
            resolved_secrets[name] = secret["data"][key]
        else:
            logger.info("Couldn't locate secret in Vault: {0}".format(path))

    return resolved_secrets
