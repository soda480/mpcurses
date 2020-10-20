# Sample - Item Processor

import sys
import random
import namegenerator
import logging
from time import sleep

from mpcurses import queue_handler
from mpcurses import execute


logger = logging.getLogger(__name__)


def get_items():
    items = []
    for count in range(0, 1000):
        items.append(namegenerator.gen())
    return items


def process_items():
    items = get_items()
    logger.debug(f'{len(items)} total items')
    for item in items:
        logger.debug(f'processing item "{item}"')
        # simulate work being done
        sleep(random.choice([0.005]))
        if item.count('e') > 4:
            # simulate warning
            logger.debug(f'warning processing item "{item}"')
        elif item.count('g') > 3:
            # simulate error
            logger.debug(f'error processing item "{item}"')
        else:
            # simulate success
            logger.debug(f'item "{item}" was processed')      
    logger.debug('processing complete')


@queue_handler
def process_worker(*args):

    process_items()


def get_screen_layout():
    return {
        'default': {
            'window': True,
            'begin_y': 0,
            'begin_x': 0,
            'height': 100,
            'width': 200
        },
        'total': {
            'position': (1, 9),
            'text': 'Total: 0',
            'text_color': 0,
            'color': 15,
            'regex': r'^(?P<value>\d+) total items$'
        },
        'processed': {
            'position': (2, 4),
            'text': 'Successful: -',
            'text_color': 0,
            'color': 2,
            'keep_count': True,
            'regex': r'^item ".*" was processed$'
        },
        'warnings': {
            'position': (3, 6),
            'text': 'Warnings: -',
            'text_color': 0,
            'color': 3,
            'keep_count': True,
            'regex': r'^warning processing item ".*"$'
        },
        'errors': {
            'position': (4, 8),
            'text': 'Errors: -',
            'text_color': 0,
            'color': 1,
            'keep_count': True,
            'regex': r'^error processing item ".*"$'
        },
        'processing': {
            'position': (5, 4),
            'text': 'Processing: -',
            'text_color': 0,
            'color': 14,
            'clear': True,
            'regex': r'^processing item "(?P<value>.*)"$'
        },
        'processing_done': {
            'position': (5, 4),
            'replace_text': ' ',
            'clear': True,
            'regex': r'^processing complete$'
        },
        'items_warning_header': {
            'position': (6, 2),
            'text': 'Items w/Warnings',
            'text_color': 0
        },
        'items_error_header': {
            'position': (6, 35),
            'text': 'Items w/Errors',
            'text_color': 0
        },
        'items_with_warnings': {
            'position': (6, 2),
            'list': True,
            'color': 3,
            'regex': r'^warning processing item "(?P<value>.*)"$'
        },
        'items_with_errors': {
            'position': (6, 35),
            'list': True,
            'color': 1,
            'regex': r'^error processing item "(?P<value>.*)"$'
        }

    }


def main():
    execute(
        function=process_worker,
        number_of_processes=1,
        screen_layout=get_screen_layout())


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'simple':
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
        process_items()
    else:
        main()
