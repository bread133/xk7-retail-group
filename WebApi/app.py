from fastapi import FastAPI, UploadFile
import time
import uvicorn
import json
from uuid import UUID

from Common.FaultException import Fault

app = FastAPI()
timestr = time.strftime("%Y%m%d-%H%M%S")


@app.get('/download/submission-file')
def get_submission_file(id_video: UUID):
    # достать из бд и показать в файле (какое расширение у submission file?)
    pass


def get_borrow_table(id_video: UUID):
    # достать из бд и показать в json-табличке
    pass


@app.post('/upload/to-database')
def upload_video_to_database(file: UploadFile):
    if file == None:
        raise Fault.validation_fault('load file is empty')
    # upload from client
    data = json.loads(file.file.read())
    # validation
    # create castVideo
    return {'content': data, 'filename': file.filename}


@app.post('/upload/to-cast')
def upload_video_to_cast(file: UploadFile):
    pass


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)
