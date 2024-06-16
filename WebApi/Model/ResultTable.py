from typing import List


class ResultFile:
    title_license: str
    title_piracy: List[str]
    time_license_start: List[int]
    time_license_finish: List[int]
    time_piracy_start: List[int]
    time_piracy_finish: List[int]

    def __init__(self):
        pass


