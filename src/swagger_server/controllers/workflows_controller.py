import connexion
import six

from swagger_server.models.workflow import Workflow  # noqa: E501
from swagger_server import util


def add_workflow(body):  # noqa: E501
    """Create a new workflow

    This API allows to define a new workflow by specifying an ordered list of operations. Such operations are made available by the installed plugins within the edge module. # noqa: E501

    :param body: Workflow definition
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Workflow.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_workflow_by_id(workflow_id):  # noqa: E501
    """Delete workflow by ID

    This API allows to delete a defined workflow by specifying its ID # noqa: E501

    :param workflow_id: The workflow ID
    :type workflow_id: str

    :rtype: None
    """
    return 'do some magic!'


def get_workflow_by_id(workflow_id):  # noqa: E501
    """Get workflow by ID

    This API allows to get a defined workflow by specifying its ID # noqa: E501

    :param workflow_id: The workflow ID
    :type workflow_id: str

    :rtype: Workflow
    """
    return 'do some magic!'


def get_workflows(limit, offset):  # noqa: E501
    """Get list of defined workflows

    This API allows to get the list of workflows that have been defined within the edge module. # noqa: E501

    :param limit: Number of entities to return
    :type limit: int
    :param offset: Number of entities to skip
    :type offset: int

    :rtype: object
    """
    return 'do some magic!'


def run_workflow_id(workflow_id):  # noqa: E501
    """Run a workflow

    This API allows to run a defined workflow by specifying its ID # noqa: E501

    :param workflow_id: The workflow ID
    :type workflow_id: str

    :rtype: object
    """
    return 'do some magic!'
