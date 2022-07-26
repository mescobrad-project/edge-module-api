import os
import json

WORKFLOW_DIR = "mescobrad_edge/workflows"

class WorkflowValidator():
    def validate(self, workflow_id):
        print(f"Validating workflow {workflow_id}")
        
        process_file = None
        run_file = None
        config_file = None
        
        with open(f"{WORKFLOW_DIR}/{workflow_id}/process.json", 'r') as p:
            process_file = p.read()

        with open(f"{WORKFLOW_DIR}/{workflow_id}/.run", 'r') as r:
            run_file = r.read()

        if not os.path.isdir(f"{WORKFLOW_DIR}/{workflow_id}/.config"):
            return False

        with open(f"{WORKFLOW_DIR}/{workflow_id}/.config/workflow.config", 'r') as c:
            config_file = c.read()

        return self.__validate_process__(json.loads(process_file)) and \
               self.__validate_run_file__(json.loads(run_file)) and \
               self.__validate_config_file__(config_file)

    def __validate_process__(self, workflow_process_json):
        return self.__validate_outer_structure__(workflow_process_json) and \
               self.__validate_operations__(workflow_process_json)
    
    def __validate_outer_structure__(self, workflow_process_json):
        return all(elem in workflow_process_json.keys() for elem in ["id", "name", "operations"]) and \
               isinstance(workflow_process_json["operations"], list)

    def __validate_operations__(self, workflow_process_json):
        for operation in workflow_process_json["operations"]:
            if not all(elem in operation.keys() for elem in ["id", "name", "description", "plugin_id"]) :
                return False
        return True

    def __validate_run_file__(self, run_file_json):
        return all(elem in run_file_json.keys() for elem in ["last_execution", "run_info"])  and \
               isinstance(run_file_json["run_info"], list)

    def __validate_config_file__(self, config_file):
        return True