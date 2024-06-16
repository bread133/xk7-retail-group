from fastapi import UploadFile
from Common.FaultException import Fault
from Model.UploadVideo import UploadVideo


class FileValidation:
    fault: Fault
    file: UploadFile
    success: bool
    upload_video: UploadVideo

    def __init__(self, file: UploadFile, upload_video, success: bool = True, fault: Fault = None):
        self.file = file
        self.success = success
        self.fault = fault
        self.upload_video = upload_video


acceptable_extension: list = ['.mp4']


def video_validation(file: UploadFile) -> FileValidation:
    validation_result = (file.content_type != 'video/mp4')
    if validation_result:
        raise Fault.bad_request_fault("content type of upload file is incorrect")

    filename = file.filename
    index = filename.index('.')
    title = filename[:index]
    extension = filename[index:]
    if extension not in acceptable_extension:
        raise Fault.validation_fault(f'{extension} extension of file is incorrect')
    upload_video = UploadVideo(title, extension)

    return FileValidation(file, upload_video)
