import os
import random
import namegenerator
import logging
from time import sleep

from mpcurses import MPcurses
from layout import screen_layout

logger = logging.getLogger(__name__)


def get_items(count):
    items = []
    for count in range(0, count):
        items.append(namegenerator.gen())
    return items


def simulate_work(message):
    value = random.choice([.1, .15, .17, .18, .2, .25, .6])
    sleep(value)


def process_item(item=None):
    logger.debug(f'processing item {item}')
    logger.debug(f'item {item} head is at v{random.randint(0, 9)}.{random.randint(0, 9)}.{random.randint(0, 20)}')
    vectors = random.randint(20, 70)
    logger.debug(f'item {item} has {str(vectors).zfill(3)} vectors')
    for vector in range(vectors):
        simulate_work(f'processing vector {vector} for item {item}')
        logger.debug(f'processed vector {vector} for item {item}')
    logger.debug(f'processed item {item}')


def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('example6.log')
    file_formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)


def main():
    configure_logging()
    items = get_items(random.randint(1, 60))
    MPcurses(
        function=process_item,
        process_data=[
            {'item': item} for item in items
        ],
        processes_to_start=25,
        screen_layout=screen_layout).execute()


if __name__ == '__main__':

    main()
