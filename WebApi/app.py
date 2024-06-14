from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import time
import uvicorn
from uuid import UUID

from Common.FaultException import Fault
from Common.FileValidation import FileValidation, video_validation
from Model.UploadVideo import UploadVideo

app = FastAPI()
timestr = time.strftime("%Y%m%d-%H%M%S")


@app.get("/")
def root():
    return JSONResponse(content={"message": "Hello!"})


@app.get('/download-submission-file')
async def get_submission_file(id_video: UUID):
    # достать из бд и показать в файле (какое расширение у submission file?)
    pass

@app.get('/show-fingerprint')
async def get_borrow_table(id_video: UUID):
    # достать из бд и показать в json-табличке
    pass


@app.post('/upload-video/to-database')
async def upload_video_to_database(file: UploadFile = File(...)):
    if file == None:
        raise Fault.validation_fault('load file is empty')
    # validation
    file_validation = video_validation(file)
    upload_video_valid = file_validation.upload_video.load_video_to_server(file)
    # create fingerprint into video
    # add to db and return uploadVideo in json
    return JSONResponse(content={"success": True, "filepath": file_validation.upload_video.path, "message": "File upload successfully"})

@app.post('/upload-video/to-fingerprint')
async def upload_video_to_create_fingerprint(file: UploadFile):
    pass


if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8000)
