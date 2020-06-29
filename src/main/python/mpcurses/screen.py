
# Copyright (c) 2020 Intel Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import curses
from time import time

import logging
from logging import Handler

logger = logging.getLogger(__name__)


def initialize_colors():
    """ initialize colors
    """
    curses.start_color()
    curses.use_default_colors()
    for index in range(0, curses.COLORS):
        curses.init_pair(index, index, -1)
    curses.init_pair(232, 16, 226)  # black/yellow
    curses.init_pair(233, 15, 136)  # white/brown
    curses.init_pair(234, 16, 51)  # black/cyan
    curses.init_pair(235, 15, 19)  # white/blue
    curses.init_pair(236, 15, 240)  # white/grey
    curses.init_pair(237, 15, 160)  # white/red
    curses.init_pair(238, 16, 15)  # black/white
    curses.init_pair(239, 15, 23)  # white/green


def create_default_window(screen_layout):
    """ create default window
    """
    screen_layout['default'] = {
        'window': True,
        'begin_y': 0,
        'begin_x': 0,
        'height': 20,
        'width': 200
    }


def create_windows(screen_layout):
    """ create windows objects and return dict of categories of window objects
    """
    if 'default' not in screen_layout:
        create_default_window(screen_layout)
    windows = {}
    for category, data in screen_layout.items():
        if data.get('window'):
            windows[category] = curses.newwin(data['height'], data['width'], data['begin_y'], data['begin_x'])
    return windows


def assign_windows(windows, screen_layout):
    """ assign window to categories in screen layout
    """
    for category, data in screen_layout.items():
        window_id = data.get('window_id')
        if window_id:
            data['_window'] = windows[window_id]
        else:
            data['_window'] = windows['default']


def refresh_windows(windows):
    """ refresh windows
    """
    for _, window in windows.items():
        window.refresh()


def initialize_counter(offsets, screen_layout):
    """ initialize _counter_ category

        '_counter_': {
            0: {
                '_count': 0,
                '_modulus_count': 0
            },
            1: {
                '_count': 0,
                '_modulus_count': 0
            }
        }
    """
    for offset in range(0, offsets):
        screen_layout['_counter_'][offset] = {}
        screen_layout['_counter_'][offset]['_count'] = 0
        if 'modulus' in screen_layout['_counter_']:
            screen_layout['_counter_'][offset]['_modulus_count'] = 0


def initialize_text(offsets, category, screen_layout):
    """ initialize screen for categories containing text
    """
    category_data = screen_layout[category]
    window = category_data['_window']
    if category_data.get('table'):
        for offset in range(0, offsets):
            window.addstr(
                get_category_y_pos(category, offset, screen_layout),
                get_category_x_pos(category, offset, screen_layout),
                category_data['text'],
                curses.color_pair(category_data['text_color']))
    else:
        window.addstr(
            category_data['position'][0],
            category_data['position'][1],
            category_data['text'],
            curses.color_pair(category_data['text_color']))


def initialize_keep_count(category, offsets, screen_layout):
    """ initialize category keep_count

        per process:
            'category1': {
                0: {
                    '_count': 0
                },
                1: {
                    '_count': 0
                }
            }
        per execution:
            'category1' : {
                '_count': 0
            }
    """
    if screen_layout[category].get('table'):
        for offset in range(0, offsets):
            screen_layout[category][offset] = {}
            screen_layout[category][offset]['_count'] = 0
    else:
        screen_layout[category]['_count'] = 0


def initialize_screen(screen, screen_layout, offsets):
    """ initialize screen
    """
    if not screen:
        return

    logger.debug('initializing screen')
    initialize_colors()
    curses.curs_set(0)

    windows = create_windows(screen_layout)
    assign_windows(windows, screen_layout)

    for category, data in screen_layout.items():
        if category == '_counter_':
            initialize_counter(offsets, screen_layout)
        if data.get('text'):
            initialize_text(offsets, category, screen_layout)
        if data.get('keep_count'):
            initialize_keep_count(category, offsets, screen_layout)

    screen.refresh()
    refresh_windows(windows)


def finalize_screen(screen, screen_layout):
    """ finalize screen
    """
    if not screen:
        return

    window = screen_layout['default']['_window']

    window.move(0, 0)
    window.clrtoeol()

    for category, data in screen_layout.items():
        if data.get('clear_end'):
            data['_window'].move(*screen_layout[category]['position'])
            data['_window'].clrtoeol()

    window.addstr(0, 0, '[Press q to exit]', curses.color_pair(11))

    window.refresh()
    while True:
        char = window.getch()
        if char == ord('q'):
            curses.curs_set(2)
            return


def get_category_values(message, screen_layout):
    """ return list of tuples consisting of categories and their values from screen layout that match message
    """
    category_values = []
    for category, data in screen_layout.items():
        regex = data.get('regex')
        if regex:
            match = re.match(regex, message)
            if match:
                value = None
                if match.groups():
                    value = match.group('value')
                    value_len = data.get('value_len', 103)
                    if len(value) > value_len:
                        value = value[0:value_len - 3] + '...'
                category_values.append((category, value))
    return category_values


def sanitize_message(message):
    """ return tuple consisting of offset and message
    """
    regex = r'#(?P<offset>\d+)-.*'
    match = re.match(regex, message)
    if match:
        offset = match.group('offset')
        filtered_message = re.sub(r'#{}-'.format(offset), '', message)
        return int(offset), filtered_message
    return 0, message


def get_position(text):
    """ return position where count should start after text
    """
    if ':' in text:
        return text.index(':') + 1
    elif text == len(text) * '-':
        return -1
    else:
        return len(text) + 1


def process_clear(category, y_pos, x_pos, screen_layout):
    """ process clear directive
    """
    if screen_layout[category].get('clear'):
        window = screen_layout[category]['_window']
        window.move(y_pos, x_pos)
        window.clrtoeol()


def process_counter(offset, category, value, screen_layout):
    """ process counter directive
    """
    if '_counter_' not in screen_layout:
        return
    window = screen_layout[category]['_window']
    if category in screen_layout['_counter_']['categories']:
        position = screen_layout['_counter_']['position']
        x_pos = position[1] + screen_layout['_counter_'][offset]['_count']
        y_pos = position[0] + offset
        counter_value = screen_layout['_counter_']['counter_text']
        color = screen_layout[category]['color']
        screen_layout['_counter_'][offset]['_count'] += 1
        if 'modulus' in screen_layout['_counter_']:
            if screen_layout['_counter_'][offset]['_count'] % screen_layout['_counter_']['modulus'] == 0:
                # increments the progress bar
                x_pos = position[1] + screen_layout['_counter_'][offset]['_modulus_count']
                color = screen_layout['_counter_']['color']
                screen_layout['_counter_'][offset]['_modulus_count'] += 1
                x_pos = x_pos + 1 if 'regex' in screen_layout['_counter_'] else x_pos
                window.addstr(y_pos, x_pos, counter_value, curses.color_pair(color))
        else:
            # increments the counter
            if screen_layout['_counter_'].get('width'):
                # width and modulus are mutually exclusive
                width = screen_layout['_counter_']['width']
                count = screen_layout['_counter_'][offset]['_count']
                if count % width == 0:
                    screen_layout['_counter_']['position'] = (position[0] + 1, position[1])
                    screen_layout['_counter_'][offset]['_count'] = 0
            window.addstr(y_pos, x_pos, counter_value, curses.color_pair(color))
    elif category == '_counter_':
        # regex infers progress bar
        # this sets up the progress bar boundary
        position = screen_layout['_counter_']['position']
        color = screen_layout[category]['color']
        span = int(value) / screen_layout['_counter_']['modulus']
        progress_value = '[{}]'.format(' ' * int(span))
        window.addstr(position[0] + offset, position[1], progress_value, curses.color_pair(color))


def get_category_color(category, message, screen_layout):
    """ return color for category in screen layout
    """
    color = screen_layout[category].get('color', 0)
    for effect in screen_layout[category].get('effects', []):
        match = re.match(effect['regex'], message)
        if match:
            color = effect['color']
            break
    return color


def get_category_count(category, offset, screen_layout):
    """ return count for category in screen layout
    """
    zfill = screen_layout[category].get('zfill', 3)
    if screen_layout[category].get('table'):
        screen_layout[category][offset]['_count'] += 1
        return str(screen_layout[category][offset]['_count']).zfill(zfill)
    else:
        screen_layout[category]['_count'] += 1
        return str(screen_layout[category]['_count']).zfill(zfill)


def get_category_value(category, offset, initial_value, screen_layout):
    """ return value for category in screen layout
    """
    value = initial_value
    if screen_layout[category].get('keep_count'):
        value = get_category_count(category, offset, screen_layout)
    if screen_layout[category].get('replace_text'):
        value = screen_layout[category]['replace_text']
    return value


def get_category_x_pos(category, offset, screen_layout):
    """ return x pos for category in screen layout
    """
    x_pos = screen_layout[category]['position'][1]
    if screen_layout[category].get('text', ''):
        x_pos = x_pos + get_position(screen_layout[category]['text']) + 1
    if screen_layout.get('table'):
        rows = screen_layout['table']['rows']
        width = screen_layout['table']['width']
        if offset >= rows:
            x_pos += int(offset / rows) * width
            # logger.debug(f'table offset {offset} x_pos is {x_pos}')
    return x_pos


def get_category_y_pos(category, offset, screen_layout):
    """ return y pos for category in screen layout
    """
    y_pos = screen_layout[category]['position'][0]
    if screen_layout[category].get('table'):
        y_pos += offset
        if screen_layout.get('table'):
            rows = screen_layout['table']['rows']
            if offset >= rows:
                y_pos -= int(offset / rows) * rows
                # logger.debug(f'table offset {offset} y_pos is {y_pos}')
    return y_pos


def update_screen(message, screen, screen_layout):
    """ update screen with message as dictated by screen layout

        gets list of categories from screen layout that match the message (via regex)
        iterates through the matching categories and executes display as dictated by
        the category
    """
    if not screen:
        return

    offset, sanitized_message = sanitize_message(message)
    category_values = get_category_values(sanitized_message, screen_layout)

    try:
        for category_value in category_values:
            category = category_value[0]
            y_pos = get_category_y_pos(category, offset, screen_layout)
            x_pos = get_category_x_pos(category, offset, screen_layout)
            color = get_category_color(category, sanitized_message, screen_layout)
            value = get_category_value(category, offset, category_value[1], screen_layout)

            process_clear(category, y_pos, x_pos, screen_layout)

            window = screen_layout[category]['_window']
            window.addstr(y_pos, x_pos, value, curses.color_pair(color))

            process_counter(offset, category, value, screen_layout)

            window.refresh()

    except Exception as exception:  # curses.error as exception:
        logger.error('error occurred when updating screen: {}'.format(str(exception)))
        # need to figure out why so many: wmove() returned ERR


def blink_running(screen, blink_meta):
    """ blink running message to screen every .7 seconds

        this was implemented to provide a message that continuously blinks a message
        on the screen to indicate that the program is still working
    """
    if not screen:
        return

    if not blink_meta:
        blink_meta['blink_on_time'] = time()
        blink_meta['blink_off_time'] = time()
        blink_meta['blink_on'] = True
        screen.addstr(0, 0, ' RUNNING ', curses.color_pair(11))
        return

    current_time = time()
    if blink_meta['blink_on']:
        _, seconds = divmod((current_time - blink_meta['blink_on_time']), 60)
        if seconds > .7:
            screen.addstr(0, 0, ' RUNNING ', curses.color_pair(16))
            blink_meta['blink_on'] = False
            blink_meta['blink_off_time'] = current_time
    else:
        _, seconds = divmod((current_time - blink_meta['blink_off_time']), 60)
        if seconds > .7:
            screen.addstr(0, 0, ' RUNNING ', curses.color_pair(11))
            blink_meta['blink_on'] = True
            blink_meta['blink_on_time'] = current_time


def echo_to_screen(screen, data, screen_layout, offset=None):
    """ iterate over items in data dict update screen with echo messages in shared data
    """
    if not screen:
        return

    for key, value in data.items():
        message = ''
        if isinstance(value, (int, float, str, bool)):
            message = "'{}' is '{}'".format(key, value)
        elif isinstance(value, (list, dict, tuple)):
            message = "'{}' has {} items".format(key, len(value))
        if offset:
            message = '#{}-{}'.format(offset, message)
        logger.debug(message)
        update_screen(message, screen, screen_layout)
        if offset:
            # send empty message at offset
            update_screen('#{}-'.format(offset), screen, screen_layout)


def refresh_screen(screen):
    """ refresh screen
    """
    if not screen:
        return

    screen.refresh()
