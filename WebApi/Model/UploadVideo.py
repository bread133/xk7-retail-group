import secrets
import uuid
import os
from fastapi import UploadFile

from Model.BaseOperation import BaseOperation

class UploadVideo(BaseOperation):
    title: str
    extension: str
    filename_hex: str
    path: str
    result_of_loading: dict[str, str | bool]

    def __init__(self, title: str, extension: str):
        self.title = title
        self.extension = extension
        self.filename_hex = secrets.token_hex(16)
        self.path = f"{os.getcwd()}\\WebApi\\VideoContainer\\{self.filename_hex}{extension}"
        self.result_of_loading = None

        _id = uuid.uuid4()
        super = BaseOperation(_id)

    def __str__(self):
        return str(super)

    async def load_video_to_server(self, file: UploadFile):
        success = True
        message = "File saved successfully"
        try:
            with open(self.path, "wb") as f:
                content = await file.read()
                f.write(content)
            if not os.path.exists(self.path):
                success = False
                message = "Could not load file to server"
        except:
            success = False
            message = "Could not load file to server"
        finally:
            result_str = {"success": success, "filepath": self.path, "message": message}
            self.result_of_loading = result_str
            return result_str
