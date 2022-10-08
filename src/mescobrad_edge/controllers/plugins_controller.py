import connexion
import six

from mescobrad_edge.models.plugin import Plugin  # noqa: E501
from mescobrad_edge.models.plugin_configuration import PluginConfiguration  # noqa: E501
from mescobrad_edge import util

import mescobrad_edge.singleton as singleton

import boto3
from botocore.client import Config
from io import BytesIO
import datetime


def delete_plugin_by_id(plugin_id):  # noqa: E501
    """Uninstall plugin by ID

    This API allows to uninstall a plugin by specifying its ID # noqa: E501

    :param plugin_id: The plugin ID
    :type plugin_id: str

    :rtype: None
    """
    if singleton.plugin_manager.get_plugin_info(plugin_id) is not None:
        singleton.plugin_manager.delete_plugin_folder(plugin_id)
        return None, 202
    else:
        return None, 404


def get_plugin_by_id(plugin_id):  # noqa: E501
    """Get installed plugin by ID

    This API allows to get an installed plugin by specifying its ID # noqa: E501

    :param plugin_id: The plugin ID
    :type plugin_id: str

    :rtype: Plugin
    """
    plugin_info = singleton.plugin_manager.get_plugin_info(plugin_id)

    return (Plugin.from_dict(plugin_info), 200) if plugin_info is not None else (None, 404)


def get_plugin_config_by_id(plugin_id):  # noqa: E501
    """Get installed plugin configuration by plugin ID

    This API allows to get the configuration of an installed plugin by specifying its ID # noqa: E501

    :param plugin_id: The plugin ID
    :type plugin_id: str

    :rtype: PluginConfiguration
    """
    return 'do some magic!'


def get_plugins(limit, offset):  # noqa: E501
    """Get list of installed plugins

    This API allows to get the list of plugins that have been installed within the edge module. # noqa: E501

    :param limit: Number of entities to return
    :type limit: int
    :param offset: Number of entities to skip
    :type offset: int

    :rtype: Plugin
    """

    plugin_raw_list = singleton.plugin_manager.list_plugins()
    return [Plugin.from_dict(p) for p in plugin_raw_list.values()][offset:offset+limit], 200


def install_plugin(body):  # noqa: E501
    """Install plugin

    This API allows to install a plugin within the edge module # noqa: E501

    :param body: Plugin details
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        new_plugin = Plugin.from_dict(connexion.request.get_json())  # noqa: E501
        success = singleton.plugin_manager.download_plugin(new_plugin.id, new_plugin.url)
        return (None, 200) if success else (None, 400)
    else:
        return None, 405


def upload_questionnaires_data(upload_file, trigger_anonymization):  # noqa: E501
    """Upload questionnaires data

    This API allows to upload questionnaires data. # noqa: E501

    :param upload_file: The file to upload
    :type upload_file: werkzeug.datastructures.FileStorage
    :param trigger_anonymization: Trigger anonymization workflow
    :type trigger_anonymization: bool

    :rtype: None
    """

    from mescobrad_edge.workflow_engine.workflow_engine import WorkflowEngine

    # Check if data is csv file
    if not upload_file.filename.endswith('.csv'):
        return None, 405

    # Init client
    endpoint_url = ""
    access_id = ""
    secret_access_key = ""
    region_name = "us-east-1"
    obj_storage_bucket = ""
    s3 = boto3.resource('s3',
                        endpoint_url=endpoint_url,
                        aws_access_key_id=access_id,
                        aws_secret_access_key=secret_access_key,
                        config=Config(signature_version='s3v4'),
                        region_name=region_name)

    # Upload data
    if s3.Bucket(obj_storage_bucket).creation_date is None:
            s3.create_bucket(Bucket=obj_storage_bucket)
    file_name = upload_file.filename
    obj_name = "personal_data/" + file_name
    file_content = upload_file.read()
    s3.Bucket(obj_storage_bucket).upload_fileobj(BytesIO(file_content), obj_name, ExtraArgs={'ContentType': "text/csv"})

    # start anonymization workflow
    if trigger_anonymization:
        workflow_engine_singleton = WorkflowEngine()
        workflow_id = "anonymization_data_workflow"
        print(f"Request received.. executing workflow {workflow_id}")
        workflow_engine_singleton.execute_workflow(workflow_id=workflow_id)
    return None, 200


def update_plugin_config_by_id(plugin_id, body):  # noqa: E501
    """Update plugin configuration by plugin ID

    This API allows to update the configuration of an installed plugin by specifying its ID # noqa: E501

    :param plugin_id: The plugin ID
    :type plugin_id: str
    :param body: Plugin configuration
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = PluginConfiguration.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
