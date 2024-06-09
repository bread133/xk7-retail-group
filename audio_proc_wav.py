from scipy.io import wavfile
import numpy as np
import time 
import random
from scipy.ndimage import maximum_filter
from utils import *
from audio_hash import *

def compute_log_spectrogram(wav_path, frame_size=2048, hop_size=512):
    """
    Загружает WAV файл и вычисляет его логарифмическую спектрограмму.

    Параметры:
        wav_path (str): Путь к WAV файлу.
        frame_size (int): Размер каждого фрейма для FFT. По умолчанию 2048.
        hop_size (int): Шаг между фреймами. По умолчанию 512.

    Возвращает:
        log_spectrogram (np.ndarray): Логарифмическая спектрограмма.
        sample_rate (int): Частота дискретизации аудиофайла.
        frames_count (int): Количество фреймов в логарифмической спектрограмме.
        freq_count (int): Количество частотных бинов в логарифмической спектрограмме.
    """
    try:
        # Загрузка WAV файла
        sample_rate, samples = wavfile.read(wav_path)
        if len(samples.shape) > 1:  # Если стерео, взять только первый канал
            samples = samples[:, 0]
        
        # Преобразование одномерных аудиоданных в фреймы
        frames = np.array([samples[i:i+frame_size].astype(np.float32) 
                           for i in range(0, len(samples) - frame_size, hop_size)])
        
        # Применение окна Хэннинга к каждому фрейму
        window = np.hanning(frame_size)
        frames *= window
        
        # Вычисление спектрограммы
        spectrogram = np.abs(np.fft.rfft(frames, n=frame_size))
        power_spectrum = spectrogram ** 2
        log_spectrogram = 10 * np.log10(power_spectrum)
        
        return log_spectrogram, sample_rate, log_spectrogram.shape[0], log_spectrogram.shape[1]
        
    except FileNotFoundError:
        print(f"Файл не найден: {wav_path}")
        return None, None, None, None
    except ValueError as ve:
        print(f"Ошибка значения: {ve}")
        return None, None, None, None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None, None, None, None

def max_filter(spectrogram, window_size=3):
    """
    Применяет фильтр максимумов размером kxk к логарифмической спектрограмме.

    Параметры:
        spectrogram (np.ndarray): Логарифмическая спектрограмма.
        window_size (int): Размер окна

    Возвращает:
        filtered_spectrogram (np.ndarray): Спектрограмма после применения фильтра максимумов.
    """

    filtered_spectrogram = np.zeros_like(spectrogram)
    
    # Размеры спектрограммы
    num_frames, num_bins = spectrogram.shape
    
    # Половина размера окна для удобства использования при выборе окрестности
    half_window_size = window_size // 2
    
    # Применяем фильтр к каждому пикселю спектрограммы, кроме граничных пикселей
    for i in range(half_window_size, num_frames - half_window_size):
        for j in range(half_window_size, num_bins - half_window_size):
            # Выбираем окрестность с пользовательским размером окна вокруг текущего пикселя
            neighborhood = spectrogram[i-half_window_size:i+half_window_size+1, j-half_window_size:j+half_window_size+1]
            # Находим максимальное значение в окрестности
            max_value = np.max(neighborhood)
            # Присваиваем максимальное значение текущему пикселю в результате
            filtered_spectrogram[i, j] = max_value
    
    return filtered_spectrogram

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

def select_uniform_points(matrix, N, non_zero_coords):
    """
    Функция для ограничения пиков спектрограммы до N точек

    Параметры:
        matrix (np.ndarray): Исходная матрица (спектрограмма)
        N (int): Число точек, которые надо оставить
        non_zero_coords: Координаты оставшихся точек
    Возвращает:
        N_matrix - Проработанная до N - точек спектрограмма
    """
    n, m = matrix.shape
    
    # Проверяем, что ненулевых точек больше или равно N
    if len(non_zero_coords) < N:
        raise ValueError("Количество ненулевых точек меньше, чем N")
    
    # Сэмплирование по Uniform-распеределению N точек из ненулевых координат
    selected_coords = random.sample(non_zero_coords, N)
    
    # Создаем новую матрицу с нулями
    N_matrix = np.zeros((n, m), dtype=matrix.dtype)
    
    # Расставляем выбранные точки в новой матрице
    for i, j in selected_coords:
        N_matrix[i, j] = matrix[i, j]
    
    return N_matrix


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

def test():
    wav_path = 'test3.wav'
    # Пример использования
    start = time.time()
    log_spectrogram, sample_rate, frames_count, freq_count = compute_log_spectrogram(wav_path)
    filtered_spectrogram = max_filter(log_spectrogram)
    compare_filtered_spectrogram, non_zero_coords = compared_filter(log_spectrogram, filtered_spectrogram)
    n_spectrogram = select_uniform_points(compare_filtered_spectrogram, len(non_zero_coords) // 4, non_zero_coords)

    peaks_mask = find_peaks(n_spectrogram, threshold_ratio=0.8)
    pairs = form_pairs(peaks_mask)
    hashes = generate_hashes(pairs)
    finish = time.time()
    res = finish - start
    res_msec = int(res * 1000)
    print('Время работы в миллисекундах: ', res_msec)
    plot_spectrogram(n_spectrogram, sample_rate, frames_count, freq_count)

if __name__ == "__main__":
    test()