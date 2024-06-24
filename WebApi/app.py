import os
from typing import List

from pydantic import ValidationError
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from Algorithm.db_service import DBService
from Algorithm.db_utilities import load_config
from Common.FaultException import Fault
from Common.FileValidation import video_validation
from Common.HttpStatusCodes import HttpStatusSuccessfulCode
from Model.OperationInfo import *
from Model.UploadVideo import UploadVideo
from Algorithm.upload_all_audio_to_db import create_fingerprint_audio, create_and_load_fingerprint_audio, \
    match_audio_fingerprint
from Algorithm.db_service import DBService
from Model.ResultTable import IResponseServerUploadFiles, IVideoBorrowing

# TODO: solve import with Algorithm import

app = FastAPI()

config = load_config()
db_service = DBService(1, 5, config)

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
            await result_value.load_video_to_server(_file)
        operation_info = OperationInfo(OperationType.LoadVideoToSubFile, OperationStatus.InProcess)

        # create list of dictionary
        result_audio_matching = match_audio_fingerprint(result_value.path, db_service)

        video_borrowing_dictionary: List[IVideoBorrowing] = []
        for result_audio_matching_item in result_audio_matching:
            id_piracy = int(result_audio_matching_item)
            title_piracy = DBService.get_content_by_id(db_service, id_piracy)[0]
            for result_audio_matching_tuple in result_audio_matching[result_audio_matching_item]:
                time_license_start = result_audio_matching_tuple[0]
                time_license_finish = result_audio_matching_tuple[1]
                diff = result_audio_matching_tuple[2]
                video_borrowing_dictionary.append(IVideoBorrowing(title_license=title_piracy, title_piracy=result_value.title + result_value.extension, time_license_start=time_license_start, time_license_finish=time_license_finish, time_piracy_start=time_license_start + diff, time_piracy_finish=time_license_finish + diff))

        json = IResponseServerUploadFiles(message="matching is successful", status=HttpStatusSuccessfulCode.Ok, borrowing=video_borrowing_dictionary).model_json_schema()
        operation_info.change_status(OperationStatus.Done)

        if os.path.exists(video_validation_result.upload_video.path):
            os.remove(video_validation_result.upload_video.path)

        dump_json = json.dumps(json, indent=2)
        return JSONResponse(dump_json)

    except ValidationError as e:
        operation_info.set_fault(Fault(400, e.json(result_value)))
        # delete video after fingerprint creation
        if os.path.exists(video_validation_result.upload_video.path):
            os.remove(video_validation_result.upload_video.path)

        return JSONResponse(operation_info.to_json(result_value))
    except Exception as e:
        operation_info.set_fault(Fault(400, e.json(result_value)))
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
        create_and_load_fingerprint_audio(result_value.title + result_value.extension, result_value.path, db_service)
        operation_info.change_status(OperationStatus.Done)
    except ValidationError as e:
        operation_info.set_fault(Fault(400, e.json(result_value)))
    except Exception as e:
        operation_info.set_fault(Fault(400, e.json()))
    finally:
        # delete video after fingerprint creation
        if os.path.exists(video_validation_result.upload_video.path):
            os.remove(video_validation_result.upload_video.path)
        return JSONResponse(operation_info.to_json(result_value))


if __name__ == '__main__':
    uvicorn.run('app:app', host='127.0.0.1', port=8001)
