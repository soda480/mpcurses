# Sample - Wrap-around Table

from mpcurses import queue_handler
from mpcurses import execute

import os
import random
import namegenerator
from time import sleep

import logging
logger = logging.getLogger(__name__)


def get_items(count):
    items = []
    for count in range(0, count):
        items.append(namegenerator.gen())
    return items


def simulate_error(value, message):
    if value < .2:
        raise Exception(message)


def simulate_work(message):
    value = random.choice([.1, .15, .17, .18, .2, .25, .6])
    sleep(value)
    simulate_error(value, message)


@queue_handler
def process_item(data, shared_data):
    item = data['item']
    logger.debug(f'processing item {item}')
    logger.debug(f'item {item} head is at v{random.randint(0, 9)}.{random.randint(0, 9)}.{random.randint(0, 20)}')
    vectors = random.randint(20, 70)
    logger.debug(f'item {item} has {str(vectors).zfill(3)} vectors')
    for vector in range(vectors):
        try:
            simulate_work(f'processing vector {vector} for item {item}')
            logger.debug(f'processed vector {vector} for item {item}')
        except Exception as exception:
            logger.error(f'{exception}')
            continue
    logger.debug(f'processed item {item}')


def get_screen_layout():
    return {
        'default': {
            'window': True,
            'begin_y': 0,
            'begin_x': 0,
            'height': 100,
            'width': 200
        },
        'table': {
            'rows': 20,
            'cols': 3,
            'width': 50
        },
        '_on': {
            'position': (1, 0),
            'text': '',
            'replace_text': '>',
            'color': 14,
            'regex': r'^processing item .*$',
            'table': True
        },
        '_off': {
            'position': (1, 0),
            'text': '',
            'replace_text': ' ',
            'regex': r'^processed item .*$',
            'table': True
        },
        'vectors': {
            'position': (1, 2),
            'text': '---',
            'text_color': 244,
            'color': 7,
            'regex': r'^item .* has (?P<value>.*) vectors$',
            'table': True,
        },
        'processed': {
            'position': (1, 6),
            'text': '---',
            'text_color': 244,
            'color': 7,
            'keep_count': True,
            'regex': r'^processed vector .*$',
            'zfill': 3,
            'table': True
        },
        'version': {
            'position': (1, 10),
            'text': '-------',
            'text_color': 244,
            'color': 244,
            'width': 7,
            'right_justify': True,
            'regex': r'^item .* head is at (?P<value>.*)$',
            'table': True
        },
        'item_initialized': {
            'position': (1, 18),
            'text': '',
            'color': 244,
            'width': 28,
            'regex': r"^'item' is '(?P<value>.*)'$",
            'table': True
        },
        'item_processing': {
            'position': (1, 18),
            'text': '',
            'color': 14,
            'width': 28,
            'regex': r'^processing item (?P<value>.*)$',
            'table': True
        },
        'item_processed': {
            'position': (1, 18),
            'text': '',
            'color': 7,
            'width': 28,
            'regex': r'^processed item (?P<value>.*)$',
            'table': True
        },
        'processes': {
            'text': 'Processes:',
            'text_color': 244,
            'position': (22, 2)
        },
        'procs_active': {
            'text': 'Active: 0',
            'text_color': 7,
            'color': 14,
            'position': (23, 5),
            'regex': r'^mpcurses: number of active processes (?P<value>\d+)$',
            'effects': [
                {
                    'regex': r'^mpcurses: number of active processes 000$',
                    'color': 7
                }
            ],
        },
        'procs_queued': {
            'text': 'Queued: 0',
            'text_color': 7,
            'color': 244,
            'position': (24, 5),
            'regex': r'^mpcurses: number of queued processes (?P<value>\d+)$',
            'effects': [
                {
                    'regex': r'^mpcurses: number of queued processes 000$',
                    'color': 7
                }
            ],
        },
        'procs_complete': {
            'text': 'Completed: 0',
            'text_color': 7,
            'color': 7,
            'position': (25, 2),
            'keep_count': True,
            'regex': r'^mpcurses: a process has completed$'
        },
    }


def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('sample6.log')
    file_formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)


def main():
    configure_logging()
    items = get_items(60)
    execute(
        function=process_item,
        process_data=[
            {'item': item} for item in items
        ],
        number_of_processes=25,
        screen_layout=get_screen_layout())


if __name__ == '__main__':

    main()
