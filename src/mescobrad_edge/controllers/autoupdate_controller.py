import json
import requests

import connexion
import six

#from swagger_server import util

def current_version():  # noqa: E501
    """Get installed version of edge module

    This API allows to get the version of the installed edge module # noqa: E501


    :rtype: text/plain
    """
    return handle_request('/current')

def update_module():  # noqa: E501
    """Update edge module to latest version

    This API allows to update the edge module to the latest version.


    :rtype: str
    """
    return handle_request('/update')

def update_to_version(version):  # noqa: E501
    """Update edge module to specified version

    This API allows to update the edge module to the specified version.


    :param version: The version to update to (e.g., 1.2.3)
    :type version: str
    :rtype: str
    """
    return handle_request('/update/{}'.format(version))

def list_available_versions():  # noqa: E501
    """List available edge module versions

    This API lists the available versions of the edge module.


    :rtype: list[str]
    """
    return handle_request('/listversions')

def update_plugin(plugin_name):  # noqa: E501
    """Update specified plugin to latest version

    This API allows to update the specified plugin to the latest version.


    :param plugin_name: The name of the plugin to update
    :type plugin_name: str
    :rtype: str
    """
    return handle_request('/updateplugin/{}'.format(plugin_name))

def handle_request(path):
    response = requests.get('http://mescobrad_autoupdate:8081/{}'.format(path))
    content = response.content.decode('utf-8') # Decode the bytes object to a string
    print(content)
    return content

