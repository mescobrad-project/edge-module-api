from threading import Lock

WORKFLOW_FOLDER_PATH = 'workflows'
workflow_mutexes = {}

def get_mutex_from_workflow_id(workflow_id):
    if workflow_id in workflow_mutexes.keys():
        workflow_mutex = workflow_mutexes[workflow_id]
    else:
        workflow_mutex = Lock()
        workflow_mutexes[workflow_id] = workflow_mutex
    
    return workflow_mutex