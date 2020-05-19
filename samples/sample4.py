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
    logger.debug('checking total of {} numbers'.format(upper - lower))
    for number in range(lower, upper):
        logger.debug('checking {}'.format(number))
        if is_prime(number):
            logger.debug('prime')
        else:
            logger.debug('not prime')


def get_screen_layout():
    return {
        'range_header': {
            'position': (2, 3),
            'text': 'Range',
            'text_color': 243,
        },
        'number_header': {
            'position': (2, 14),
            'text': 'Number',
            'text_color': 243,
        },
        'prime_header': {
            'position': (2, 23),
            'text': 'Primes',
            'text_color': 243,
        },
        'notprime_header': {
            'position': (2, 32),
            'text': 'NotPrimes',
            'text_color': 243,
        },
        'progress_header': {
            'position': (2, 44),
            'text': 'Progress',
            'text_color': 243,
        },
        'range': {
            'position': (3, 0),
            'text': '',
            'color': 0,
            'regex': "^'range' is '(?P<value>.*)'$",
            'table': True
        },
        'number': {
            'position': (3, 14),
            'text': '',
            'color': 63,
            'regex': '^checking (?P<value>\d+)$',
            'table': True
        },
        'prime': {
            'position': (3, 23),
            'text': '',
            'color': 40,
            'keep_count': True,
            'zfill': 4,
            'regex': '^prime$',
            'table': True
        },
        'not_prime': {
            'position': (3, 32),
            'text': '',
            'color': 11,
            'keep_count': True,
            'regex': '^not prime$',
            'zfill': 4,
            'table': True
        },
        '_counter_': {
            'position': (3, 44),
            'categories': [
                'number'
            ],
            'counter_text': '|',
            'modulus': 200,
            'color': 44,
            'regex': '^checking total of (?P<value>\d+) numbers$',
            'table': True
        },
        'total_header': {
            'position': (14, 15),
            'text': 'Total:',
            'text_color': 243,
        },
        'prime_total': {
            'position': (14, 23),
            'text': '',
            'color': 40,
            'keep_count': True,
            'zfill': 4,
            'regex': '^prime$',
        },
        'not_prime_total': {
            'position': (14, 32),
            'text': '',
            'color': 11,
            'keep_count': True,
            'zfill': 5,
            'regex': '^not prime$',
        },
    }


def main():
    execute(
        function=check_primes,
        process_data=[
            {'range': '00001-10000'},
            {'range': '10001-20000'},
            {'range': '20001-30000'},
            {'range': '30001-40000'},
            {'range': '40001-50000'},
            {'range': '50001-60000'},
            {'range': '60001-70000'},
            {'range': '70001-80000'},
            {'range': '80001-90000'},
            {'range': '90001-100000'},
        ],
        number_of_processes=10,
        screen_layout=get_screen_layout())


if __name__ == '__main__':
    main()
