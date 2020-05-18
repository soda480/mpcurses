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
        'number': {
            'position': (1, 0),
            'text': 'Current Number: -',
            'text_color': 244,
            'color': 0,
            'clear': True,
            'regex': '^checking (?P<value>\d+)$'
        },
        'prime': {
            'position': (2, 0),
            'text': 'Primes: 0',
            'text_color': 244,
            'color': 3,
            'keep_count': True,
            'regex': '^prime$'
        },
        'not_prime': {
            'position': (3, 0),
            'text': 'Not Primes: 0',
            'text_color': 244,
            'color': 2,
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
