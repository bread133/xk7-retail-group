import uuid
from typing import Any

from pydantic import BaseModel, ConfigDict
import datetime
from enum import Enum
import pytz
import json

from Common.FaultException import Fault
from Model.BaseOperation import BaseOperation


class OperationType(Enum):
    Unknown = 0
    LoadVideoToSubFile = 1,
    LoadVideoToDatabase = 2,
    GetSubFile = 3,
    GetDataTable = 4


class OperationStatus(Enum):
    Unknown = 0,
    InProcess = 1,
    Done = 2,
    Die = 3


class OperationInfo:
    id: uuid
    create_at: datetime
    op_type: OperationType
    status: OperationStatus
    change_at: datetime
    success: bool
    fault: Fault
    content: BaseOperation

    def __init__(self, op_type=OperationType.Unknown, status=OperationStatus.Unknown):
        self.id = uuid.uuid4()
        self.create_at = get_msk_time()
        self.op_type = op_type
        self.status = status
        self.change_at = get_msk_time()
        self.success = True
        self.fault = None

    def change_status(self, status: OperationStatus):
        self.status = status
        self.change_at = get_msk_time()

    def change_type(self, op_type):
        self.op_type = op_type
        self.change_at = get_msk_time()

    def set_fault(self, fault: Fault):
        self.success = False
        self.fault = fault
        self.status = OperationStatus.Die
        self.change_at = get_msk_time()

    def to_json(self, content):
        operation_info_to_serialize = OperationInfoToSerialize(
            id=str(self.id), create_at=str(self.create_at),
            op_type=str(self.op_type), status=str(self.status),
            change_at=str(self.change_at), success=str(self.success),
            fault=str(self.fault), content=str(content)
        )
        return operation_info_to_serialize.json()

    def __str__(self):
        return (
            f"id = {self.id}, create_at = {self.create_at}, "
            f"op_type = {self.op_type}, status = {self.status}, "
            f"change_at = {self.change_at}, success = {self.success}, content={self.content}")


class OperationInfoToSerialize(BaseModel):
    model_config = ConfigDict(extra='allow')

    id: str
    create_at: str
    op_type: str
    status: str
    change_at: str
    success: str
    fault: str
    content: str


def get_msk_time():
    return datetime.datetime.now(pytz.timezone("Etc/GMT+3"))
