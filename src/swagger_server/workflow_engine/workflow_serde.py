from swagger_server.models.workflow import Workflow
from swagger_server.models.operation import Operation

from swagger_server.workflow_engine.models.serde import Serde

import json

class WorkflowDefaultSerde(Serde):
    def serialize(self, workflow: Workflow) -> Workflow :
        pass

    def deserialize(self, workflow: str) -> None :
        json_workflow = json.loads(workflow)
        return self.__serialization_hook__(json_workflow)

    def __serialization_hook__(self, json_obj):
        operation_list = list()
        for o in json_obj['operations']:
            operation = Operation(
                id=o['id'],
                name=o['name'],
                description=o['description'],
                plugin_id=o['plugin_id'],
            )
            operation_list.append(operation)

        return Workflow(
            id=json_obj['id'],
            name=json_obj['name'],
            operations=operation_list
        )