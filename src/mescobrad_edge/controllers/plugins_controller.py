import connexion
import six

from mescobrad_edge.models.plugin import Plugin  # noqa: E501
from mescobrad_edge.models.plugin_configuration import PluginConfiguration  # noqa: E501
from mescobrad_edge import util

import mescobrad_edge.singleton as singleton

import boto3
from botocore.client import Config
from io import BytesIO
import os
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
        # extract plugin_id from url
        plugin_id = os.path.basename(new_plugin.url).split('.')[0]
        success = singleton.plugin_manager.download_plugin(plugin_id, new_plugin.url)
        return (None, 200) if success else (None, 400)
    else:
        return None, 405


def upload_questionnaires_data(upload_file, trigger_anonymization, workspace_id,
                               upload_metadata_json_file=None,
                               first_name=None, last_name=None, date_of_birth=None,
                               unique_id=None, clinical_id=None):  # noqa: E501
    """Upload questionnaires data

    This API allows to upload questionnaires data. # noqa: E501

    :param upload_file: The file to upload
    :type upload_file: werkzeug.datastructures.FileStorage
    :param trigger_anonymization: Trigger anonymization workflow
    :type trigger_anonymization: bool
    :param workspace_id: Workspace ID from which file is uploaded
    :type workspace_id: str
    :param upload_metadata_json_file: The file to upload
    :type upload_metadata_json_file: werkzeug.datastructures.FileStorage
    :param first_name: Name of the patient.
    :type first_name: str
    :param last_name: Surname of the patient.
    :type last_name: str
    :param date_of_birth: Date of birth of the patient.
    :type date_of_birth: str
    :param unique_id: Unique ID of the patient.
    :type unique_id: str
    :param clinical_id: Clinical ID of the patient.
    :type clinical_id: str

    :rtype: None
    """

    from mescobrad_edge.workflow_engine.workflow_engine import WorkflowEngine
    import configparser
    import re

    # Check if data is csv file
    if not upload_file.filename.lower().endswith('.csv'):
        return None, 405

    # Check parameters if any of the non-required params is present, then all need to be
    # filled in
    if any(param is not None for param in [first_name, last_name, date_of_birth, unique_id]):
        if any(param is None for param in [first_name, last_name, date_of_birth, unique_id]):
            return "Fill name, surname, date_of_birth and unique_id_of_patient.", 405

    # Data which needs to be propagated in the corresponding plugin
    exchange_data_info = {"name": first_name,
                          "surname": last_name,
                          "date_of_birth": date_of_birth,
                          "unique_id": unique_id,
                          "MRN": clinical_id,
                          "workspace_id": workspace_id,
                          "metadata_json_file": upload_metadata_json_file.read() if upload_metadata_json_file is not None else None}
    # Init client
    CONF_FILE_PATH = 'mescobrad_edge/edge_module.config'
    PLUGIN_CONF_MAIN_SECTION = 'edge-module-configuration'
    config = configparser.ConfigParser()
    config.read(CONF_FILE_PATH)
    s3 = boto3.resource('s3',
                        endpoint_url=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_URL_LOCAL"],
                        aws_access_key_id=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_ACCESS_ID_LOCAL"],
                        aws_secret_access_key=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_ACCESS_SECRET_LOCAL"],
                        config=Config(signature_version='s3v4'),
                        region_name=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_REGION"])

    # Upload data
    obj_storage_bucket = config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_BUCKET_LOCAL"]

    # Create a bucket if it is not created
    if s3.Bucket(obj_storage_bucket).creation_date is None:
            s3.create_bucket(Bucket=obj_storage_bucket)

    # Before uploading a new file, empty the folder if it is not empty
    objs = list(s3.Bucket(obj_storage_bucket).objects.filter(Prefix="csv_data/", Delimiter="/"))
    if len(list(objs))>0:
        for obj in objs:
            s3.Bucket(obj_storage_bucket).objects.filter(Prefix=obj.key).delete()

    # Upload a provided file
    file_name = upload_file.filename
    # Remove any special character from the file_name
    file_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(file_name)[0]) + ".csv"
    obj_name = "csv_data/" + file_name
    file_content = upload_file.read()
    s3.Bucket(obj_storage_bucket).upload_fileobj(BytesIO(file_content), obj_name,
                                                 ExtraArgs={'ContentType': "text/csv"})

    # start anonymization workflow
    if trigger_anonymization:
        workflow_engine_singleton = WorkflowEngine(data_info=exchange_data_info)
        workflow_id = "anonymization_data_workflow"
        print(f"Request received.. executing workflow {workflow_id}")
        workflow_engine_singleton.execute_workflow(workflow_id=workflow_id)
    return None, 202


def upload_mri_data(upload_mri_file, deface_method, trigger_anonymization,
                    upload_to_cloud, workspace_id,
                    upload_anonymized_and_defaced_data=False,
                    upload_metadata_json_file=None, first_name=None,
                    last_name=None, date_of_birth=None, unique_id=None,
                    clinical_id=None):  # noqa: E501
    """Upload MRI data

    This API allows to upload MRI data. # noqa: E501

    :param upload_mri_file: The MRI file to upload
    :type upload_mri_file: werkzeug.datastructures.FileStorage
    :param deface_method: Choose freesurfer or deface (FSL deface) option.
    :type deface_method: str
    :param trigger_anonymization: Trigger MRI anonymization workflow
    :type trigger_anonymization: bool
    :param upload_to_cloud: Upload defaced and anonymized MRI DICOM files.
    :type upload_to_cloud: bool
    :param workspace_id: Workspace ID from which file is uploaded
    :type workspace_id: str
    :param upload_anonymized_and_defaced_data: Upload already anonymized and defaced data
    :type upload_anonymized_and_defaced_data: bool
    :param upload_metadata_json_file: The file to upload
    :type upload_metadata_json_file: werkzeug.datastructures.FileStorage
    :param first_name: Name of the patient.
    :type first_name: str
    :param last_name: Surname of the patient.
    :type last_name: str
    :param date_of_birth: Date of birth of the patient.
    :type date_of_birth: str
    :param national_unique_id: Unique ID of the patient.
    :type national_unique_id: str
    :param clinical_id: Clinical ID of the patient.
    :type clinical_id: str

    :rtype: None
    """
    from mescobrad_edge.workflow_engine.workflow_engine import WorkflowEngine
    import configparser
    import re
    import time
    import pytz

    # Check if data is csv file
    if not upload_mri_file.filename.lower().endswith('.zip'):
        return None, 405

    # Check parameters if any of the non-required params is present, then all need to be
    # filled in
    if any(param is not None for param in [first_name, last_name, date_of_birth, unique_id]):
        if any(param is None for param in [first_name, last_name, date_of_birth, unique_id]):
            return "Fill name, surname, date_of_birth and unique_id_of_patient.", 405

    # Data which needs to be propagated in the corresponding plugin
    exchange_data_info = {"name": first_name,
                          "surname": last_name,
                          "date_of_birth": date_of_birth,
                          "unique_id": unique_id,
                          "MRN": clinical_id,
                          "workspace_id": workspace_id,
                          "metadata_json_file": upload_metadata_json_file.read() if upload_metadata_json_file is not None else None,
                          "upload_anonymized_and_defaced_data": upload_anonymized_and_defaced_data}

    # Init client
    CONF_FILE_PATH = 'mescobrad_edge/edge_module.config'
    PLUGIN_CONF_MAIN_SECTION = 'edge-module-configuration'
    config = configparser.ConfigParser()
    config.read(CONF_FILE_PATH)
    s3 = boto3.resource('s3',
                        endpoint_url=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_URL_LOCAL"],
                        aws_access_key_id=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_ACCESS_ID_LOCAL"],
                        aws_secret_access_key=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_ACCESS_SECRET_LOCAL"],
                        config=Config(signature_version='s3v4'),
                        region_name=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_REGION"])

    # Upload data
    if trigger_anonymization:
        obj_storage_bucket = config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_BUCKET_LOCAL"]

        # Create a bucket if it is not created
        if s3.Bucket(obj_storage_bucket).creation_date is None:
                s3.create_bucket(Bucket=obj_storage_bucket)

        # Before uploading a new file, empty the folder if there are files to remove
        objs = list(s3.Bucket(obj_storage_bucket).objects.filter(Prefix="mri_data/", Delimiter="/"))
        if len(list(objs))>0:
            for obj in objs:
                time_threshold = datetime.datetime.now(pytz.UTC) - datetime.timedelta(hours=12)
                if obj.last_modified < time_threshold:
                    s3.Bucket(obj_storage_bucket).objects.filter(Prefix=obj.key).delete()

        # Upload a provided file
        file_name = upload_mri_file.filename
        # Remove any special character from the file_name
        file_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(file_name)[0]) + ".zip"
        ts = round(time.time()*1000)
        filename = os.path.splitext(file_name)[0] + "_" + str(ts) + ".tmp.part"
        obj_name = "mri_data/" + filename
        exchange_data_info["filename"] = obj_name
        file_content = upload_mri_file.read()
        s3.Bucket(obj_storage_bucket).upload_fileobj(BytesIO(file_content), obj_name, ExtraArgs={'ContentType': "application/zip"})

    # start anonymization workflow
    if trigger_anonymization and not upload_to_cloud:
        if deface_method == "freesurfer":
            workflow_id = "MRI_freesurfer_anonymization_workflow"
        else:
            # TO DO - Extend this, when second deface method is added
            workflow_id = ""

        workflow_engine_singleton = WorkflowEngine(data_info=exchange_data_info)
        print(f"Request received.. executing workflow {workflow_id}")
        workflow_engine_singleton.execute_workflow(workflow_id=workflow_id)

    elif trigger_anonymization and upload_to_cloud:
        workflow_id = "MRI_anonymized_data_upload_to_cloud_workflow"

        workflow_engine_singleton = WorkflowEngine(data_info=exchange_data_info)
        print(f"Request received.. executing workflow {workflow_id}")
        workflow_engine_singleton.execute_workflow(workflow_id=workflow_id)
    return None, 202


def upload_edf_data(upload_edf_file, trigger_anonymization, workspace_id,
                    upload_metadata_json_file=None, first_name=None, last_name=None,
                    date_of_birth=None, unique_id=None, clinical_id=None):  # noqa: E501
    """Upload edf file

    This API allows to upload edf data. # noqa: E501

    :param upload_edf_file: The edf file to upload.
    :type upload_edf_file: werkzeug.datastructures.FileStorage
    :param trigger_anonymization: Trigger edf anonymization workflow
    :type trigger_anonymization: bool
    :param workspace_id: Workspace ID from which file is uploaded
    :type workspace_id: str
    :param upload_metadata_json_file: The file to upload
    :type upload_metadata_json_file: werkzeug.datastructures.FileStorage
    :param first_name: Name of the patient.
    :type first_name: str
    :param last_name: Surname of the patient.
    :type last_name: str
    :param date_of_birth: Date of birth of the patient.
    :type date_of_birth: str
    :param unique_id: Unique ID of the patient.
    :type unique_id: str
    :param clinical_id: Clinical ID of the patient.
    :type clinical_id: str

    :rtype: None
    """
    from mescobrad_edge.workflow_engine.workflow_engine import WorkflowEngine
    import configparser
    import re

    # Check if data is edf file
    if not upload_edf_file.filename.lower().endswith('.edf'):
        return None, 405

    # Check parameters if any of the non-required params is present, then all need to be
    # filled in
    if any(param is not None for param in [first_name, last_name, date_of_birth, unique_id]):
        if any(param is None for param in [first_name, last_name, date_of_birth, unique_id]):
            return "Fill name, surname, date_of_birth and unique_id_of_patient.", 405

    # Data which needs to be propagated in the corresponding plugin
    exchange_data_info = {"name": first_name,
                          "surname": last_name,
                          "date_of_birth": date_of_birth,
                          "unique_id": unique_id,
                          "MRN": clinical_id,
                          "workspace_id": workspace_id,
                          "metadata_json_file": upload_metadata_json_file.read() if upload_metadata_json_file is not None else None}

    # Init client
    CONF_FILE_PATH = 'mescobrad_edge/edge_module.config'
    PLUGIN_CONF_MAIN_SECTION = 'edge-module-configuration'
    config = configparser.ConfigParser()
    config.read(CONF_FILE_PATH)
    s3 = boto3.resource('s3',
                        endpoint_url=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_URL_LOCAL"],
                        aws_access_key_id=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_ACCESS_ID_LOCAL"],
                        aws_secret_access_key=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_ACCESS_SECRET_LOCAL"],
                        config=Config(signature_version='s3v4'),
                        region_name=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_REGION"])

    # Upload data
    obj_storage_bucket = config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_BUCKET_LOCAL"]

    # Create bucket if it is not created
    if s3.Bucket(obj_storage_bucket).creation_date is None:
            s3.create_bucket(Bucket=obj_storage_bucket)

    # Before uploading a new file, empty the folder if it is not empty
    objs = list(s3.Bucket(obj_storage_bucket).objects.filter(Prefix="edf_data_tmp/", Delimiter="/"))
    if len(list(objs))>0:
        for obj in objs:
            s3.Bucket(obj_storage_bucket).objects.filter(Prefix=obj.key).delete()

    # Upload a provided file
    file_name = upload_edf_file.filename
    # Remove any special character from the file_name
    file_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(file_name)[0]) + ".edf"
    obj_name = "edf_data_tmp/" + file_name
    file_content = upload_edf_file.read()
    s3.Bucket(obj_storage_bucket).upload_fileobj(BytesIO(file_content), obj_name)

    # Start anonymization workflow
    if trigger_anonymization:
        workflow_id = "EDF_anonymization_workflow"
        workflow_engine_singleton = WorkflowEngine(data_info=exchange_data_info)
        print(f"Request received.. executing workflow {workflow_id}")
        workflow_engine_singleton.execute_workflow(workflow_id=workflow_id)
    return None, 202


def upload_actiwatch_actigraphy_data(upload_actigraphy_file, workspace_id,
                                     upload_metadata_json_file=None, first_name=None,
                                     last_name=None, date_of_birth=None, unique_id=None,
                                     clinical_id=None):  # noqa: E501
    """Upload actiwatch (Philips) actigraphy data

    This API allows to upload actigraphy data from actiwatch Philips data. # noqa: E501

    :param upload_file: The actiwatch actigraphy file to upload
    :type upload_file: werkzeug.datastructures.FileStorage
    :param workspace_id: Workspace ID from which file is uploaded
    :type workspace_id: str
    :param upload_metadata_json_file: The file to upload
    :type upload_metadata_json_file: werkzeug.datastructures.FileStorage
    :param first_name: Name of the patient.
    :type first_name: str
    :param last_name: Surname of the patient.
    :type last_name: str
    :param date_of_birth: Date of birth of the patient.
    :type date_of_birth: str
    :param unique_id: Unique ID of the patient.
    :type unique_id: str
    :param clinical_id: Clinical ID of the patient.
    :type clinical_id: str

    :rtype: None
    """
    from mescobrad_edge.workflow_engine.workflow_engine import WorkflowEngine
    import configparser
    import re

    # Check if data is in csv file format
    if not upload_actigraphy_file.filename.lower().endswith('.csv'):
        return None, 405

    # Check parameters if any of the non-required params is present, then all need to be
    # filled in
    if any(param is not None for param in [first_name, last_name, date_of_birth, unique_id]):
        if any(param is None for param in [first_name, last_name, date_of_birth, unique_id]):
            return "Fill name, surname, date_of_birth and unique_id_of_patient.", 405

    # Data which needs to be propagated in the corresponding plugin
    exchange_data_info = {"name": first_name,
                          "surname": last_name,
                          "date_of_birth": date_of_birth,
                          "unique_id": unique_id,
                          "MRN": clinical_id,
                          "workspace_id": workspace_id,
                          "metadata_json_file": upload_metadata_json_file.read() if upload_metadata_json_file is not None else None}

    # Init client
    CONF_FILE_PATH = 'mescobrad_edge/edge_module.config'
    PLUGIN_CONF_MAIN_SECTION = 'edge-module-configuration'
    config = configparser.ConfigParser()
    config.read(CONF_FILE_PATH)
    s3 = boto3.resource('s3',
                        endpoint_url=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_URL_LOCAL"],
                        aws_access_key_id=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_ACCESS_ID_LOCAL"],
                        aws_secret_access_key=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_ACCESS_SECRET_LOCAL"],
                        config=Config(signature_version='s3v4'),
                        region_name=config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_REGION"])

    # Upload data
    obj_storage_bucket = config[PLUGIN_CONF_MAIN_SECTION]["OBJ_STORAGE_BUCKET_LOCAL"]

    # Create bucket if it is not created
    if s3.Bucket(obj_storage_bucket).creation_date is None:
            s3.create_bucket(Bucket=obj_storage_bucket)

    # Before uploading a new file, empty the folder if it is not empty
    objs = list(s3.Bucket(obj_storage_bucket).objects.filter(Prefix="actigraphy_data_tmp/", Delimiter="/"))
    if len(list(objs))>0:
        for obj in objs:
            s3.Bucket(obj_storage_bucket).objects.filter(Prefix=obj.key).delete()

    # Upload a provided file
    file_name = upload_actigraphy_file.filename
    # Remove any special character from the file_name
    file_name = re.sub(r'[^a-zA-Z0-9_]', '_', os.path.splitext(file_name)[0]) + ".csv"
    obj_name = "actigraphy_data_tmp/" + file_name
    file_content = upload_actigraphy_file.read()
    s3.Bucket(obj_storage_bucket).upload_fileobj(BytesIO(file_content), obj_name)

    # Start workflow
    workflow_id = "actiwatch_actigraphy_workflow"
    workflow_engine_singleton = WorkflowEngine(data_info=exchange_data_info)
    print(f"Request received.. executing workflow {workflow_id}")
    workflow_engine_singleton.execute_workflow(workflow_id=workflow_id)

    return None, 202

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
