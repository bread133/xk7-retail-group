import matplotlib.pyplot as plt

def plot_spectrogram(log_spectrogram, sample_rate, frames_count, freq_count):
    """
    Отображает логарифмическую спектрограмму.

    Параметры:
        log_spectrogram (np.ndarray): Логарифмическая спектрограмма.
        sample_rate (int): Частота дискретизации аудиофайла.
        frames_count (int): Количество фреймов в логарифмической спектрограмме.
        freq_count (int): Количество частотных бинов в логарифмической спектрограмме.

    Возвращает:
        None
    """
    if log_spectrogram is None:
        print("Нет данных спектрограммы для отображения.")
        return
    
    try:
        plt.figure(figsize=(10, 6))
        extent = [0, frames_count, 0, sample_rate / 2]
        plt.imshow(log_spectrogram.T, aspect='auto', origin='lower', extent=extent)
        plt.xlabel('Время')
        plt.ylabel('Частота')
        plt.colorbar(label='Амплитуда')
        plt.title('Спектрограмма')
        plt.show()
        
    except Exception as e:
        print(f"Произошла ошибка при построении графика, вероятно, не те размерности: {e}")