import uuid
from datetime import datetime

from swagger_server.workflow_engine.models.executor import Executor
from swagger_server.models.workflow_run import WorkflowRun

class WorkflowDefaultExecutor(Executor):
    def run(self, workflow):
        run_info = WorkflowRun(id=uuid.uuid4(), ts=datetime.now().strftime("%m/%d/%Y %H:%M:%S"), status='CREATED')
        
        return run_info