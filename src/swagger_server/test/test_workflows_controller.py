# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.workflow import Workflow  # noqa: E501
from swagger_server.test import BaseTestCase


class TestWorkflowsController(BaseTestCase):
    """WorkflowsController integration test stubs"""

    def test_add_workflow(self):
        """Test case for add_workflow

        Create a new workflow
        """
        body = Workflow()
        response = self.client.open(
            '/api/v1/workflows',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_workflow_by_id(self):
        """Test case for delete_workflow_by_id

        Delete workflow by ID
        """
        response = self.client.open(
            '/api/v1/workflows/{workflow_id}'.format(workflow_id='workflow_id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_workflow_by_id(self):
        """Test case for get_workflow_by_id

        Get workflow by ID
        """
        response = self.client.open(
            '/api/v1/workflows/{workflow_id}'.format(workflow_id='workflow_id_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_workflows(self):
        """Test case for get_workflows

        Get list of defined workflows
        """
        query_string = [('limit', 20),
                        ('offset', 0)]
        response = self.client.open(
            '/api/v1/workflows',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_run_workflow_id(self):
        """Test case for run_workflow_id

        Run a workflow
        """
        response = self.client.open(
            '/api/v1/workflows/{workflow_id}/run'.format(workflow_id='workflow_id_example'),
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
