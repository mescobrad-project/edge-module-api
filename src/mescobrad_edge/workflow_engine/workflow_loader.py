import os
import json

from mescobrad_edge.workflow_engine.models.loader import Loader


WORKFLOW_DIR = "mescobrad_edge/workflows"

class WorkflowDefaultLoader(Loader):

    def load_workflow(self, workflow_id: int):
        process = None
        print(f"Opening file {WORKFLOW_DIR}/{workflow_id}/process.json")
        with open(f"{WORKFLOW_DIR}/{workflow_id}/process.json", 'r') as process_file:
            process = process_file.read()
        return process

    def save_run_info(self, workflow_id:int, run_info):
        print(f"Updating file {WORKFLOW_DIR}/{workflow_id}/.run")
        run_file_json = None
        with open(f"{WORKFLOW_DIR}/{workflow_id}/.run", 'r') as run_file:
            run_file_json = json.loads(run_file.read())
            run_file_json['last_execution'] = run_info.ts
            run_file_json['run_info'].insert(0, {'id': str(run_info.id), 'ts': run_info.ts, 'status': run_info.status})
        with open(f"{WORKFLOW_DIR}/{workflow_id}/.run", 'w') as run_file:
            run_file.write(json.dumps(run_file_json))



    def check_if_present(self, workflow_id:int):
        print(f"Checking path {WORKFLOW_DIR}/{workflow_id}")
        return os.path.isdir(f"{WORKFLOW_DIR}/{workflow_id}")