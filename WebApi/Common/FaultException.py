import string
from HttpStatusCodes import HttpStatusErrorCode

class Fault(Exception):
    code: int
    message: string

    def __init__(self):
        self.code = HttpStatusErrorCode.InternalServerError
        self.message = 'Unknown message has throw'
        super.__init__(self.message)

    def __init__(self, code, message):
        self.code = code
        self.message = message

    @staticmethod
    def validation_fault(message: str):
        return Fault(HttpStatusErrorCode.BadRequest, message)