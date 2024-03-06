from typing import Dict
from mescobrad_edge.workflow_engine.workflow_serde import WorkflowDefaultSerde

from mescobrad_edge.workflow_engine.workflow_validator import WorkflowValidator
from mescobrad_edge.workflow_engine.workflow_loader import WorkflowDefaultLoader
from mescobrad_edge.workflow_engine.workflow_executor import WorkflowDefaultExecutor

import os
import json
from mescobrad_edge.singleton import ROOT_DIR
from mescobrad_edge.workflow_engine.workflow_singleton import WORKFLOW_FOLDER_PATH

class WorkflowEngine():

    def __init__(self, serde=None, loader=None, executor=None, data_info=None):
        self.__serde__ = WorkflowDefaultSerde() if serde is None else serde()
        self.__validator__ = WorkflowValidator()
        self.__loader__ = WorkflowDefaultLoader() if loader is None else loader()
        self.__executor__ = WorkflowDefaultExecutor() if executor is None else executor()
        self.__data_info__ = data_info

    def execute_workflow(self, workflow_id: str) -> str:
        # Check if workflow exists
        workflow_exists = self.__check_workflow__(workflow_id)
        if workflow_exists:
            # Check if workflow is valid
            workflow_is_valid = self.__validate_workflow__(workflow_id)
            if workflow_is_valid:
                # Load workflow from file system and deserialize it
                workflow = self.__serde__.deserialize(self.__loader__.load_workflow(workflow_id=workflow_id))
                # Execute workflow
                workflow_thread, workflow_run_info = self.__executor__.run(workflow, data_info=self.__data_info__)
                # Save run info
                self.__loader__.save_run_info(workflow_id=workflow_id, run_info=workflow_run_info)

                workflow_thread.start()
                # Make it sync
                # workflow_thread.join()

                return workflow_run_info.id
            else:
                print(f"Workflow {workflow_id} is not a valid workflow")
        else:
            print(f"Workflow {workflow_id} does not exist on this system")
        return None

    def __check_workflow__(self, workflow_id: str) -> bool:
        return self.__loader__.check_if_present(workflow_id)

    def __validate_workflow__(self, workflow_id: str) -> bool:
        return self.__validator__.validate(workflow_id)

    def get_existent_workflows(self):
        """Returns list of existent workflow folders"""
        existent_workflow_folders = [ '/'.join(f.path.split(WORKFLOW_FOLDER_PATH)[1:]) for f in os.scandir(ROOT_DIR + '/' + WORKFLOW_FOLDER_PATH) if f.is_dir() ]
        return existent_workflow_folders

    def list_workflows(self):
        """List existing workflows"""
        workflows_list = {}
        # List folder within workflows folder
        WORKFLOW_INFO_FILE = "process.json"
        existent_workflow_folders =self.get_existent_workflows()
        for workflow in existent_workflow_folders:
            workflow_info = {}
            with open(f"{ROOT_DIR}/{WORKFLOW_FOLDER_PATH}{workflow}" + "/" + WORKFLOW_INFO_FILE, 'r') as workflow_info_file:
                workflow_info = json.load(workflow_info_file)
                workflows_list[workflow] = workflow_info
        return workflows_list

    def get_workflow_info(self, workflow_id):
        """For specified workflow_id returns informations about workflow"""
        WORKFLOW_INFO_FILE = "process.json"
        existent_workflow_folders = self.get_existent_workflows()
        workflow_info = None
        for workflow in existent_workflow_folders:
            with open(f"{ROOT_DIR}/{WORKFLOW_FOLDER_PATH}{workflow}" + "/" + WORKFLOW_INFO_FILE, 'r') as workflow_info_file:
                workflow_current_info = json.load(workflow_info_file)
                if workflow_current_info["id"] == workflow_id:
                    workflow_info = workflow_current_info
        return workflow_info