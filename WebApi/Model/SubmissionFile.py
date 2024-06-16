from typing import List


class SubmissionFile:
    id_license: int
    id_piracy: List[int]
    time_license_start: List[int]
    time_license_finish: List[int]
    time_piracy_start: List[int]
    time_piracy_finish: List[int]

    def __init__(self):
        pass

    def to_csv(self):
        pass
