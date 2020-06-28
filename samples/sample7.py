# Sample - Server Bay Firmware Update

from mpcurses import queue_handler
from mpcurses import execute

from datetime import datetime
from time import sleep
from os import getenv
import random
import uuid
import sys

import logging
logger = logging.getLogger(__name__)


def get_hex():
    try:
        return str(uuid.uuid4().get_hex().upper())
    except AttributeError:
        return uuid.uuid4().hex.upper()


def get_servers(bays):
    servers = []
    for bay in bays:
        servers.append({
            'bay': str(bay).zfill(2),
            'firmware version': get_current_firmware(),
            'servername': 'srv{}.company.com'.format(get_hex()[0:6]),
        })
    return servers


def simulate_error(value, message):
    if value > 9:
        raise Exception(message)


def simulate_work(message):
    value = random.choice(range(3, 11))
    sleep(value)
    simulate_error(value, message)


def replace_suffix(message):
    word = message.split(' ')[0]
    new_word = word.replace('ing', '')
    if new_word[-1] in 'y':
        new_word = new_word[:-1] + 'ied'
    else:
        new_word = new_word + 'ed'
    return message.replace(word, new_word)


def execute_task(message):
    logger.debug(message)
    simulate_work(message)
    logger.debug(replace_suffix(message))


def update_server_firmware(bay_number, servername, firmware_version):
    logger.debug('processing bay {} at: {}'.format(bay_number, datetime.now().strftime('%H:%M:%S')))
    execute_task('turning maintenance mode ON for server at bay {}'.format(bay_number))
    execute_task('applying firmware update for server at bay {}'.format(bay_number))
    execute_task('recycling server at bay {}'.format(bay_number))
    execute_task('verifying firmware update for server at bay {}'.format(bay_number))
    logger.debug("'firmware version' is '{}'".format(firmware_version))
    execute_task('turning maintenance mode OFF for server at bay {}'.format(bay_number))


@queue_handler
def update_firmware(process_data, *args):
    bay_number = str(process_data['bay'])
    servername = process_data['servername']
    firmware_version = '2.64'

    sleep(random.choice([.1, .2, .3, .4, .5, .6, .7, .8]))

    logger.debug('executing firmware update on server at bay {}'.format(bay_number))
    update_server_firmware(bay_number, servername, firmware_version)
    logger.debug('firmware update on server at bay {} was successful'.format(bay_number))
    logger.debug('processing next bay')


def get_screen_layout():
    return {
        'legend': {
            'window': True,
            'begin_y': 19,
            'begin_x': 0,
            'height': 5,
            'width': 17
        },
        'process_header': {
            'position': (1, 1),
            'text': 'Processes',
            'text_color': 244,
            'window_id': 'legend'
        },
        'active': {
            'position': (2, 4),
            'text': 'Active: 0',
            'text_color': 15,
            'color': 6,
            'regex': r'^mpcurses: number of active processes (?P<value>\d+)$',
            'effects': [
                {
                    'regex': r'^mpcurses: number of active processes 000$',
                    'color': 15
                }
            ],
            'window_id': 'legend'
        },
        'queued': {
            'position': (3, 4),
            'text': 'Queued: 0',
            'text_color': 15,
            'color': 11,
            'regex': r'^mpcurses: number of queued processes (?P<value>\d+)$',
            'effects': [
                {
                    'regex': r'^mpcurses: number of queued processes 000$',
                    'color': 15
                }
            ],
            'window_id': 'legend'
        },
        'complete': {
            'position': (4, 1),
            'text': 'Completed:',
            'text_color': 15,
            'color': 27,
            'count': 0,
            'keep_count': True,
            'regex': r'^mpcurses: a process has completed$',
            'window_id': 'legend'
        },
        'task_legend': {
            'window': True,
            'begin_y': 19,
            'begin_x': 18,
            'height': 7,
            'width': 50
        },
        'task_header': {
            'position': (1, 0),
            'text': 'Tasks',
            'text_color': 244,
            'window_id': 'task_legend'
        },
        'task1_header': {
            'position': (2, 1),
            'text': '1: turn maintenance mode ON',
            'text_color': 15,
            'window_id': 'task_legend'
        },
        'task2_header': {
            'position': (3, 1),
            'text': '2: apply firmware update',
            'text_color': 15,
            'window_id': 'task_legend'
        },
        'task3_header': {
            'position': (4, 1),
            'text': '3: recycle server',
            'text_color': 15,
            'window_id': 'task_legend'
        },
        'task4_header': {
            'position': (5, 1),
            'text': '4: verify firmware update',
            'text_color': 15,
            'window_id': 'task_legend'
        },
        'task5_header': {
            'position': (6, 1),
            'text': '5: turn maintenance mode OFF',
            'text_color': 15,
            'window_id': 'task_legend'
        },
        'bay_header': {
            'position': (2, 1),
            'text': 'Bay',
            'text_color': 244,
        },
        'server_header': {
            'position': (2, 5),
            'text': 'Server Name',
            'text_color': 244,
        },
        'version_header': {
            'position': (2, 27),
            'text': 'Ver.',
            'text_color': 244,
        },
        'tasks_header1': {
            'position': (1, 32),
            'text': 'Tasks',
            'text_color': 244,
        },
        'tasks_header2': {
            'position': (2, 32),
            'text': '12345',
            'text_color': 244,
        },
        'message_header': {
            'position': (2, 38),
            'text': 'Messages',
            'text_color': 244,
        },
        '_indicator_on': {
            'position': (3, 0),
            'text': '',
            'replace_text': '=>',
            'color': 14,
            'regex': r'^executing firmware update on server at bay \d+$',
            'table': True
        },
        '_indicator_off': {
            'position': (3, 0),
            'text': '',
            'replace_text': '  ',
            'regex': r'^processing next bay$',
            'table': True
        },
        'bay': {
            'position': (3, 2),
            'text': '',
            'color': 243,
            'regex': r"^'bay' is '(?P<value>\d+)'$",
            'table': True
        },
        'servername': {
            'position': (3, 5),
            'text': '',
            'color': 15,
            'regex': r"^'servername' is '(?P<value>.*)'$",
            'table': True
        },
        'version': {
            'position': (3, 27),
            'text': '',
            'color': 243,
            'regex': r"^'firmware version' is '(?P<value>.*)'$",
            'effects': [
                {
                    'regex': r'.*2.64.*$',
                    'color': 2
                }
            ],
            'table': True
        },
        'task1': {
            'position': (3, 32),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*turn.* maintenance mode ON for server at bay \d+$',
            'effects': [
                {
                    'regex': r'^turned maintenance mode ON for server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'task2': {
            'position': (3, 33),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*appl.* firmware update for server at bay \d+$',
            'effects': [
                {
                    'regex': r'^applied firmware update for server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'task3': {
            'position': (3, 34),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*recycl.* server at bay \d+$',
            'effects': [
                {
                    'regex': r'^recycled server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'task4': {
            'position': (3, 35),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*verif.* firmware update for server at bay \d+$',
            'effects': [
                {
                    'regex': r'^verified firmware update for server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'task5': {
            'position': (3, 36),
            'text': '',
            'replace_text': '|',
            'regex': r'^.*turn.* maintenance mode OFF for server at bay \d+$',
            'effects': [
                {
                    'regex': r'^turned maintenance mode OFF for server at bay \d+$',
                    'color': 2
                }, {
                    'regex': r'^ERROR: .*$',
                    'color': 237
                }
            ],
            'table': True
        },
        'message': {
            'position': (3, 38),
            'text': '',
            'color': 14,  # 149,
            'clear': True,
            'regex': r'^(?!mpcurses:.*)(?!processing next bay)(?!DONE)(?!INFO:.*)(?P<value>.*)$',
            'effects': [
                {
                    'regex': r'^ERROR: .*$',
                    'color': 244
                }, {
                    'regex': r'^firmware update on server at bay \d+ was successful$',
                    'color': 15
                }
            ],
            'table': True
        }
    }


def get_current_firmware():

    return random.choice(['1.01', '2.01', '2.00', '2.02', '2.03', '2.04', '2.05', '2.06'])


def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)

    name = 'sample6.log'
    logfile = '{}/{}'.format(getenv('PWD'), name)
    file_handler = logging.FileHandler(logfile)
    file_formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)


def main():
    """ main program
    """
    configure_logging()
    bays = range(1,17)
    process_data = get_servers(bays)
    execute(
        function=update_firmware,
        process_data=process_data,
        number_of_processes=5,
        screen_layout=get_screen_layout())

    if any([process.get('result') for process in process_data]):
        sys.exit(-1)


if __name__ == '__main__':
    main()
