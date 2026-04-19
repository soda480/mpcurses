from mpcurses import MPcurses
import logging

logger = logging.getLogger(__name__)

def noop(arg1=None):
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
        process_data=[{'arg1': 'value1'}],
        # processes_to_start=1,
        screen_layout=get_screen_layout()).execute()


if __name__ == '__main__':
    main()
