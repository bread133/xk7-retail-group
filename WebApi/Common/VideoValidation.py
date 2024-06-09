from fastapi import UploadFile

from WebApi.Common.FaultException import Fault

class ValidationResult:
    fault: Fault
    file: UploadFile

def FileValidation(file: UploadFile):
    validation_result = file.validate('multipart/form-data')
    if not validation_result:
        # TODO: DEBUG
        raise Fault.validation_fault(validation_result.error.message)
    filename = file.filename
    index = filename.index('.')
    title = filename[:index]
    extension = filename[index:]
    if extension is not 'mp4':
        raise Fault.validation_fault(f'{extension} extension of file is incorrect')



