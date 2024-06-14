import numpy as np

from io import BytesIO
from moviepy.video.io.VideoFileClip import VideoFileClip
from requests import get
from scipy.io import wavfile


def extract_audio_from_video_source(input_source) -> BytesIO:
    """
    Извлекает аудиодорожку из видеопотока и возвращает её в формате wav.

    :param video_stream: Поток байтов с видеоданными.
    :return audio_stream: Поток байтов с аудиоданными в формате wav.
    """
    video_clip = VideoFileClip(input_source)
    audio_clip = video_clip.audio
    audio_samples = audio_clip.to_soundarray()
    sample_rate = audio_clip.fps  # Получение исходного sample rate

    # Создаем поток для wav-данных
    wav_io = BytesIO()
    wavfile.write(wav_io, sample_rate, audio_samples.astype(np.int16))
    wav_io.seek(0)
    return wav_io


def read_audio(input_source) -> tuple[np.ndarray, int]:
    """
    Выполняет чтение аудиоданных в формате 'wav'

    :param input_source: Поток аудиоданным или путь к аудиоданным.
    :return audio_samples: Аудиоданные.
    :return sample_rate: Частота дискретизации аудиоданных.
    """

    if isinstance(input_source, str):
        with open(input_source, 'rb') as f:
            sample_rate, audio_samples = wavfile.read(f)
    else:
        # Иначе, считаем, что это объект BytesIO
        with input_source as f:
            sample_rate, audio_samples = wavfile.read(f)

    return audio_samples, sample_rate


def get_audio_duration(audio_samples: np.ndarray, sample_rate: int) -> float:
    """
    Получает длительность аудиозаписи в секундах.

    :param audio_samples: Аудиоданные.
    :param sample_rate: Частота дискретизации аудиоданных.
    :return duration: Длительность аудиозаписи в секундах.
    """
    num_samples = audio_samples.shape[0]

    duration = num_samples / sample_rate

    return duration


def example1(filename_: str):
	"""
    Пример. Извлекает аудиодорожку из видеофайла и печатает длительность в секундах.

    :param filename_: Путь к видеофайлу.
    """

    audio_stream = extract_audio_from_video_source(filename_)
    audio_samples, sample_rate = read_audio(audio_stream)

    duration = get_audio_duration(audio_samples, sample_rate)

    print(f'duration \'{filename_}\': {duration}')


if __name__ == '__main__':

    try:
        example1('video_check.mp4')

    except Exception as ex:
        print(f'Exception: {ex}')
