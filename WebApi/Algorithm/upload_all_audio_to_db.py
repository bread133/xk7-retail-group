import cv2
import os
import sys

from Algorithm.video_create_hash import create_video_fingerprints
from db_service import DBService
from db_utilities import load_config
from os import listdir
from audio_create_hashes import create_audio_hashes
from audio_utility import extract_audio_from_video_source, read_audio
from default_logger import logger


def get_duration_video(filename: str):
    cap = cv2.VideoCapture(filename)

    if not cap.isOpened():
        logger.error(f'failed open file {filename}')
        return None

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fps = cap.get(cv2.CAP_PROP_FPS)

    cap.release()
    return frame_count / fps


def create_fingerprint_audio(path: str):
    audio_stream_ = extract_audio_from_video_source(path)
    audio_samples_, sample_rate_ = read_audio(audio_stream_)

    result_hashes_ = create_audio_hashes(audio_samples_, sample_rate_)

    return result_hashes_


def create_and_load_fingerprint_audio(title: str, path: str, db_service_):
    id_ = db_service_.add_content(title, get_duration_video(path))

    result_hashes_audio = create_fingerprint_audio(path)

    audio_data_ = [(id_, time_s, hash_value) for hash_value, time_s in result_hashes_audio]
    db_service_.add_audio_snapshots(audio_data_)

    return id_


def create_and_load_video_fingerprint(id_, path: str):
    result_fingerprint = create_video_fingerprints(path)
    db_service.add_video_fingerprints(result_fingerprint, id_)

    return id_


if __name__ == '__main__':

    if len(sys.argv) != 2:
        logger.error(f'wrong number of arguments')

    dir = sys.argv[1]

    if os.path.isdir(dir):
        logger.error(f'path is not a directory')

    try:
        config = load_config()
        db_service = DBService(1, 1, config)

        logger.info(f'count files: {len(listdir(dir))}')

        data = []

        for root, dirs, files in os.walk(dir):
            for file in listdir(dir):

                full_path = os.path.join(dir, file)

                logger.info(f'handle file {full_path}')

                if not os.path.isfile(full_path):
                    logger.warning(f'Skipping {full_path} as it is not a file.')
                    continue

                duration = int(get_duration_video(full_path))
                id_content = db_service.add_content(file, duration)

                data.append((full_path, id_content))

        logger.info(f'count data: {len(data)}')

        if len(data) > 0:
            logger.debug(f'first id: {data[0][1]}; last id: {data[-1][1]}')

        for file, id_content in data:
            logger.debug(f'({file}, {id_content})')

        with open('data.txt', 'w') as f:
            for file, id_content in data:
                f.write(f'{file} {id_content}')

        for file, id_content in data:

            audio_stream = extract_audio_from_video_source(file)
            logger.info(f'[{id_content}] extracted audio')
            audio_samples, sample_rate = read_audio(audio_stream)

            result_hashes = create_audio_hashes(audio_samples, sample_rate)
            logger.info(f'[{id_content}] created {len(result_hashes)} hashes')

            audio_data = [(id_content, time_s, hash_value) for hash_value, time_s in result_hashes]

            db_service.add_audio_snapshots(audio_data)
            logger.info(f'[{id_content}] added to DB')

    except Exception as ex:
        logger.error(f'exception: {ex}')
