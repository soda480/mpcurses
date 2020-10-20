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


def process_items(group):
    items = get_items()
    logger.debug(f'group{group} has {len(items)} total items')
    for item in items:
        logger.debug(f'processing item "group{group}-{item}"')
        # simulate work being done
        sleep(random.choice([0.005, 0.018]))
        if item.count('e') > 4:
            # simulate warning
            logger.debug(f'warning processing item "group{group}-{item}"')
        elif item.count('g') > 3:
            # simulate error
            logger.debug(f'error processing item "group{group}-{item}"')
        else:
            # simulate success
            logger.debug(f'item "group{group}-{item}" was processed')      
    logger.debug(f'processing complete for group{group}')


@queue_handler
def process_worker(process_data, *args):
    group = process_data['group']
    process_items(group)


def get_screen_layout():
    return {
        'default': {
            'window': True,
            'begin_y': 0,
            'begin_x': 0,
            'height': 100,
            'width': 400
        },
        'header_group': {
            'position': (1, 4),
            'text': 'Group',
            'text_color': 0
        },
        'header_total': {
            'position': (1, 12),
            'text': 'TOT',
            'text_color': 0
        },
        'header_successful': {
            'position': (1, 17),
            'text': 'SUC',
            'text_color': 0
        },
        'header_warnings': {
            'position': (1, 21),
            'text': 'WAR',
            'text_color': 0
        },
        'header_errors': {
            'position': (1, 25),
            'text': 'ERR',
            'text_color': 0
        },
        'header_item': {
            'position': (1, 29),
            'text': 'Item',
            'text_color': 0
        },
        'active': {
            'position': (2, 2),
            'text': '',
            'replace_text': '->',
            'color': 0,
            'regex': r'^processing item .*$',
            'table': True
        },
        'inactive': {
            'position': (2, 2),
            'text': '',
            'replace_text': '  ',
            'regex': r'^processing complete for group.*$',
            'table': True
        },
        'group': {
            'position': (2, 4),
            'color': 14,
            'regex': r"^(?P<value>.*) has \d+ total items$",
            'table': True
        },
        'total': {
            'position': (2, 12),
            'color': 15,
            'regex': r"^group.* has (?P<value>\d+) total items$",
            'table': True
        },
        'successful': {
            'position': (2, 17),
            'text': '---',
            'text_color': 0,
            'color': 2,
            'keep_count': True,
            'regex': r'^item ".*" was processed$',
            'table': True,
        },
        'warnings': {
            'position': (2, 21),
            'text': '---',
            'text_color': 0,
            'color': 3,
            'keep_count': True,
            'regex': r'^warning processing item ".*"$',
            'table': True,
        },
        'errors': {
            'position': (2, 25),
            'text': '---',
            'text_color': 0,
            'color': 1,
            'keep_count': True,
            'regex': r'^error processing item ".*"$',
            'table': True,
        },
        'item': {
            'position': (2, 29),
            'color': 14,
            'clear': True,
            'regex': r'^processing item "group\d+-(?P<value>.*)"$',
            'table': True,
        },
        'item_done': {
            'position': (2, 29),
            'replace_text': ' ',
            'clear': True,
            'regex': r'^processing complete for group.*$',
            'table': True,
        },
        'group01_items_header': {
            'position': (6, 2),
            'text': 'group01 Warnings/Errors',
            'text_color': 0
        },
        'group02_items_header': {
            'position': (6, 35),
            'text': 'group02 Warnings/Errors',
            'text_color': 0
        },
        'group03_items_header': {
            'position': (6, 68),
            'text': 'group03 Warnings/Errors',
            'text_color': 0
        },
        'group01_items': {
            'position': (6, 2),
            'list': True,
            'color': 3,
            'regex': r'^(warning|error) processing item "group01-(?P<value>.*)"$',
            'effects': [
                {
                    'regex': r'^error processing item .*$',
                    'color': 1
                }, {
                    'regex': r'^warning processing item .*$',
                    'color': 3
                }
            ]
        },
        'group02_items': {
            'position': (6, 35),
            'list': True,
            'color': 3,
            'regex': r'^(warning|error) processing item "group02-(?P<value>.*)"$',
            'effects': [
                {
                    'regex': r'^error processing item .*$',
                    'color': 1
                }, {
                    'regex': r'^warning processing item .*$',
                    'color': 3
                }
            ]
        },
        'group03_items': {
            'position': (6, 68),
            'list': True,
            'color': 3,
            'regex': r'^(warning|error) processing item "group03-(?P<value>.*)"$',
            'effects': [
                {
                    'regex': r'^error processing item .*$',
                    'color': 1
                }, {
                    'regex': r'^warning processing item .*$',
                    'color': 3
                }
            ]
        },
    }


def main():
    execute(
        function=process_worker,
        process_data=[
            {'group': '01'},
            {'group': '02'},
            {'group': '03'}
        ],
        number_of_processes=3,
        screen_layout=get_screen_layout())


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'simple':
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
        for group in ['01', '02', '03']:
            process_items(group)
    else:
        main()
