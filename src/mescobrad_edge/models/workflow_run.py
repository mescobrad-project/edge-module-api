import json

class WorkflowRun():
    def __init__(self, id, ts, status) -> None:
        self._id = id
        self._ts = ts
        self._status = status
    
    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, id: str):
        self._id = id

    @property
    def ts(self) -> str:
        return self._ts

    @ts.setter
    def ts(self, ts: str):
        self._ts = ts

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, status: str):
        self._status = status