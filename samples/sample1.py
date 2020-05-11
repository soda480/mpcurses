# Sample - Prime Number Counter

from mpcurses import queue_handler
from mpcurses import execute

from time import sleep
import logging
logger = logging.getLogger(__name__)


def is_prime(num):
    if num == 1:
        return False
    for i in range(2, num):
        if (num % i) == 0:
            return False
            break
    else:
        return True


@queue_handler
def check_primes(data, shared_data):
    range_split = data['range'].split('-')
    lower = int(range_split[0])
    upper = int(range_split[1]) + 1
    for number in range(lower, upper):
        logger.debug('checking {}'.format(number))
        # sleep here only to assist in the visualization of screen
        sleep(.001)
        if is_prime(number):
            logger.debug('prime')
        else:
            logger.debug('not prime')


def get_screen_map():
    return {
        'default': {
            'window': True,
            'begin_y': 0,
            'begin_x': 0,
            'height': 27,
            'width': 300
        },
        'number': {
            'text': 'Current Number: -',
            'text_color': 244,
            'color': 0,
            'position': (1, 0),
            'clear': True,
            'regex': '^checking (?P<value>\d+)$'
        },
        'prime': {
            'text': 'Primes: 0',
            'text_color': 244,
            'color': 3,
            'position': (2, 0),
            'count': 0,
            'keep_count': True,
            'regex': '^prime$'
        },
        'not_prime': {
            'text': 'Not Primes: 0',
            'text_color': 244,
            'color': 2,
            'position': (3, 0),
            'count': 0,
            'keep_count': True,
            'regex': '^not prime$'
        }
    }


def main():
    execute(
        function=check_primes,
        process_data=[
            {'range': '1-10000'}
        ],
        number_of_processes=1,
        screen_layout=get_screen_map())


if __name__ == '__main__':
    main()
