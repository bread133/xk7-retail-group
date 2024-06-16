import os
from typing import List

from pydantic import ValidationError
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from uuid import UUID

from Algorithm.db_service import DBService
from Algorithm.db_utilities import load_config
from Common.FaultException import Fault
from Common.FileValidation import video_validation
from Model.OperationInfo import *
from Model.UploadVideo import UploadVideo
from Algorithm.upload_all_audio_to_db import create_fingerprint_audio, create_and_load_fingerprint_audio

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


@app.post('/api/files')
async def upload_video_to_create_fingerprint(file: List[UploadFile] = File(...)):
    try:
        if file is None:
            raise Fault.bad_request_fault('load file is empty')
        # validation
        for _file in file:
            video_validation_result = video_validation(_file)
            result_value: UploadVideo = video_validation_result.upload_video
            result_of_loading_to_server = await result_value.load_video_to_server(_file)
        operation_info = OperationInfo(OperationType.LoadVideoToSubFile, OperationStatus.InProcess)
        # create fingerprint into video
        fingerprint = create_fingerprint_audio(result_value.path)
        # TODO: sopostavlenie sdelayte sami
        # TODO: add to db and return uploadVideo in json
        operation_info.change_status(OperationStatus.Done)
    except ValidationError as e:
        operation_info.set_fault(Fault(400, e.json(result_value)))
    finally:
        # delete video after fingerprint creation
        if os.path.exists(video_validation_result.upload_video.path):
            os.remove(video_validation_result.upload_video.path)


        return JSONResponse(operation_info.to_json(result_value))


# ready
@app.post('/api/filesOriginal')
async def upload_video_to_database(file: List[UploadFile] = File(...)):
    try:
        if file is None:
            raise Fault.bad_request_fault('load file is empty')
        # validation
        for _file in file:
            video_validation_result = video_validation(_file)
            result_value: UploadVideo = video_validation_result.upload_video
            await result_value.load_video_to_server(_file)
        operation_info = OperationInfo(OperationType.LoadVideoToDatabase, OperationStatus.InProcess)
        # create fingerprint into video and add to db
        fingerprint = create_fingerprint_audio(result_value.path)
        operation_info.change_status(OperationStatus.Done)
    except ValidationError as e:
        operation_info.set_fault(Fault(400, e.json(result_value)))
    finally:
        # delete video after fingerprint creation
        if os.path.exists(video_validation_result.upload_video.path):
            os.remove(video_validation_result.upload_video.path)
        return JSONResponse(operation_info.to_json(result_value))


if __name__ == '__main__':
    config = load_config()
    db_service = DBService(1, 5, config)
    uvicorn.run('app:app', host='127.0.0.1', port=8001)
