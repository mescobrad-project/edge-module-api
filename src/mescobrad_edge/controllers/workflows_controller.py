import connexion
import six
import os
import json
import shutil

from mescobrad_edge.models.workflow import Workflow  # noqa: E501
from mescobrad_edge import util

from mescobrad_edge.workflow_engine.workflow_engine import WorkflowEngine
from mescobrad_edge.models.workflow import Workflow
import mescobrad_edge.singleton as singleton

workflow_engine_singleton = WorkflowEngine()

def add_workflow(body):  # noqa: E501
    """Create a new workflow

    This API allows to define a new workflow by specifying an ordered list of operations. Such operations are made available by the installed plugins within the edge module. # noqa: E501

    :param body: Workflow definition
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Workflow.from_dict(connexion.request.get_json())  # noqa: E501

    # Check if input is correct
    if not check_workflow_input(body):
        return None, 405

    # Check if workflow already exists
    if workflow_engine_singleton.__check_workflow__(body.id):
        return None, 409

    # Create directory with new workflow
    # Directory
    directory = body.id

    # Parent Directory path
    parent_dir = "mescobrad_edge/workflows"

    # Path
    path = os.path.join(parent_dir, directory)

    # Create the directory
    os.mkdir(path)
    print("Directory '% s' created" % directory)

    # Creating all needed new files (process.json, run.py, workflow.config) and fill with required information
    # Creating config directory
    path_config = os.path.join(path, ".config")
    os.mkdir(path_config)

    # Creating config file within config directory
    file_path = os.path.join(path_config, "workflow.config")
    with open(file_path, "w") as config_file:
        config_file.write("EXECUTION_INTERVAL = ")
        config_file.write(body.execution_interval)

    # Creating .run file
    file_path = os.path.join(path, ".run")
    run_info_data = {
        "last_execution": "",
        "run_info": []
    }
    with open(file_path, "w") as run_file:
        run_file.write(json.dumps(run_info_data))

    # Creating process.json file
    file_path = os.path.join(path, "process.json")
    ops = [item.to_dict() for item in body.operations]
    process_info_data = {
        "id": body.id,
        "name": body.name,
        "operations": ops
    }
    with open(file_path, "w") as process_file:
        process_file.write(json.dumps(process_info_data))

    return None, 201



def delete_workflow_by_id(workflow_id):  # noqa: E501
    """Delete workflow by ID

    This API allows to delete a defined workflow by specifying its ID # noqa: E501

    :param workflow_id: The workflow ID
    :type workflow_id: str

    :rtype: None
    """
    if not isinstance(workflow_id, str):
        return None, 400
    if not workflow_engine_singleton.__check_workflow__(workflow_id):
        return None, 404

    parent_dir = "mescobrad_edge/workflows"
    path = os.path.join(parent_dir, workflow_id)
    shutil.rmtree(path)
    return None, 204


def get_workflow_by_id(workflow_id):  # noqa: E501
    """Get workflow by ID

    This API allows to get a defined workflow by specifying its ID # noqa: E501

    :param workflow_id: The workflow ID
    :type workflow_id: str

    :rtype: Workflow
    """
    workflow_info = workflow_engine_singleton.get_workflow_info(workflow_id)

    return (Workflow.from_dict(workflow_info), 200) if workflow_info is not None else (None, 404)


def get_workflows(limit, offset):  # noqa: E501
    """Get list of defined workflows

    This API allows to get the list of workflows that have been defined within the edge module. # noqa: E501

    :param limit: Number of entities to return
    :type limit: int
    :param offset: Number of entities to skip
    :type offset: int

    :rtype: object
    """
    if limit < 0 or offset < 0:
        return None, 405
    workflow_raw_list = workflow_engine_singleton.list_workflows()
    return [Workflow.from_dict(p) for p in workflow_raw_list.values()][offset:offset+limit], 200


def run_workflow_id(workflow_id):  # noqa: E501
    """Run a workflow

    This API allows to run a defined workflow by specifying its ID # noqa: E501

    :param workflow_id: The workflow ID
    :type workflow_id: str

    :rtype: object
    """
    print(f"Request received.. executing workflow {workflow_id}")
    workflow_engine_singleton.execute_workflow(workflow_id=workflow_id)

    return None, 201


def is_empty_string(body):
    """Check if fields in workflow input are empty."""
    if not body.id.strip() or not body.name.strip() or not body.operations:
        return True
    else:
        return False


def is_present_plugin_id(body):
    """Check if plugin_id is correct"""
    return all(elem.plugin_id in singleton.plugin_manager.plugin_list.keys() for elem in body.operations)


def check_workflow_input(body):
    """Check if input for creating workflow is correct"""
    if not is_empty_string(body) and \
        is_present_plugin_id(body):
        return True
    else:
        return False