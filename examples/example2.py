import sys
import random
import namegenerator
import logging
from time import sleep

from mpcurses import MPcurses
from screen_layouts.example2_sl import get_screen_layout


logger = logging.getLogger(__name__)


def get_items():
    items = []
    for count in range(0, 1000):
        items.append(namegenerator.gen())
    return items


def _process_items(group):
    items = get_items()
    logger.debug(f'group{group} has {len(items)} total items')
    for item in items:
        logger.debug(f'processing item "group{group}-{item}"')
        # simulate work being done
        sleep(random.choice([0.005]))
        if item.count('e') > 4:
            # simulate warning
            logger.debug(f'warning processing item "group{group}-{item}"')
        elif item.count('g') > 3:
            # simulate error
            logger.debug(f'error processing item "group{group}-{item}"')
        else:
            # simulate success
            logger.debug(f'item "group{group}-{item}" was processed')      
    logger.debug(f'processing complete for group{group}')


def process_items(process_data, *args):
    group = process_data['group']
    _process_items(group)


def main(screen=True):
    screen_layout = None
    if screen:
        screen_layout = get_screen_layout()
    mpcurses = MPcurses(
        function=process_items,
        process_data=[
            {'group': '01'},
            {'group': '02'},
            {'group': '03'}
        ],
        screen_layout=screen_layout)
    mpcurses.execute()


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'simple':
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
        for group in ['01', '02', '03']:
            _process_items(group)
    elif len(sys.argv) == 2 and sys.argv[1] == 'no-screen':
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
        main(screen=False)
    else:
        main()
