import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from moviepy.editor import VideoFileClip
import statistics
from time import time
from default_logger import logger


def resize_and_change_fps(input_path, new_width=144, new_height=176, fps=4):
    """
    Функция для изменения размера видео и установки частоты кадров.

    Параметры:
    - input_path (str): Путь к входному видеофайлу.
    - new_width (int): Новая ширина видео.
    - new_height (int): Новая высота видео.
    - fps (int): Частота кадров в секунду (по умолчанию 4).
    """
    # Загрузка видео
    clip = VideoFileClip(input_path)

    # Изменение размеров и частоты кадров
    resized_clip = clip.resize(newsize=(new_width, new_height)).set_fps(fps)

    return resized_clip


def extract_keyframes(resized_clip, threshold=0.6):
    """
    Функция для извлечения ключевых кадров из видео.

    Параметры:
    - resized_clip (VideoFileClip): Объект VideoFileClip.
    - threshold (float): Пороговое значение SSIM для определения ключевых кадров.
    """
    fps = resized_clip.fps
    key_frames = []
    frame_groups = []
    numGroups = 1
    numScenes = 0
    frame_times = []  # Список для хранения времени ключевых кадров

    # Инициализация итератора кадров
    frames = list(resized_clip.iter_frames())
    num_frames = len(frames)

    # Захват первого кадра
    if num_frames == 0:
        logger.error("Ошибка: Не удалось прочитать первый кадр.")
        return []

    prev_frame = frames[0]
    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_RGB2GRAY)
    key_frames.append(prev_frame)
    frame_groups.append([prev_frame])
    frame_times.append(0)  # Время первого кадра (0 мс)
    frame_count = 0

    for frame_idx in range(1, num_frames):
        curr_frame = frames[frame_idx]
        frame_time = (frame_idx / fps) * 1000  # Время в миллисекундах

        curr_frame_gray = cv2.cvtColor(curr_frame, cv2.COLOR_RGB2GRAY)
        # Вычисление SSIM между текущим и предыдущим ключевыми кадрами
        ssim_value = ssim(prev_frame_gray, curr_frame_gray)

        if ssim_value < threshold:
            # Если SSIM ниже порогового значения, добавляем новый ключевой кадр
            key_frames.append(curr_frame)
            frame_groups.append([curr_frame])
            frame_times.append(frame_time)  # Добавляем время текущего кадра
            prev_frame_gray = curr_frame_gray
            numGroups += 1
            numScenes += 1  # Обновляем количество сцен

        else:
            # Группируем кадр с последней группой
            frame_groups[-1].append(curr_frame)

    return key_frames, frame_times


def generate_tiri(frames, J, gamma=0.65):
    height, width, _ = frames[0].shape
    tiri = np.zeros((height, width), dtype=np.float32)

    weights = [gamma ** k for k in range(J)]

    for i in range(min(J, len(frames))):
        gray_frame = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        weighted_frame = gray_frame * weights[i]
        tiri += weighted_frame

    return tiri.astype(np.uint8)


def process_video(video, threshold=0.6, J=5):
    key_frames, frame_times = extract_keyframes(video, threshold)
    logger.info(f'Ключевых кадров = {len(key_frames)}')
    tiris = []
    tiri_times = []
    for i in range(0, len(key_frames), J):
        segment = key_frames[i:i + J]
        if len(segment) < J:
            continue

        tiri = generate_tiri(segment, J)
        tiris.append(tiri)
        tiri_times.append(frame_times[i])  # Сохраняем времена для сегмента

    return tiris, tiri_times


def segment_Tiri(tiri_image, window_size=2):
    """
    Извлекает окна изображения.

    Параметры:
    - image (numpy.ndarray): Изображение (матрица).
    - window_size (int): Размер окна

    Возвращает:
    - patches (numpy.ndarray): Массив окон размером (image.shape[0] - 1, image.shape[1] - 1, window_size, window_size).
    """

    Height, Width = tiri_image.shape
    w = window_size
    patches = np.zeros((Height - 1, Width - 1, 2 * w + 1, 2 * w + 1), dtype=np.uint8)
    padded = np.pad(tiri_image, pad_width=w)
    # Извлечение окон
    for i in range(w, Height):
        for j in range(w, Width):
            patch = padded[i - w:i + w + 1, j - w:j + w + 1]
            patches[i - w, j - w] = patch

    return patches


def compute_dct_coefficients(B):
    """
    Вычисляет коэффициенты DCT для заданной матрицы B.

    Параметры:
    B (numpy.ndarray): Четырехмерная матрица размерности (Height, Width, block_size, block_size)

    Возвращает:
    alpha (numpy.ndarray): Матрица коэффициентов alpha размерности (Height, Width)
    beta (numpy.ndarray): Матрица коэффициентов beta размерности (Height, Width)
    """
    # Размер блока
    block_size = B.shape[2]
    w = (block_size - 1) / 2

    # Генерация вектора v
    v = np.array([np.cos((k + 0.5) * np.pi / (2 * w)) for k in range(block_size)])

    # Инициализация массивов для коэффициентов
    Height, Width = B.shape[:2]
    alpha = np.zeros((Height, Width))
    beta = np.zeros((Height, Width))

    # # Вычисление коэффициентов
    # for i in range(Height):
    #     for j in range(Width):
    #         block = B[i, j, :, :]
    #         alpha[i, j] = np.dot(np.dot(v, block), np.ones(block_size))
    #         beta[i, j]  = np.dot(np.dot(np.ones(block_size), block), v)
    # Вычисление alpha
    alpha = np.tensordot(B, np.outer(v, np.ones(block_size)), axes=([2, 3], [0, 1]))

    # Вычисление beta
    beta = np.tensordot(B, np.outer(np.ones(block_size), v), axes=([2, 3], [0, 1]))

    return np.ravel(alpha).tolist(), np.ravel(beta).tolist()


def get_f(alpha, beta):
    return np.ravel(alpha).tolist() + np.ravel(beta).tolist()


def hash_frame(f_vector):
    median = statistics.median(f_vector)
    for i in range(len(f_vector)):
        f_vector[i] = int(f_vector[i] >= median)

    return f_vector


def binary_to_decimal(binary_list):
    # Проверяем, что длина списка кратна 10
    if len(binary_list) % 10 != 0:
        raise ValueError("Длина списка должна быть кратна 10")

    # Разбиваем список на блоки длиной 10
    blocks = [binary_list[i:i + 10] for i in range(0, len(binary_list), 10)]

    # Преобразуем каждый блок в десятичное число
    decimal_numbers = [int(''.join(map(str, block)), 2) for block in blocks]

    return decimal_numbers


def create_video_fingerprints(filename: str) -> list[tuple[list[int], int]]:
    """
    Create video fingerprint

    :param filename: full path to file
    :return: list with tuple (fingerprint data and fingerprint timestamp)
    """

    start_time = time()
    resized_file = resize_and_change_fps(filename, new_width=104, new_height=136, fps=5)
    logger.debug(f'resized: {time() - start_time} seconds')

    start_time = time()
    tiris, tiri_times = process_video(resized_file, threshold=0.6, J=5)
    logger.debug(f'created tiris (count: {len(tiris)}): {time() - start_time} seconds')

    start_time = time()
    B = []
    for tiri in tiris:
        B.append(segment_Tiri(tiri))
    logger.debug(f'created B (count: {len(B)}): {time() - start_time} seconds')

    start_time_cycle = time()
    hashes = []

    for i in range(len(B)):
        alpha, beta = compute_dct_coefficients(B[i])

        f = get_f(alpha, beta)

        hashes.append(hash_frame(f))

    logger.debug(f'created hashes (count: {len(hashes)}): {time() - start_time_cycle} seconds')
    hashes_decimal = map(binary_to_decimal, hashes)

    return list(zip(hashes_decimal, tiri_times))
