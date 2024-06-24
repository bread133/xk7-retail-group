from collections import defaultdict
from datetime import time

from default_logger import logger
from db_service import DBService
from db_utilities import load_config
from audio_utility import get_audio_duration
from audio_utility import read_audio
from audio_utility import extract_audio_from_video_source
from audio_detection import detect_audio
from audio_create_hashes import create_audio_hashes
from time import time
import sys
import traceback 


def add_audio_to_db(db_service_: DBService, audio_source_, id_content_: int) -> list[tuple[str, int]]:
    """
    Adds hashes to the database and returns them

    :param db_service_: Database access object
    :param audio_source_: Source or path to the audio file
    :param id_content_: id content
    :return: A list of tuples (hash and time)
    """

    result_hashes = []

    try:
        audio_samples_, sample_rate_ = read_audio(audio_source_)
        duration = get_audio_duration(audio_samples_, sample_rate_)
        logger.info(f'audio file read (duration {duration} seconds)')

        result_hashes = create_audio_hashes(audio_samples_, sample_rate_)
        logger.info(f'created {len(result_hashes)} hashes')

        audio_data = [(id_content_, time_s, hash_value) for hash_value, time_s in result_hashes]

        db_service_.add_audio_snapshots(audio_data)
        logger.info(f'added hashes to DB')

    except Exception as ex_:
        logger.error(ex_)

    finally:
        return result_hashes


def audio_match_search(db_service_: DBService, audio_source_) -> dict[int, list[tuple[int, int, int]]]:
    """

    :param db_service_: Database access object
    :param audio_source_: Source or path to the audio file
    :return: Dictionary, where the key is the content id and the value is a list of tuples
        (start time of the match in the database in seconds, end time of the match in the database in seconds,
        time offset of the current audio record relative to the found audio record in seconds)
    """
    audio_dict = defaultdict(list)

    try:

        audio_samples_, sample_rate_ = read_audio(audio_source_)
        duration = get_audio_duration(audio_samples_, sample_rate_)
        logger.info(f'audio file read (duration {duration} seconds)')

        result_hashes = create_audio_hashes(audio_samples_, sample_rate_)
        logger.info(f'created {len(result_hashes)} hashes')

        audio_dict = detect_audio(result_hashes, duration, db_service_, max_diff_s=2)
        logger.info(f'count find: {len(audio_dict)}\naudio id finds: {list(audio_dict.keys())}')

    except Exception as ex_:
        logger.error(ex_)
        traceback.print_exc() 

    finally:
        return audio_dict


def example_audio_match_search(path: str):
    """
    Example of an audio record match search
    """

    try:
        config = load_config()
        
        db_service = DBService(1, 1, config)
        
        start_time = time()
        audio_source = extract_audio_from_video_source(path)
        print(f'extract audio from video: {time() - start_time} seconds')
        
        start_time = time()
        dict_audio_matches = audio_match_search(db_service, audio_source)
        print(f'search matches time: {time() - start_time} seconds')
        
        for id_content, values in dict_audio_matches.items():
            logger.info(f'audio {id_content}:')
            for time_start, time_end, diff in values:
                logger.info(f'match {time_start} to {time_end} ({time_start + diff} to {time_end + diff} ) seconds')

    except Exception as ex:
        logger.error(ex)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        logger.error(f'error')
    
    example_audio_match_search(sys.argv[1])
