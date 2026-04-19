from mpcurses import MPcurses
from time import sleep
import logging
import uuid
import random

logger = logging.getLogger(__name__)

def do_work(worker_id=None, num_items=None):
    logger.debug(f'worker {worker_id} will process {num_items} items')
    for _ in range(num_items):
        logger.debug(f'processing item "{uuid.uuid4()}"')
        sleep(.01)

def main():
    MPcurses(
        function=do_work,
        process_data=[{'worker_id': f'Worker-{i}', 'num_items': random.randint(100, 200)} for i in range(3)],
        screen_layout={
            'worker': {'position': (1, 1), 'color': 2, 'table': True, 'clear': True, 'regex': r'^worker (?P<value>.*) will process \d+ items$'},
            'num_items': {'position': (1, 10), 'color': 4, 'table': True, 'clear': True, 'regex': r'^worker .* will process (?P<value>\d+) items$'},
            'item': {'position': (1, 14), 'color': 6, 'table': True, 'clear': True, 'regex': r'^processing item "(?P<value>.*)"$'},
        }).execute()

if __name__ == '__main__':
    main()
