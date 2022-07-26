import uuid
from datetime import datetime
import json

import importlib.util
import sys
from threading import Thread, Lock

from mescobrad_edge.workflow_engine.models.executor import Executor
from mescobrad_edge.models.workflow_run import WorkflowRun

PLUGIN_FOLDER = 'mescobrad_edge/plugins'
WORKFLOW_FOLDER = 'mescobrad_edge/workflows'

workflow_mutexes = {}

def workflow_thread_func(workflow, run_info):
    print(f"Starting a new run for workflow {workflow.id} with id {run_info.id}")
    
    exchange_info = None
    
    # Iterate over the operations
    for operation in workflow.operations:
        print(f"Starting operation {operation.id} with name {operation.name}")

        plugin_id = operation.plugin_id
        plugin_path = f"{PLUGIN_FOLDER}/{plugin_id}".replace('-','_')

        # Read entrypoint file name
        with open(f"{plugin_path}/plugin.info.json", 'r') as plugin_info_file:
            plugin_info_json = json.loads(plugin_info_file.read())
            entry_point = plugin_info_json["entry-point"]
        
        # Dynamically load entrypoint
        print(f"Loading {entry_point} (entrypoint) for plugin {plugin_id} located at {plugin_path}")

        spec = importlib.util.spec_from_file_location(entry_point, f"{plugin_path}/{entry_point}")

        plugin = importlib.util.module_from_spec(spec)
        sys.modules[entry_point] = plugin
        spec.loader.exec_module(plugin)
        plugin_instance = plugin.GenericPlugin()

        # Get workflow mutex (if not exist create it)
        if workflow.id in workflow_mutexes.keys():
            workflow_mutex = workflow_mutexes[workflow.id]
        else:
            workflow_mutex = Lock()
            workflow_mutexes[workflow.id] = workflow_mutex

        # Update workflow run file
        with workflow_mutex:
            # Read entrypoint file name
            workflow_path = f"{WORKFLOW_FOLDER}/{workflow.name}".replace('-','_')
            workflow_process_json = None
            with open(f"{workflow_path}/.run", 'r') as workflow_process_file:
                workflow_process_json = json.loads(workflow_process_file.read())
            
            for idx in range(len(workflow_process_json['run_info'])):
                run_info = workflow_process_json['run_info'][idx]
                if run_info['id'] == workflow.id:
                    run_info['status'] = operation.id
                    workflow_process_json['run_info'][idx] = run_info

            with open(f"{workflow_path}/.run", 'w') as workflow_process_file:
                workflow_process_file.write(json.dumps(workflow_process_json))

        # Execute plugin
        exchange_info = plugin_instance.__execute__(exchange_info)

    # Update workflow run file
    return 0

class WorkflowDefaultExecutor(Executor):
    def run(self, workflow):
        run_info = WorkflowRun(id=uuid.uuid4(), ts=datetime.now().strftime("%m/%d/%Y %H:%M:%S"), status='CREATED')

        # Create a new thread
        p = Thread(target=workflow_thread_func, args=(workflow, run_info))
        p.start()

        return p, run_info