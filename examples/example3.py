import logging
from time import sleep

from mpcurses import MPcurses
from screen_layouts.example3_sl import get_screen_layout

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


def main():
    MPcurses(
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
            {'range': '90001-100000'}
        ],
        screen_layout=get_screen_layout()).execute()


if __name__ == '__main__':

    main()
