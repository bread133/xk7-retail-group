from collections import defaultdict
from bisect import bisect_left
from db_service import DBService
from default_logger import logger


def merge_sequence(duration_list: list[tuple[int, int, int]], value: tuple[int, int, int], idx_start: int, idx_end: int):
    
    left_value = min(duration_list[idx_start][0], value[0])
    right_value = max(duration_list[idx_end - 1][1], value[1])

    duration = duration_list[idx_end - 1][2]
    if duration_list[idx_end - 1][1] - duration_list[idx_start][0] < value[1] - value[0]:
        duration = value[2]

    duration_list[idx_start] = (left_value, right_value, duration)

    if idx_end > idx_start + 1:
        del duration_list[idx_start + 1:idx_end]


def add_duration(duration_list: list[tuple[int, int, int]], value: tuple[int, int, int], max_distance=1):

    if not duration_list:
        duration_list.append(value)
        return

    idx_start = bisect_left(duration_list, value[0], key=lambda item: item[0])
    idx_end = bisect_left(duration_list, value[1], lo=idx_start, key=lambda item: item[1])

    if idx_start > 0 and value[0] - duration_list[idx_start - 1][1] <= max_distance:
        idx_start -= 1
    if idx_end < len(duration_list) and duration_list[idx_end][0] - value[1] <= max_distance:
        idx_end += 1

    if idx_start == idx_end:
        duration_list.insert(idx_start, value)
    else:
        merge_sequence(duration_list, value, idx_start, idx_end)

    if idx_start > 0 and duration_list[idx_start][0] - duration_list[idx_start - 1][1] <= max_distance:
        merge_sequence(duration_list, duration_list[idx_start], idx_start - 1, idx_start + 1)
    if idx_start < len(duration_list) - 1 and duration_list[idx_start + 1][0] - duration_list[idx_start][1]\
            <= max_distance:
        merge_sequence(duration_list, duration_list[idx_start], idx_start, idx_start + 2)


def find_durations(dict_audio: dict[list[tuple[int, int]]], max_diff_s=1, min_duration_s=10)\
        -> dict[int, list[tuple[int, int, int]]]:

    result_dict = defaultdict(list[tuple[int, int, int]])

    for id_content, values in dict_audio.items():

        duration_list = []
        data_duration = defaultdict(list)

        for time1, time2 in values:
            diff = int((time2 - time1) // 1000)
            data_duration[diff].append(time1)

        for diff_local, times in data_duration.items():

            duration_list_local = []

            if len(times) < 2:
                continue

            logger.debug(f'count: {len(times)}\n{diff_local}: {times}')
            
            count = 0
            i = 0
            while i < len(times):
                j = i
                while j < len(times) - 1:
                    if (times[j + 1] - times[j]) // 1000 > max_diff_s:
                        break
                    j += 1
                if j - i > 2:
                    new_diff_local = int(diff_local)
                    if times[i] // 1000 + int(diff_local) < 0:
                        new_diff_local += 1
                    
                    add_duration(duration_list_local, (times[i] // 1000, times[j] // 1000, new_diff_local),
                                 max_diff_s)
                    count += j - i

                i = j + 1

            for tuple_value in duration_list_local:
                if tuple_value[1] - tuple_value[0] >= min_duration_s:
                    add_duration(duration_list, tuple_value, 5)

        if duration_list:
            result_dict[str(id_content)] = duration_list

    return result_dict


def detect_audio(hashes_: list[tuple[str, int]], duration_audio, db_service_: DBService, max_diff_s=3, min_duration_s=10) -> dict[int, list[tuple[int, int, int]]]:

    result_hashes = db_service_.get_audio_snapshots_by_hashes([values[0] for values in hashes_])

    hash_table = defaultdict(int)
    for hash_value, timestamp in hashes_:
        hash_table[hash_value] = timestamp

    dict_audio = defaultdict(list)
    for id_content, timestamp, hash_value in result_hashes:
        dict_audio[id_content].append((timestamp, hash_table[hash_value]))

    result_dict = find_durations(dict_audio, max_diff_s=max_diff_s, min_duration_s=min_duration_s)
    
    for id_content, values in result_dict.items():
        if values[0][0] <= 5:
            values[0] = (0, values[0][1], values[0][2])
            
        if duration_audio - values[len(values) - 1][1] <= 5:
            values[len(values) - 1] = (values[len(values) - 1][0], duration_audio, values[len(values) - 1][2])
        
        values[:] = [values_tuple for values_tuple in values if values_tuple[1] - values_tuple[0] > min_duration_s]
        
    return result_dict
