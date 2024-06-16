from uuid import UUID
from typing import Any
from varname import nameof


class BaseOperation:
    id: UUID

    def __init__(self, _id: UUID):
        self.id = _id

    def __str__(self):
        return f"id={self.id}"
