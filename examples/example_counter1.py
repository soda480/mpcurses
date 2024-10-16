# counter example

import namegenerator
import logging
from time import sleep
from mpcurses import MPcurses
from screen_layouts.example_counter import screen_layout

logger = logging.getLogger(__name__)

def get_items():
    items = []
    for count in range(0, 1000):
        items.append(namegenerator.gen())
    return items

def do_work(*args):
    items = get_items()
    logger.debug(f'{len(items)} total items')
    for item in items:
        logger.debug(f'processing item "{item}"')
        sleep(.015)
        if item.count('e') > 4:
            logger.debug(f'warning processing item "{item}"')
        elif item.count('g') > 3:
            logger.debug(f'error processing item "{item}"')
        else:
            logger.debug(f'item "{item}" was processed')      
    logger.debug('processing complete')

def main():
    MPcurses(
        function=do_work,
        screen_layout=screen_layout).execute()

if __name__ == '__main__':
        main()
