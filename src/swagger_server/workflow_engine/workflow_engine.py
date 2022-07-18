from swagger_server.workflow_engine.workflow_serde import WorkflowDefaultSerde

from swagger_server.workflow_engine.workflow_validator import WorkflowValidator
from swagger_server.workflow_engine.workflow_loader import WorkflowDefaultLoader
from swagger_server.workflow_engine.workflow_executor import WorkflowDefaultExecutor

class WorkflowEngine():

    def __init__(self, serde=None, loader=None, executor=None):
        self.__serde__ = WorkflowDefaultSerde() if serde is None else serde()
        self.__validator__ = WorkflowValidator()
        self.__loader__ = WorkflowDefaultLoader() if loader is None else loader()
        self.__executor__ = WorkflowDefaultExecutor() if executor is None else executor()

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
                workflow_run_info = self.__executor__.run(workflow)
                # Save run info
                self.__loader__.save_run_info(workflow_id=workflow_id, run_info=workflow_run_info)

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
