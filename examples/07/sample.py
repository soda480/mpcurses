import logging
from time import sleep

from mpcurses import MPcurses
from layout import screen_layout

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


def check_primes(nrange=None):
    range_split = nrange.split('-')
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
            {'nrange': '00001-10000'},
            {'nrange': '10001-20000'},
            {'nrange': '20001-30000'},
            {'nrange': '30001-40000'},
            {'nrange': '40001-50000'},
            {'nrange': '50001-60000'},
            {'nrange': '60001-70000'},
            {'nrange': '70001-80000'},
            {'nrange': '80001-90000'},
            {'nrange': '90001-100000'}
        ],
        screen_layout=screen_layout).execute()


if __name__ == '__main__':

    main()
