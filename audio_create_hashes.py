import time
import hashlib
import numpy as np
from scipy.ndimage import maximum_filter
from sklearn.neighbors import KDTree
from audio_utility import get_audio_duration
from default_logger import logger


def compute_log_spectrogram(audio_samples: np.ndarray, sample_rate: int, frame_size=2048, hop_size=512) \
        -> tuple[np.ndarray, int, int, int]:
    """
    Загружает WAV файл и вычисляет его логарифмическую спектрограмму.

    :param audio_samples: Аудиоданные.
    :param sample_rate: Частота дискретизации аудиоданных.
    :param frame_size: Размер каждого фрейма для FFT. По умолчанию 2048.
    :param hop_size: Шаг между фреймами. По умолчанию 512.

    :return log_spectrogram: Логарифмическая спектрограмма.
    :return sample_rate: Частота дискретизации аудиофайла.
    :return frames_count: Количество фреймов в логарифмической спектрограмме.
    :return freq_count: Количество частотных бинов в логарифмической спектрограмме.
    """
    try:
        if len(audio_samples.shape) > 1:  # Если стерео, взять только первый канал
            audio_samples = audio_samples[:, 0]

        num_frames = (len(audio_samples) - frame_size) // hop_size + 1

        # Применение окна Хэннинга к каждому фрейму
        window = np.hanning(frame_size)

        log_spectrogram = []

        for i in range(num_frames):
            frame = audio_samples[i * hop_size:i * hop_size + frame_size].astype(np.float32)
            frame *= window
            spectrogram = np.abs(np.fft.rfft(frame, n=frame_size))
            power_spectrum = spectrogram ** 2
            log_spectrogram.append(10 * np.log10(power_spectrum))

        log_spectrogram = np.array(log_spectrogram)

        return log_spectrogram, sample_rate, log_spectrogram.shape[0], log_spectrogram.shape[1]

    except ValueError as ve:
        print(f"Ошибка значения: {ve}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    


def apply_maximum_filter(spectrogram, size_window):
    """
    Применение фильтрации точек за счет оставления пиков после сравнения с исходной спектрограммой

    :param spectrogram: логарифмическая спектрограмма
    :param size_window: размер окна
    :return filtered_spectrogram: отфильтрованная спектограмма
    """

    # Применение фильтра максимумов размером kxk к логарифмической спектрограмме.
    filtered_spectrogram = maximum_filter(spectrogram, size=size_window, mode='constant')

    mask = spectrogram == filtered_spectrogram

    # Применение маски для создания отфильтрованной спектрограммы
    filtered_spectrogram = np.where(mask, spectrogram, 0).astype(np.float32)

    return filtered_spectrogram


def find_peaks(spectrogram, threshold_ratio=0.8, neighborhood_size=20):
    """
    Функция для поиска пиков в двумерном массиве (спектрограмме).
    
    :param spectrogram: логарифмическая спектрограмма
    :param threshold_ratio: процент от максимальной амплитуды для порога
    :param neighborhood_size: размер окна для поиска локальных максимумов
    
    :return detected_peaks: двумерный логический массив, где True обозначает пик
    """

    # Normalize spectrogram
    max_val = np.max(arr)
    threshold = threshold_ratio * max_val
    
    # Find local maximums
    local_max = maximum_filter(arr, size=neighborhood_size) == arr
    detected_peaks = (arr > threshold) & local_max
    return detected_peaks

def make_pairs(peaks, time_window=50, freq_window=20):
    """
    Функция для формирования пар опорных и целевых точек из target-зоны.

    :param peaks: двумерный логический массив пиков
    :param time_window: максимальный временной интервал между anchor и target
    :param freq_window: максимальная частотная разница между anchor и target

    :return pairs: список пар точек ((time_a, freq_a), (time_b, freq_b))
    """

    # Get coordinates of peaks
    peak_coordinates = np.argwhere(peaks)

    # Create KD-Tree from peak coordinates
    tree = KDTree(peak_coordinates)

    pairs = []
    # For each peak, look for the nearest points in the given windows
    for i, (t1, f1) in enumerate(peak_coordinates):
        # Find points within time_window and freq_window
        indices = tree.query_radius([[t1, f1]], r=np.sqrt(time_window ** 2 + freq_window ** 2))[0]

        for j in indices:
            if i != j:
                t2, f2 = peak_coordinates[j]
                if 0 < (t2 - t1) <= time_window and abs(f2 - f1) <= freq_window:
                    pairs.append(((t1, f1), (t2, f2)))

    return pairs


def generate_hashes(pairs, duration):
    """
    Функция для формирования хэш слепка для пар точек.
    
    :param pairs: список пар точек с ((t1, f1), (t2, f2))
    
    :return result_hashes: спиок хэш сплепков для каждой пары и время якороной точки A
    """
    min_duration_ds = pairs[0][0][0]
    max_duration_ds = pairs[-1][0][0]
    step = ((max_duration_ds - min_duration_ds) / duration)

    result_hashes = []
    for pair in pairs:

        point_a, point_b = pair
        time_a, freq_a = point_a
        time_b, freq_b = point_b

        # Key generation from frequencies and time difference
        key = f"{freq_a}-{freq_b}-{time_b - time_a}"

        # Create hash value
        hash_object = hashlib.sha256(key.encode())
        hash_hex = hash_object.hexdigest()

        # Convert to milliseconds
        time_a = int((time_a - min_duration_ds) / step)

        result_hashes.append((hash_hex, time_a))

    return result_hashes


def create_audio_hashes(audio_samples: np.ndarray, sample_rate: int, frame_size=2048, hop_size=512, size_window=3,
                          threshold_ratio=0.8, neighborhood_size=20, time_window=50, freq_window=20)\
        -> list[tuple[str, int]]:

    duration_audio_ms = int(get_audio_duration(audio_samples, sample_rate) * 1000)

    start_time = time.time()
    spectrogram, _, _, _ = compute_log_spectrogram(audio_samples, sample_rate, frame_size=frame_size, hop_size=hop_size)
    logger.debug(f'created spectrogram (shape: {spectrogram.shape}); done: {time.time() - start_time} seconds')

    start_time = time.time()
    filtered_spectrogram = apply_maximum_filter(spectrogram, size_window=size_window)
    logger.debug(f'applied maximum filter (shape: {filtered_spectrogram.shape}); done: {time.time() - start_time} seconds')

    start_time = time.time()
    peaks_mask = find_peaks(filtered_spectrogram, threshold_ratio=threshold_ratio, neighborhood_size=neighborhood_size)
    logger.debug(f'found peak mask; done: {time.time() - start_time} seconds')

    start_time = time.time()
    pairs = make_pairs(peaks_mask, time_window=time_window, freq_window=freq_window)
    logger.debug(f'found {len(pairs)} pairs; done: {time.time() - start_time} seconds')

    start_time = time.time()
    result_hashes = generate_hashes(pairs, duration=duration_audio_ms)
    logger.debug(f'generated {len(result_hashes)} hashes; done: {time.time() - start_time} seconds')

    return result_hashes    