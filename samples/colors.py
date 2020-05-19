# Sample - Prime Number Counter

from mpcurses import queue_handler
from mpcurses import execute

from time import sleep
import logging
logger = logging.getLogger(__name__)


@queue_handler
def noop(*args):
    pass


def get_screen_layout():
    layout = {
        'default': {
            'window': True,
            'begin_y': 0,
            'begin_x': 0,
            'height': 200,
            'width': 200
        }
    }
    y_pos = 2
    x_pos = 0
    for index in range(0, 256):
        count = index + 1
        text = 'color{}'.format(str(index).zfill(3))
        layout[text] = {
            'position': (y_pos, x_pos),
            'text': text,
            'text_color': index 
        }
        if count % 12 == 0:
            y_pos += 1
            x_pos = 0
        else:
            x_pos = x_pos + len(text) + 2
    return layout


def main():
    execute(
        function=noop,
        process_data=[
            {}
        ],
        number_of_processes=1,
        screen_layout=get_screen_layout())


if __name__ == '__main__':
    main()
