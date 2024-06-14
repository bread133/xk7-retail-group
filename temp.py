import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import librosa

# Загрузка wav файла
sample_rate, audio_data = wavfile.read('test3.wav')

# Генерация спектрограммы
frequencies, times, spectrogram_data = spectrogram(audio_data[:, 0], sample_rate)

# Вывод спектрограммы
plt.figure(figsize=(10, 6))
plt.pcolormesh(times, frequencies, 10 * np.log10(spectrogram_data), shading='gouraud')
plt.colorbar(label='Амплитуда')
plt.xlabel('Время, с')
plt.ylabel('Частота')
plt.show()

# Загрузка аудиофайла
audio_file = 'test3.wav'
y, sr = librosa.load(audio_file)

# Вычисление спектрограммы
spectrogram = np.abs(librosa.stft(y))

# Проверка размерности спектрограммы
print(spectrogram.shape)  # Размерность (частота, время)

# Возможно, вам понадобится транспонировать массив, чтобы он соответствовал вашему описанию
spectrogram_3d = np.expand_dims(spectrogram, axis=-1)

# Проверка размерности трехмерного массива
print(spectrogram_3d.shape)  # Размерность (частота, время, 1)
