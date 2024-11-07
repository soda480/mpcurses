import sys
import logging

from mpcurses import MPcurses

logger = logging.getLogger(__name__)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)


def is_prime(num):
    if num == 1:
        return False
    for i in range(2, num):
        if (num % i) == 0:
            return False
            break
    else:
        logger.debug(f'{num} is prime')
        return True


def check_primes(nrange=None):
    primes = []
    range_split = nrange.split('-')
    lower = int(range_split[0])
    upper = int(range_split[1]) + 1
    logger.info(f"finding prime numbers in range {nrange}")
    for number in range(lower, upper):
        if is_prime(number):
            primes.append(number)
    return primes


def main():
    process_data = [
        {'nrange': '00001-10000'},
        {'nrange': '10001-20000'},
        {'nrange': '20001-30000'}
    ]
    mpc = MPcurses(
        function=check_primes,
        process_data=process_data,
        processes_to_start=len(process_data))
    results = mpc.execute()

    for index, process in enumerate(process_data):
        print(f"the range {process['nrange']} has {len(results[index])} primes")


if __name__ == '__main__':  

    main()
