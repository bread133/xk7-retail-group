from typing import List
from pydantic import BaseModel


class IVideoBorrowing(BaseModel):
    title_license: str
    title_piracy: str
    time_license_start: int
    time_license_finish: int
    time_piracy_start: int
    time_piracy_finish: int


class IResponseServerUploadFiles(BaseModel):
    message: str
    status: int
    borrowing: List[IVideoBorrowing]


def to_json(upload_files_response: IResponseServerUploadFiles):
    upload_files_response.json()
