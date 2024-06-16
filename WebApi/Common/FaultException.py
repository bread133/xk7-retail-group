import string
from fastapi import HTTPException

from Common.HttpStatusCodes import HttpStatusErrorCode

class Fault(HTTPException):
    code: int
    message: string

    def __init__(self):
        self.code = HttpStatusErrorCode.InternalServerError
        self.message = 'Unknown message has throw'
        super.__init__(self.message)

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super.__init__(self.message)

    def __str__(self):
        return f"Fault(code={self.code}, message={self.message})"

    @staticmethod
    def bad_request_fault(message: str):
        return Fault(HttpStatusErrorCode.BadRequest, message)