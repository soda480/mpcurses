# Sample - Network Name Translator

from mpcurses import queue_handler
from mpcurses import execute

import uuid
import random
from time import sleep

import logging
logger = logging.getLogger(__name__)


def get_hex():
    try:
        return str(uuid.uuid4().get_hex().upper())
    except AttributeError:
        return uuid.uuid4().hex.upper()


def get_networks():
    networks = []
    for count in range(0, 150):
        networks.append(get_hex()[0:12])
    return networks


@queue_handler
def process_networks(data, shared_data):
    networks = get_networks()
    logger.debug('{} networks extracted'.format(len(networks)))

    for network in networks:
        logger.debug('processing network "{}"'.format(network))

        if network.startswith('6'):
            # simulate blacklist
            logger.debug('network "{}" is blacklisted'.format(network))

        elif network.startswith('0'):
            # simulate no translation
            logger.debug('network "{}" was not translated'.format(network))

        else:
            # simulate translation
            sleep(random.choice([0.1, 0.2]))
            logger.debug('network "{}" was translated'.format(network))


def get_screen_map():
    return {
        'default': {
            'window': True,
            'begin_y': 0,
            'begin_x': 0,
            'height': 27,
            'width': 300
        },
        'network': {
            'text': 'Processing Network: 0',
            'text_color': 244,
            'color': 0,
            'position': (1, 0),
            'clear': True,
            'regex': '^processing network "(?P<value>.*)"$'
        },
        'extracted': {
            'text': 'Networks To Process: 0',
            'text_color': 244,
            'color': 0,
            'position': (2, 0),
            'regex': '^(?P<value>\d+) networks extracted$'
        },
        'translated': {
            'text': 'Networks Translated: 0',
            'text_color': 244,
            'color': 3,
            'position': (3, 0),
            'count': 0,
            'keep_count': True,
            'regex': '^network ".*" was translated$'
        },
        'blacklisted': {
            'text': 'Networks BlackListed: 0',
            'text_color': 244,
            'color': 4,
            'position': (4, 0),
            'count': 0,
            'keep_count': True,
            'regex': '^network ".*" is blacklisted$'
        },
        'not_translated': {
            'text': 'Networks Not Translated: 0',
            'text_color': 244,
            'color': 2,
            'position': (5, 0),
            'count': 0,
            'keep_count': True,
            'regex': '^network ".*" was not translated$'
        },
        'counter': {
            'categories': ['translated', 'blacklisted', 'not_translated'],
            'text': '.',
            'position': (6, 0),
            'counter': True,
            'ticker': 0
        }
    }


def main():
    execute(
        function=process_networks,
        number_of_processes=1,
        screen_layout=get_screen_map())


if __name__ == '__main__':
    main()
