from scipy.io import wavfile
import numpy as np
import time 
import random
from scipy.ndimage import maximum_filter
from utils import *
from audio_hash import *

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
    


def compared_filter(spectrogram, spectrogram_max_filtered):
    """
    Фильтрация точек за счет оставления пиков после сравнения с исходной спектрограммой

    Параметры:
        spectrogram (np.ndarray): Логарифмическая спектрограмма исходная
        spectrogram_max_filtered (np.ndarray): Логарифмическая спектрограмма после max-pooling'a

    Возвращает:
        filtered_spectrogram - отфильтрованная спектрограмма
        non_zero_coords - координаты оставшихся точек
    """
    filtered_spectrogram = np.zeros_like(spectrogram, dtype=np.float32)
    # Размеры спектрограммы
    num_frames, num_bins = spectrogram.shape
    non_zero_coords = []
    for i in range(num_frames):
        for j in range(num_bins):
            if spectrogram[i, j] == spectrogram_max_filtered[i ,j]:
                filtered_spectrogram[i, j] = spectrogram[i, j]
                non_zero_coords.append((i, j))
    
    return filtered_spectrogram, non_zero_coords



def find_peaks(arr, threshold_ratio=0.8, neighborhood_size=20):
    """
    Функция для поиска пиков в двумерном массиве (спектрограмме).
    
    Параметры:
    - arr: двумерный массив (спектрограмма)
    - threshold_ratio: процент от максимальной амплитуды для порога
    - neighborhood_size: размер окна для поиска локальных максимумов
    
    Возвращает:
    - detected_peaks: двумерный логический массив, где True обозначает пик
    """
    # Нормализуем спектрограмму
    max_val = np.max(arr)
    threshold = threshold_ratio * max_val
    
    # Найдем локальные максимумы
    local_max = maximum_filter(arr, size=neighborhood_size) == arr
    detected_peaks = (arr > threshold) & local_max
    return detected_peaks

def form_pairs(peaks, time_window=50, freq_window=20):
    """
    Функция для формирования пар опорных и целевых точек из target-зоны.
    
    Параметры:
    - peaks: двумерный логический массив пиков
    - time_window: максимальный временной интервал между anchor и target
    - freq_window: максимальная частотная разница между anchor и target
    
    Возвращает:
    - pairs: список пар точек ((t1, f1), (t2, f2))
    """
    # Получим координаты пиков
    peak_coords = np.argwhere(peaks)
    pairs = []
    
    # Для каждой опорной точки найдем целевые точки в заданных окнах
    for i, (t1, f1) in enumerate(peak_coords):
        for j, (t2, f2) in enumerate(peak_coords):
            if i != j and 0 < (t2 - t1) <= time_window and abs(f2 - f1) <= freq_window:
                pairs.append([(t1, f1), (t2, f2)])
    
    return pairs


if __name__ == "__main__":
    test_per_second_spectr()