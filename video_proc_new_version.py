import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from moviepy.editor import VideoFileClip
import statistics

def resize_and_change_fps(input_path, output_path, new_width, new_height, fps=4):
    """
    Функция для изменения размера видео и установки частоты кадров.

    Параметры:
    - input_path (str): Путь к входному видеофайлу.
    - output_path (str): Путь к выходному видеофайлу.
    - new_width (int): Новая ширина видео.
    - new_height (int): Новая высота видео.
    - fps (int): Частота кадров в секунду (по умолчанию 4).
    """
    # Загрузка видео
    clip = VideoFileClip(input_path)

    # Изменение размеров и частоты кадров
    resized_clip = clip.resize(newsize=(new_width, new_height)).set_fps(fps)

    # Сохранение результата
    resized_clip.write_videofile(output_path, fps=fps)

def extract_keyframes(video_path, threshold=0.6):
    # Инициализация видеозахвата
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Ошибка: Не удалось открыть видео.")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) 
    frame_step = fps

    key_frames = []
    frame_groups = []
    numGroups = 1
    numScenes = 0
    frame_times = []  # Список для хранения времени ключевых кадров

    # Захват первого кадра
    ret, prev_frame = cap.read()

    if not ret:
        print("Ошибка: Не удалось прочитать первый кадр.")
        return []

    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    key_frames.append(prev_frame)
    frame_groups.append([prev_frame])
    frame_times.append(cap.get(cv2.CAP_PROP_POS_MSEC))  # Добавляем время первого кадра
    frame_count = 0

    while True:
        ret, curr_frame = cap.read()
        if not ret:
            break

        frame_count += 1


        curr_frame_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        # Вычисление SSIM между текущим и предыдущим ключевыми кадрами
        ssim_value = ssim(prev_frame_gray, curr_frame_gray)

        if ssim_value < threshold:
            # Если SSIM ниже порогового значения, добавляем новый ключевой кадр
            key_frames.append(curr_frame)
            frame_groups.append([curr_frame])
            frame_times.append(cap.get(cv2.CAP_PROP_POS_MSEC))  # Добавляем время текущего кадра
            prev_frame_gray = curr_frame_gray
            numGroups += 1
            numScenes += 1  # Обновляем количество сцен

        else:
            # Группируем кадр с последней группой
            frame_groups[-1].append(curr_frame)

    cap.release()
    return key_frames, frame_times

def generate_tiri(frames, J, gamma=0.65):
    height, width, _ = frames[0].shape
    tiri = np.zeros((height, width), dtype=np.float32)

    weights = [gamma**k for k in range(J)]

    for i in range(min(J, len(frames))):
        gray_frame = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        weighted_frame = gray_frame * weights[i]
        tiri += weighted_frame

    return tiri.astype(np.uint8)

def process_video(video_path, threshold=0.6, J=5):
    key_frames, frame_times = extract_keyframes(video_path, threshold)
    print(f"Ключевых кадров = {len(key_frames)}")
    tiris = []
    tiri_times = []
    for i in range(0, len(key_frames), J):
        segment = key_frames[i:i+J]
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
    patches = np.zeros((Height - 1, Width - 1, 2 * w  + 1, 2 * w  + 1), dtype=np.uint8)
    padded = np.pad(tiri_image, pad_width=w)
    # Извлечение окон
    for i in range(w, Height):
        for j in range(w, Width):
            patch = padded[i-w:i+w + 1, j - w:j+w+ 1]
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

    # Вычисление коэффициентов
    for i in range(Height):
        for j in range(Width):
            block = B[i, j, :, :]
            alpha[i, j] = np.dot(np.dot(v, block), np.ones(block_size))
            beta[i, j]  = np.dot(np.dot(np.ones(block_size), block), v)

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
    blocks = [binary_list[i:i+10] for i in range(0, len(binary_list), 10)]
    
    # Преобразуем каждый блок в десятичное число
    decimal_numbers = [int(''.join(map(str, block)), 2) for block in blocks]
    
    return decimal_numbers

if __name__ == "__main__":
    input_file = "D:/hackaton/xk7-retail-group/test_video.mp4"
    resized_file = "test_video_resized.mp4"
    resized_file2 = "test_video_resized2.mp4"
    resize_and_change_fps(input_file, resized_file, new_width=144, new_height=176, fps=10)
    resize_and_change_fps(input_file, resized_file2, new_width=144, new_height=176, fps=10)
    tiris, tiri_times = process_video(resized_file, threshold=0.6, J=5)
    print(f"TirisLen : {len(tiris)}")
    B = []
    for tiri in tiris:
        B.append(segment_Tiri(tiri))
    print(f"B shape: {B[0].shape}")
    print(f"BLen : {len(B)}")
    alpha, beta = compute_dct_coefficients(B[0])
    f = get_f(alpha, beta)
    hash1 = hash_frame(f)
    decimal_hash1 = binary_to_decimal(hash1)
    print(len(decimal_hash1))
    print(tiri_times)  # Вывод временных меток

    tiris, tiri_times = process_video(resized_file2, threshold=0.6, J=5)
    print(f"TirisLen : {len(tiris)}")
    B = []
    for tiri in tiris:
        B.append(segment_Tiri(tiri))
    print(f"B shape: {B[0].shape}")
    print(f"BLen : {len(B)}")
    alpha, beta = compute_dct_coefficients(B[0])
    f = get_f(alpha, beta)
    hash2 = hash_frame(f)
    decimal_hash2 = binary_to_decimal(hash2)
    print(len(decimal_hash2))
    print(tiri_times) 
    print(hash1 == hash2)
    # Пример вывода TIRI изображений
    # for idx, tiri in enumerate(tiris):
    #     print(tiri.shape)
    #     cv2.imshow(f"TIRI {idx}", tiri)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
