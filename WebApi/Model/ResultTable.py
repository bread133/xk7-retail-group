from typing import List
from pydantic import BaseModel
from varname import nameof

class IVideoBorrowing(BaseModel):
    title_license: str
    title_piracy: str
    time_license_start: int
    time_license_finish: int
    time_piracy_start: int
    time_piracy_finish: int

    def __str__(self):
        return (f"{nameof(self.title_license)}: {self.title_license},\n"
                f"")


class IResponseServerUploadFiles(BaseModel):
    message: str
    status: int
    borrowing: List[IVideoBorrowing]

    def __str__(self):
        return (f"{nameof(self.message)}: {self.message},\n"
                f"{nameof(self.status)}: {self.status},\n"
                f"{nameof(self.borrowing)}: {self.borrowing}")



def to_json(upload_files_response: IResponseServerUploadFiles):
    upload_files_response.json()
