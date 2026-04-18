from mpcurses import MPcurses
import namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_something(*args):
    for _ in range(0, 400):
        logger.debug(f'processing item "{namegenerator.gen()}"')
        time.sleep(.01)

MPcurses(
    function=do_something,
    screen_layout={
        'display_item': {
            'position': (1, 1), 'text': 'Processing:', 'text_color': 0, 'color': 14,
            'clear': True, 'regex': r'^processing item "(?P<value>.*)"$'}
    }).execute()

if __name__ == '__main__':
    main()