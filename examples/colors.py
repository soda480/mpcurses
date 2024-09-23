# Sample - Prime Number Counter

# from mpcurses import queue_handler
from mpcurses import MPcurses

from time import sleep
import logging
logger = logging.getLogger(__name__)


def noop(*args):
    pass


def get_screen_layout():
    layout = {}
    y_pos = 2
    x_pos = 0
    for index in range(0, 2800):
        count = index + 1
        text = 'color{}'.format(str(index).zfill(4))
        layout[text] = {
            'position': (y_pos, x_pos),
            'text': text,
            'text_color': index 
        }
        if count % 32 == 0:
            y_pos += 1
            x_pos = 0
        else:
            x_pos = x_pos + len(text) + 2
    return layout


def main():
    MPcurses(
        function=noop,
        process_data=[{}],
        processes_to_start=1,
        screen_layout=get_screen_layout())


if __name__ == '__main__':
    main()
