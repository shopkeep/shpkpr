# stdlib imports
import socket

# third-party imports
import six.moves.urllib as urllib


def resolve(marathon_lb_url):
    """Return the individual URLs for all available Marathon-LB instances given
    a single URL to a DNS-balanced Marathon-LB cluster.

    Marathon-LB typically uses DNS for load balancing between instances and so
    the address provided by the user may actually be multiple load-balanced
    instances. This function uses DNS to lookup the hostnames (IPv4 A-records)
    of each instance, returning them all to the caller for use as required.
    """
    url = urllib.parse.urlparse(marathon_lb_url)
    all_hosts = _get_alias_records(url.hostname)
    resolved_urls = _reassemble_urls(url, all_hosts)
    return resolved_urls


def _get_alias_records(hostname):
    """Return all IPv4 A records for a given hostname
    """
    return socket.gethostbyname_ex(hostname)[2]


def _reassemble_urls(url, hosts):
    return [_reassemble_url(url, host) for host in hosts]


def _reassemble_url(url, host):
    """Reassemble a stringified URL with the host replaced
    """
    netloc = "{0}:{1}".format(host, url.port)
    parts = (url[0], netloc, url[2], url[3], url[4], url[5])
    return urllib.parse.urlunparse(parts)
