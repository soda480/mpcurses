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


def get_screen_layout():
    return {
        'network': {
            'position': (1, 0),
            'text': 'Processing Network: 0',
            'text_color': 244,
            'color': 236,
            'clear': True,
            'regex': '^processing network "(?P<value>.*)"$'
        },
        'extracted': {
            'position': (2, 0),
            'text': 'Networks To Process: 0',
            'text_color': 244,
            'color': 0,
            'regex': '^(?P<value>\d+) networks extracted$'
        },
        'translated': {
            'position': (3, 0),
            'text': 'Networks Translated: 0',
            'text_color': 244,
            'color': 2,
            'keep_count': True,
            'regex': '^network ".*" was translated$'
        },
        'blacklisted': {
            'position': (4, 0),
            'text': 'Networks BlackListed: 0',
            'text_color': 244,
            'color': 232,
            'keep_count': True,
            'regex': '^network ".*" is blacklisted$'
        },
        'not_translated': {
            'position': (5, 0),
            'text': 'Networks Not Translated: 0',
            'text_color': 244,
            'color': 237,
            'keep_count': True,
            'regex': '^network ".*" was not translated$'
        },
        '_counter_': {
            'position': (6, 0),
            'categories': [
                'translated',
                'blacklisted',
                'not_translated'
            ],
            'counter_text': '|',
            # 'modulus': 5,
            # 'color': 44,
            # 'regex': '^(?P<value>\d+) networks extracted$'
        }
    }


def main():
    execute(
        function=process_networks,
        number_of_processes=1,
        screen_layout=get_screen_layout())


if __name__ == '__main__':
    main()
