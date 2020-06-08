# Sample - Prime Number Counter

from mpcurses import queue_handler
from mpcurses import execute
from queue import Empty

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
    primes = []
    range_split = data['range'].split('-')
    lower = int(range_split[0])
    upper = int(range_split[1]) + 1
    logger.debug('total of {} numbers'.format(upper - lower))
    for number in range(lower, upper):
        logger.debug('checking {}/{}'.format(str(number).zfill(6), str(range_split[1]).zfill(6)))
        if is_prime(number):
            logger.debug('prime')
            primes.append(number)
        else:
            logger.debug('not prime')
    return primes


def main():
    process_data = [
        {'range': '00001-10000'},
        {'range': '10001-20000'},
        {'range': '20001-30000'}
    ]
    print('running...')
    execute(
        function=check_primes,
        process_data=process_data,
        number_of_processes=3)

    for process in process_data:
        print('{}: has {} primes'.format(
            process['range'], len(process['result'])))


if __name__ == '__main__':
    main()
