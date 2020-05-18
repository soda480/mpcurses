# Sample - Server Bay Firmware Update

from mpcurses import queue_handler
from mpcurses import execute

from datetime import datetime
from time import sleep
import random
import uuid

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
            'bay': bay,
            'firmware version': get_current_firmware(),
            'servername': 'server-{}.company.com'.format(get_hex()[0:4]),
        })
    return servers


def update_bay_firmware(bay_number, servername, firmware_version):
    logger.debug('processing bay {} at: {}'.format(bay_number, datetime.now().strftime('%H:%M:%S')))

    if '0' in servername or '9' in servername or '-4' in servername:
        warnings = random.choice([1, 2])
        for _ in range(1, warnings):
            logger.warn('simulate a warning occurring')

    logger.debug('mounting iso image at bay {}'.format(bay_number))
    sleep(random.choice([2, 3, 8]))

    logger.debug('powering on server at bay {}'.format(bay_number))
    sleep(random.choice([2, 3, 4, 5, 8, 25]))

    logger.debug('executing firmware update on server at bay {}'.format(bay_number))
    sleep(random.choice([0.4, 1, 2, 3, 4, 5, 6, 12, 24]))

    if 'B' in servername:
        raise ValueError('simulate an error occurring')

    if '0' in servername or '9' in servername or '-4' in servername:
        warnings = random.choice([1, 2, 3, 4])
        for _ in range(1, warnings):
            logger.warn('simulate a warning occurring')

    logger.debug("'firmware version' is '{}'".format(firmware_version))


@queue_handler
def update_firmware(process_data, shared_data):
    bay_number = str(process_data['bay'])
    servername = process_data['servername']
    acronym = 'BIOS'
    version = '2.64'

    try:
        logger.debug('executing {} v{} firmware update on server at bay {}'.format(acronym.upper(), version, bay_number))
        update_bay_firmware(bay_number, servername, version)
        logger.debug('{} v{} firmware update on server at bay {} was successful'.format(acronym.upper(), version, bay_number))

    except Exception as exception:
        error_message = str(exception)
        logger.error(error_message)

    finally:
        logger.debug('processing next bay')

    logger.info('completed firmware update on all servers')


def get_screen_layout():
    return {
        'window_legend': {
            'window': True,
            'begin_y': 22,
            'begin_x': 0,
            'height': 3,
            'width': 300
        },
        'legend_s1': {
            'position': (0, 0),
            'text': 'WRN: # of warnings that occurred during a step in the upgrade process',
            'text_color': 243,
            'window_id': 'window_legend'
        },
        'procs_active': {
            'position': (1, 1),
            'text': 'Active: 0',
            'text_color': 245,
            'color': 7,
            'regex': '^mpcurses: number of active processes (?P<value>\d+)$',
            'window_id': 'window_legend'
        },
        'procs_queued': {
            'position': (1, 20),
            'text': 'Queued: 0',
            'text_color': 245,
            'color': 7,
            'regex': '^mpcurses: number of queued processes (?P<value>\d+)$',
            'window_id': 'window_legend'
        },
        'procs_complete': {
            'position': (1, 39),
            'text': 'Completed: 0',
            'text_color': 245,
            'color': 7,
            'count': 0,
            'keep_count': True,
            'regex': '^mpcurses: a process has completed$',
            'window_id': 'window_legend'
        },
        'bay_header': {
            'position': (2, 2),
            'text': 'Bay',
            'text_color': 243,
        },
        'server_header': {
            'position': (2, 7),
            'text': 'Server Name',
            'text_color': 243,
        },
        'firmware_header': {
            'position': (2, 34),
            'text': 'F/W',
            'text_color': 243,
        },
        'warning_header': {
            'position': (2, 41),
            'text': 'WRN',
            'text_color': 243,
        },
        'message_header': {
            'position': (2, 48),
            'text': 'Status',
            'text_color': 243,
        },
        '_indicator_on': {
            'position': (3, 0),
            'text': '',
            'replace_text': '->',
            'color': 15,
            'regex': '^executing .* firmware update on server at bay .*$',
            'table': True
        },
        '_indicator_off': {
            'position': (3, 0),
            'text': '',
            'replace_text': '  ',
            'regex': '^processing next bay$',
            'table': True
        },
        'bay': {
            'position': (3, 2),
            'text': '',
            'color': 0,
            'regex': "^'bay' is '(?P<value>\d+)'$",
            'table': True
        },
        'servername': {
            'position': (3, 7),
            'text': '',
            'color': 0,
            'regex': "^'servername' is '(?P<value>.*)'$",
            'table': True
        },
        'firmware': {
            'position': (3, 34),
            'text': '',
            'color': 0,
            'regex': "^'firmware version' is '(?P<value>.*)'$",
            'effects': [
                {
                    'regex': '.*2.64.*$',
                    'color': 3
                }
            ],
            'table': True
        },
        'warning': {
            'position': (3, 41),
            'text': '',
            'color': 4,
            'keep_count': True,
            'regex': '^WARN:.*$',
            'table': True
        },
        'message': {
            'position': (3, 48),
            'text': '',
            'color': 0,
            'clear': True,
            'regex': '^(?!mpcurses:.*)(?!processing next bay)(?!DONE)(?!INFO:.*)(?P<value>.*)$',
            'effects': [
                {
                    'regex': '.*firmware update on server at bay .* was successful$',
                    'color': 3
                }, {
                    'regex': '.* failed.*',
                    'color': 2
                }, {
                    'regex': '^ERROR.*$',
                    'color': 2
                }
            ],
            'table': True
        }
    }


def get_current_firmware():

    return random.choice(['1.01', '2.01', '2.00', '2.02', '2.03', '2.04', '2.05', '2.06'])


def main():
    """ main program
    """
    bays = range(1,17)
    servers = get_servers(bays)
    execute(
        function=update_firmware,
        process_data=servers,
        number_of_processes=5,
        screen_layout=get_screen_layout())


if __name__ == '__main__':
    main()
