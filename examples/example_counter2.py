# counter example - with modulus
from example_counter1 import do_work
from mpcurses import MPcurses
from screen_layouts.example_counter import get_screen_layout


def main():
    screen_layout = get_screen_layout()
    screen_layout['_counter_']['modulus'] = 20
    screen_layout['_counter_']['color'] = 7
    MPcurses(function=do_work, screen_layout=screen_layout).execute()


if __name__ == '__main__':
        main()
