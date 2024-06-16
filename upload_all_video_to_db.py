import re
from time import time
from db_service import DBService
from db_utilities import load_config
from default_logger import logger
from video_create_hashes import create_video_fingerprints


def parse_file(file_path):

    data = ''

    with open(file_path) as f:
        data = f.read()
    pattern = r'([^ ]+) (\d+)'

    matches = re.findall(pattern, data)

    return [(filename, int(id)) for filename, id in matches]


if __name__ == '__main__':

    config = load_config()
    db_service = DBService(1, 1, config)

    data = parse_file('data.txt')

    logger.info(f'count data: {len(data)}')

    for file, id_content in data:

        print(f'[{id_content}] handle file {file}')

        start = time()
        fingerprints = create_video_fingerprints(file)
        logger.info(f'[{id_content}] created fingerprint; time: {time() - start} seconds')

        start = time()
        db_service.add_video_fingerprints(fingerprints, id_content)
        logger.info(f'[{id_content}] added to DB; times: {time() - start} seconds')
