def hamming_distance(seq1, seq2):
    if len(seq1) != len(seq2):
        raise ValueError("Sequences must be of the same length")

    distance = 0
    for num1, num2 in zip(seq1, seq2):
        xor_result = num1 ^ num2
        distance += bin(xor_result).count('1')
    return distance


def find_video_duration(hashes_db: list[tuple[list[int]], int], hashes_local: list[tuple[list[int], int]], thresh,
                        max_diff_time, min_duration_time):
    durations = []

    len_min = min(len(hashes_db), len(hashes_local))

    for i in range(len_min - 1):

        if abs((hashes_db[i + 1][1] - hashes_db[i][1]) - (hashes_local[i + 1][1] - hashes_local[i][1])) > max_diff_time:
            continue

        start_time_db, start_time_local = hashes_db[i][1], hashes_local[i][1]

        old_i = i
        while i < len_min - 1 and hamming_distance(hashes_db[i][0], hashes_local[i][0]) < thresh:
            i += 1

        if i > old_i and (
                hashes_db[i][1] - start_time_db >= min_duration_time or hashes_local[i][1] - start_time_local):
            durations.append(((start_time_db, hashes_db[i][1]), (start_time_local, hashes_local[i][1])))

    return durations
