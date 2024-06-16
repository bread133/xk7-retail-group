import os
from typing import List

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uuid import UUID

from Common.FaultException import Fault
from Common.FileValidation import FileValidation, video_validation
from Model.OperationInfo import *

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/download-submission-file')
async def get_submission_file(id_video: UUID):
    # достать из бд и показать в файле (какое расширение у submission file?)
    pass


@app.get('/show-fingerprint')
async def get_borrow_table(id_video: UUID):
    # достать из бд и показать в json-табличке
    pass


@app.post('/api/files')
async def upload_video_to_create_fingerprint(file: List[UploadFile] = File(...)):
    if file is None:
        raise Fault.validation_fault('load file is empty')
    # validation
    for _file in file:
        video_validation_result = video_validation(_file)
        result_value = await video_validation_result.upload_video.load_video_to_server(_file)
    operation_info = OperationInfo(OperationType.LoadVideoToSubFile, OperationStatus.InProcess)
    # TODO: create fingerprint into video
    # TODO: sopostavlenie
    # TODO: add to db and return uploadVideo in json
    operation_info.change_status(OperationStatus.Done)
    # delete video after fingerprint creation
    if os.path.exists(video_validation_result.upload_video.path):
        os.remove(video_validation_result.upload_video.path)
    return JSONResponse(operation_info.to_json())


@app.post('/api/filesOriginal')
async def upload_video_to_database(file: List[UploadFile] = File(...)):
    if file is None:
        raise Fault.validation_fault('load file is empty')
    # validation
    for _file in file:
        video_validation_result = video_validation(_file)
        result_value = await video_validation_result.upload_video.load_video_to_server(_file)
    operation_info = OperationInfo(OperationType.LoadVideoToDatabase, OperationStatus.InProcess)
    # TODO: create fingerprint into video
    # TODO: sopostavlenie
    # TODO: add to db and return uploadVideo in json
    operation_info.change_status(OperationStatus.Done)
    # delete video after fingerprint creation
    if os.path.exists(video_validation_result.upload_video.path):
        os.remove(video_validation_result.upload_video.path)
    return JSONResponse(operation_info.to_json())


if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8001)
