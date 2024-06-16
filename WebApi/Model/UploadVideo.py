import secrets
import uuid
import os

from fastapi import UploadFile

class UploadVideo:
    id: uuid
    title: str
    extension: str
    filename_hex: str
    path: str

    def __init__(self, title: str, extension: str):
        self.id = uuid.uuid4()
        self.title = title
        self.extension = extension
        self.filename_hex = secrets.token_hex(16)
        self.path = f"{os.getcwd()}\\WebApi\\VideoContainer\\{self.filename_hex}{extension}"

    async def load_video_to_server(self, file: UploadFile):
        with open(self.path, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"success": True, "filepath": self.path, "message": "File saved successfully"}
