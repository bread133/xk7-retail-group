from collections import defaultdict
from bisect import bisect_left
from db_service import DBService
from default_logger import logger


def merge_sequence(duration_list: list[tuple[int, int, int]], value: tuple[int, int, int], idx_start: int, idx_end: int):
    """
    Выполняет соединение последовательности с новым элементом (если есть пересечение). 

    :param duration_list: список-кортежей (начало совпадения из БД, конец совпадения из БД, смещение для определения локального времени).
    :param value: кортеж, который необходимо соединить с некоторой последовательностью.
    :param idx_start: индекс начала последовательности.
    :param idx_end: индекс конца последовательности.
    """
     
    left_value = min(duration_list[idx_start][0], value[0])
    right_value = max(duration_list[idx_end - 1][1], value[1])

    duration = duration_list[idx_end - 1][2]
    if duration_list[idx_end - 1][1] - duration_list[idx_start][0] < value[1] - value[0]:
        duration = value[2]

    duration_list[idx_start] = (left_value, right_value, duration)

    if idx_end > idx_start + 1:
        del duration_list[idx_start + 1:idx_end]


def add_duration(duration_list: list[tuple[int, int, int]], value: tuple[int, int, int], max_distance=1):
    """
    Выполняет добавление нового промежутка (value) в список промежутков, которые не пересекаются, а также,
    расстояние между границами, больше чем max_distance. После добавления нового промежутка свойства списка сохрананяются.
    
    :param duration_list: список промежутков, представлен в виде списка-кортежей, где элементы:
        начало совпадения из БД, конец совпадения из БД, смещение для определения локального времени.
    :param value: промежуток в виде кортежа для добавления в список.
    :param max_distance: максимальное расстояние между границами для выполнения их объединения (в секундах).
    """

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
    """
    Выполняет поиск промежутков совпадения.
    Идея: ранжировать время по разности локального и удаленного времени.
    Ранжирование происходит в словаре data_duration.
    Ключ это разность локального и удаленного времени, а значение это список удаленных времен.
    Тогда для каждого ключа есть список, где времена совпадения в порядке возрастения в МС.
    В таком случае необходимо найти все подпоследовательности, где разность не больше max_diff_s
    и выполнить их объединения с другими промежутками, если их разность соседних границ не больше max_diff_s.
    Итоговые последовательности должны быть не меньше min_duration_s.
    
    :param dict_audio: словарь аудио совпадений из БД, где ключ - id контента, а значение - список в виде кортежа времен, у которых совпали хеши,
        первый элемент кортежа - время из БД, второй - время локального аудиофрагмента.
    :param max_diff_s: максимальное расстояние между границами для выполнения их объединения (в секундах).
    :param min_duration_s: длительность минимального промежука совпадения (в секундах).
    :result: промежутки совпадения в виде словаря, где ключ - id контента, а значение - список совпадений в виде
        кортежа: начало совпадения из БД, конец совпадения из БД, смещение для определения локального времени.
    """

    result_dict = defaultdict(list[tuple[int, int, int]])

    for id_content, values in dict_audio.items():

        duration_list = []
        data_duration = defaultdict(list)

        # Ранжируем по разности time2 и time1
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
    """
    Определение совпадений аудио фрагмента из БД
    
    :param hashes_: хеши аудио фрагмента для поиска совпадений из БД.
    :param duration_audio: длительность аудио фрагмента (в секундах).
    :param db_service_: объект сервиса БД
    :param max_diff_s: максимальное расстояние между границами для выполнения их объединения (в секундах).
    :param min_duration_s: длительность минимального промежука совпадения (в секундах).
    
    :result: промежутки совпадения в виде словаря, где ключ - id контента, а значение - список совпадений в виде
        кортежа: начало совпадения из БД, конец совпадения из БД, смещение для определения локального времени.
    """

    result_hashes = db_service_.get_audio_snapshots_by_hashes([values[0] for values in hashes_])

    # Для быстрого поиска по хешу
    hash_table = defaultdict(int)
    for hash_value, timestamp in hashes_:
        hash_table[hash_value] = timestamp

    # Ранжируем по id_content
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
