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
    logger.debug('total of {} numbers'.format(upper - lower))
    for number in range(lower, upper):
        logger.debug('checking {}/{}'.format(str(number).zfill(6), str(range_split[1]).zfill(6)))
        if is_prime(number):
            logger.debug('prime')
        else:
            logger.debug('not prime')


def get_screen_layout():
    return {
        'number_header': {
            'position': (2, 4),
            'text': 'Number',
            'text_color': 14,
        },
        'prime_header': {
            'position': (2, 15),
            'text': 'Prime :',
            'text_color': 14,
        },
        'not_prime_header1': {
            'position': (1, 22),
            'text': 'Not',
            'text_color': 14,
        },
        'not_prime_header2': {
            'position': (2, 21),
            'text': 'Prime',
            'text_color': 14,
        },
        'number': {
            'position': (3, 1),
            'text': '',
            'color': 27,
            'regex': '^checking (?P<value>\d+)/\d+$',
            'table': True
        },
        'uppper_number': {
            'position': (3, 7),
            'text': '',
            'color': 15,
            'regex': '^checking \d+(?P<value>/\d+)$',
            'table': True
        },
        'prime': {
            'position': (3, 15),
            'text': '',
            'color': 2,
            'keep_count': True,
            'zfill': 5,
            'regex': '^prime$',
            'table': True
        },
        'not_prime': {
            'position': (3, 21),
            'text': '',
            'color': 3,
            'keep_count': True,
            'regex': '^not prime$',
            'zfill': 5,
            'table': True
        },
        '_counter_': {
            'position': (3, 27),
            'categories': [
                'number'
            ],
            'counter_text': '|',
            'modulus': 200,
            'color': 15,
            # 'regex': '^total of (?P<value>\d+) numbers$',
            'table': True
        },
        'total_header': {
            'position': (14, 8),
            'text': 'Total:',
            'text_color': 14,
        },
        'prime_total': {
            'position': (14, 15),
            'text': '',
            'color': 2,
            'keep_count': True,
            'zfill': 5,
            'regex': '^prime$',
        },
        'not_prime_total': {
            'position': (14, 21),
            'text': '',
            'color': 3,
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
