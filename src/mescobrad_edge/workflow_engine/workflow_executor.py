import uuid
from datetime import datetime
import json

import importlib.util
import sys
from threading import Thread, Lock

from mescobrad_edge.workflow_engine.models.executor import Executor
from mescobrad_edge.models.workflow_run import WorkflowRun

from mescobrad_edge.singleton import ROOT_DIR, PLUGIN_FOLDER_PATH as PLUGIN_FOLDER
from mescobrad_edge.workflow_engine.workflow_singleton import WORKFLOW_FOLDER_PATH as WORKFLOW_FOLDER, get_mutex_from_workflow_id

class WorkflowThread():

    def __init__(self, workflow, run_info) -> None:
        self.__workflow__ = workflow
        self.__run_info__ = run_info

    def run(self):
        print(f"Starting a new run for workflow {self.__workflow__.id} with id {self.__run_info__.id}")

        exchange_info = None
        # Iterate over the operations
        for operation in self.__workflow__.operations:
            exchange_info = self.__run_operation__(operation, exchange_info)
        return 0

    def __run_operation__(self, operation, exchange_info):
        print(f"Starting operation {operation.id} with name {operation.name}")
        plugin_id = operation.plugin_id
        plugin_path = f"{ROOT_DIR}/{PLUGIN_FOLDER}/{plugin_id.replace('-','_')}"
        plugin_entry_point = self.__get_entry_point_name__(plugin_path)

        # Dynamically load entrypoint
        print(f"Loading {plugin_entry_point} (entrypoint) for plugin {plugin_id} located at {plugin_path}")
        plugin_instance = self.__get_plugin_instance__(plugin_path, plugin_entry_point)
        workflow_mutex = get_mutex_from_workflow_id(self.__workflow__.id)

        # Update workflow run file
        with workflow_mutex:
            # Read entrypoint file name
            workflow_path = f"{ROOT_DIR}/{WORKFLOW_FOLDER}/{(self.__workflow__.name).replace('-','_')}"
            workflow_process_json = self.__open_workflow_run_file__(workflow_path, 'r', lambda file_content: json.loads(file_content.read()))
            workflow_process_json = self.__overwrite_run_info_status__(workflow_process_json, operation)

            self.__open_workflow_run_file__(workflow_path, 'w', lambda file_content: file_content.write(json.dumps(workflow_process_json)))

        # Execute plugin
        exchange_info = plugin_instance.__execute__(exchange_info)
        return exchange_info


    def __get_entry_point_name__(self, plugin_path):
        entry_point = None
        # Read entrypoint file name
        with open(f"{plugin_path}/plugin.info.json", 'r') as plugin_info_file:
            plugin_info_json = json.loads(plugin_info_file.read())
            entry_point = plugin_info_json["entry-point"]

        return entry_point

    def __get_plugin_instance__(self, plugin_path, entry_point):
        spec = importlib.util.spec_from_file_location(entry_point, f"{plugin_path}/{entry_point}")

        plugin = importlib.util.module_from_spec(spec)
        sys.modules[entry_point] = plugin
        spec.loader.exec_module(plugin)
        return plugin.GenericPlugin()

    def __open_workflow_run_file__(self, workflow_path, mode, func):
        # if mode = 'w' return None, otherwise return the content of the file
        with open(f"{workflow_path}/.run", mode) as workflow_process_file:
                content = func(workflow_process_file)
        if mode == 'w':
            return None
        else:
            return content

    def __overwrite_run_info_status__(self, workflow_process_json, operation):
        for idx in range(len(workflow_process_json['run_info'])):
            run_info_json = workflow_process_json['run_info'][idx]
            if str(run_info_json['id']) == str(self.__run_info__.id):
                run_info_json['status'] = operation.id
                workflow_process_json['run_info'][idx] = run_info_json
                break
        return workflow_process_json



class WorkflowDefaultExecutor(Executor):
    def run(self, workflow):
        run_info = WorkflowRun(id=uuid.uuid4(), ts=datetime.now().strftime("%m/%d/%Y %H:%M:%S"), status='CREATED')

        # Create a new thread
        p = Thread(target=WorkflowThread(workflow, run_info).run)

        return p, run_info