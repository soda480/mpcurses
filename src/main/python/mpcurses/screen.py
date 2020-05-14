
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
        curses.init_pair(index + 1, index, -1)


def initialize_screen(screen, screen_layout):
    """ initialize screen
    """
    if not screen:
        return

    logger.debug('initializing screen')
    initialize_colors()
    curses.curs_set(0)

    # create window objects
    windows = {}
    for item, data in screen_layout.items():
        if data.get('window'):
            windows[item] = curses.newwin(data['height'], data['width'], data['begin_y'], data['begin_x'])

    # assign window objects
    for item, data in screen_layout.items():
        window_id = data.get('window_id')
        if window_id:
            data['_window'] = windows[window_id]
        else:
            if data.get('window'):
                if item != 'default':
                    continue
            data['_window'] = windows['default']

    for item, data in screen_layout.items():
        if data.get('text') and item != 'counter':
            args = list(data['position'])
            args.append(data['text'])
            args.append(curses.color_pair(data['text_color']))
            data['_window'].addstr(*args)
        if data.get('number'):
            data['_window'].addstr(data['position'][0], data['position'][1] + len(data['text']) + 1, '0')

    screen.refresh()
    for window_id, window in windows.items():
        window.refresh()


def finalize_screen(screen, screen_layout):
    """ finalize screen
    """
    if not screen:
        return

    window = screen_layout['default']['_window']

    window.move(0, 0)
    window.clrtoeol()

    for item, data in screen_layout.items():
        if data.get('clear_end'):
            data['_window'].move(*screen_layout[item]['position'])
            data['_window'].clrtoeol()

    window.addstr(0, 0, '[Press q to exit]', curses.color_pair(12))

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
    for category, category_data in screen_layout.items():
        regex = category_data.get('regex')
        if regex:
            match = re.match(regex, message)
            if match:
                value = None
                if match.groups():
                    value = match.group('value')
                    if len(value) > 100:
                        value = value[0:100] + '...'

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
    else:
        return len(text) + 1


def update_screen(message, screen, screen_layout):
    """ update screen with message as dictated by screen layout

        gets list of categories from screen layout that match the message (via regex)
        iterates through the matching categories and executes display as dictated by
        the category
    """
    if not screen:
        return

    # strip offset from message
    offset, sanitized_message = sanitize_message(message)
    category_values = get_category_values(sanitized_message, screen_layout)
    if not category_values:
        return

    try:
        for category_value in category_values:
            category = category_value[0]
            value = category_value[1]

            # use category to lookup screen meta-data
            window = screen_layout[category]['_window']
            position = screen_layout[category].get('position', (None, None))
            y_pos = position[0]
            x_pos = position[1]
            if screen_layout[category].get('text', ''):
                x_pos = x_pos + get_position(screen_layout[category]['text']) + 1
            color = screen_layout[category].get('color', 0)

            # process keep_count flag
            if 'keep_count' in screen_layout[category]:
                if 'offset' in screen_layout[category]:
                    soffset = str(offset)
                    if soffset in screen_layout[category]['offset']:
                        screen_layout[category]['offset'][soffset] += 1
                    else:
                        screen_layout[category]['offset'][soffset] = 1
                    value = str(screen_layout[category]['offset'][soffset])
                else:
                    screen_layout[category]['count'] += 1
                    value = str(screen_layout[category]['count'])

            # process effects
            effects = screen_layout[category].get('effects', {})
            if effects:
                for effect in effects:
                    match = re.match(effect['regex'], sanitized_message)
                    if match:
                        color = effect['color']

            if 'replace_text' in screen_layout[category]:
                value = screen_layout[category]['replace_text']

            # process table flag
            if 'table' in screen_layout[category]:
                y_pos = y_pos + offset

            # process clear flag
            if screen_layout[category].get('clear', False):
                window.move(y_pos, x_pos)
                window.clrtoeol()

            # update screen
            if value:
                window.addstr(y_pos, x_pos, value, curses.color_pair(color))

            # process counter flag
            if 'counter' in screen_layout:
                if category in screen_layout['counter']['categories']:
                    counter_y_pos = screen_layout['counter']['position'][0]
                    counter_x_pos = screen_layout['counter']['ticker']
                    screen_layout['counter']['ticker'] += 1
                    counter_value = screen_layout['counter']['text']
                    counter_color = screen_layout[category]['color']
                    window.addstr(counter_y_pos, counter_x_pos, counter_value, curses.color_pair(counter_color))

            window.refresh()

    except curses.error:
        # need to figure out why so many: wmove() returned ERR
        pass


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
        screen.addstr(0, 0, ' RUNNING ', curses.color_pair(12))
        return

    current_time = time()
    if blink_meta['blink_on']:
        _, seconds = divmod((current_time - blink_meta['blink_on_time']), 60)
        if seconds > .7:
            screen.addstr(0, 0, ' RUNNING ', curses.color_pair(1))
            blink_meta['blink_on'] = False
            blink_meta['blink_off_time'] = current_time
    else:
        _, seconds = divmod((current_time - blink_meta['blink_off_time']), 60)
        if seconds > .7:
            screen.addstr(0, 0, ' RUNNING ', curses.color_pair(12))
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
