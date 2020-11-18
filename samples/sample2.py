import sys
import random
import namegenerator
import logging
from time import sleep

from mpcurses import MPcurses
from sample2_sl import get_screen_layout


logger = logging.getLogger(__name__)


def get_items():
    items = []
    for count in range(0, 1000):
        items.append(namegenerator.gen())
    return items


def process_items():
    items = get_items()
    logger.debug(f'{len(items)} total items')
    for item in items:
        logger.debug(f'processing item "{item}"')
        # simulate work being done
        sleep(random.choice([0.015]))
        if item.count('e') > 4:
            # simulate warning
            logger.debug(f'warning processing item "{item}"')
        elif item.count('g') > 3:
            # simulate error
            logger.debug(f'error processing item "{item}"')
        else:
            # simulate success
            logger.debug(f'item "{item}" was processed')      
    logger.debug('processing complete')


def process_worker(*args):

    process_items()


def main():
    MPcurses(
        function=process_worker,
        screen_layout=get_screen_layout()).execute()


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'simple':
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
        process_items()
    else:
        main()
