# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.body import Body  # noqa: E501
from swagger_server.models.plugin import Plugin  # noqa: E501
from swagger_server.models.plugin_configuration import PluginConfiguration  # noqa: E501
from swagger_server.test import BaseTestCase


class TestPluginsController(BaseTestCase):
    """PluginsController integration test stubs"""

    def test_delete_plugin_by_id(self):
        """Test case for delete_plugin_by_id

        Uninstall plugin by ID
        """
        response = self.client.open(
            '/api/v1/plugins/{plugin_id}'.format(plugin_id='plugin_id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_plugin_by_id(self):
        """Test case for get_plugin_by_id

        Get installed plugin by ID
        """
        response = self.client.open(
            '/api/v1/plugins/{plugin_id}'.format(plugin_id='plugin_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_plugin_config_by_id(self):
        """Test case for get_plugin_config_by_id

        Get installed plugin configuration by plugin ID
        """
        response = self.client.open(
            '/api/v1/plugins/{plugin_id}/config'.format(plugin_id='plugin_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_plugins(self):
        """Test case for get_plugins

        Get list of installed plugins
        """
        query_string = [('limit', 20),
                        ('offset', 0)]
        response = self.client.open(
            '/api/v1/plugins',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_install_plugin(self):
        """Test case for install_plugin

        Install plugin
        """
        body = Plugin()
        response = self.client.open(
            '/api/v1/plugins',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_plugin_config_by_id(self):
        """Test case for update_plugin_config_by_id

        Update plugin configuration by plugin ID
        """
        body = Body()
        response = self.client.open(
            '/api/v1/plugins/{plugin_id}/config'.format(plugin_id='plugin_id_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
