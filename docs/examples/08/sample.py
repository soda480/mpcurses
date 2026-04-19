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
    primes = []
    range_split = nrange.split('-')
    lower = int(range_split[0])
    upper = int(range_split[1]) + 1
    for number in range(lower, upper):
        logger.debug('checking {}'.format(number))
        # sleep here only to assist in the visualization of screen
        sleep(.0001)
        if is_prime(number):
            logger.debug('prime')
            primes.append(number)
        else:
            logger.debug('not prime')
    return len(primes)


def main():
    MPcurses(
        function=check_primes,
        process_data=[
            {'nrange': '1-10000'}
        ],
        screen_layout=screen_layout).execute()


if __name__ == '__main__':
    main()
