import logging
logger = logging.getLogger(__name__)

def is_prime(num):
    if num == 1:
        return False
    for i in range(2, num):
        if (num % i) == 0:
            break
    else:
        return True

def count_primes(*args):
    range_split = args[0]['range'].split('-')
    lower = int(range_split[0])
    upper = int(range_split[1])
    logger.debug(f'checking primes between {lower}/{upper}')
    primes = []
    for number in range(lower, upper + 1):
        logger.debug(f'checking number {number}')
        if is_prime(number):
            logger.debug(f'{number} is prime')
            primes.append(number)
    return len(primes)
