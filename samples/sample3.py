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
    for offset, bay in enumerate(bays):
        servers.append({
            'offset': offset,
            'bay': bay,
            'servername': 'server-{}.company.com'.format(get_hex()[0:4]),
        })
    return servers


def update_firmware(bay_number, servername, image_url, firmware_version):
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

    logger.debug('firmware version for bay {} is "{}"'.format(bay_number, firmware_version))


@queue_handler
def process_update(data, shared_data):
    bay_number = str(data['bay'])
    servername = data['servername']
    image_url = shared_data['image_url']
    logger.debug('executing process upgrade for data {} shared data {}'.format(data, shared_data))
    acronym = 'HPIP'
    version = '2.64'

    try:
        logger.info('executing {} v{} firmware update on server at bay {}'.format(acronym.upper(), version, bay_number))
        update_firmware(bay_number, servername, image_url, version)
        logger.debug('{} v{} firmware update on server at bay {} was successful'.format(acronym.upper(), version, bay_number))

    except Exception as exception:
        error_message = str(exception)
        logger.error(error_message)

    finally:
        logger.debug('processing next bay')

    logger.info('completed firmware update on all servers')


def get_screen_map():
    return {
        'default': {
            'window': True,
            'begin_y': 0,
            'begin_x': 0,
            'height': 21,
            'width': 300
        },
        'window_legend': {
            'window': True,
            'begin_y': 22,
            'begin_x': 0,
            'height': 3,
            'width': 300
        },
        'legend_s1': {
            'text': 'WRN: # of warnings that occurred during a step in the upgrade process',
            'text_color': 243,
            'position': (0, 0),
            'window_id': 'window_legend'
        },
        'procs_active': {
            'text': 'Active: 0',
            'text_color': 245,
            'color': 7,
            'position': (1, 1),
            'regex': '^mpcurses: number of active processes (?P<value>\d+)$',
            'window_id': 'window_legend'
        },
        'procs_queued': {
            'text': 'Queued: 0',
            'text_color': 245,
            'color': 7,
            'position': (1, 20),
            # 'clear': True,
            'regex': '^mpcurses: number of queued processes (?P<value>\d+)$',
            'window_id': 'window_legend'
        },
        'procs_complete': {
            'text': 'Completed: 0',
            'text_color': 245,
            'color': 7,
            'position': (1, 39),
            'count': 0,
            'keep_count': True,
            'regex': '^mpcurses: a process has completed$',
            'window_id': 'window_legend'
        },
        'status': {
            'text': '',
            'color': 31,
            'position': (2, 1),
            'clear': True,
            'regex': '^INFO: (?P<value>.*)$'
        },
        'bay_header': {
            'text': 'Bay',
            'text_color': 243,
            'position': (3, 2)
        },
        'server_header': {
            'text': 'Server Name',
            'text_color': 243,
            'position': (3, 7)
        },
        'firmware_header': {
            'text': 'F/W',
            'text_color': 243,
            'position': (3, 34)
        },
        'warning_header': {
            'text': 'WRN',
            'text_color': 243,
            'position': (3, 41)
        },
        'message_header': {
            'text': 'Status',
            'text_color': 243,
            'position': (3, 48)
        },
        '_indicator_on': {
            'text': '',
            'replace_text': '->',
            'color': 15,
            'position': (4, 0),
            'regex': '^.* executing .* firmware update on server at bay .*$',
            'table': 'bay_table'
        },
        '_indicator_off': {
            'text': '',
            'replace_text': '  ',
            'position': (4, 0),
            'regex': '^processing next bay$',
            'table': 'bay_table'
        },
        'bay': {
            'text': '',
            'color': 0,
            'position': (4, 2),
            'regex': '^servername for bay (?P<value>\d+) is .*$',
            'table': 'bay_table'
        },
        'server': {
            'text': '',
            'color': 0,
            'position': (4, 7),
            'regex': '^servername for bay \d+ is "(?P<value>.*)"$',
            'table': 'bay_table'
        },
        'firmware': {
            'text': '',
            'color': 0,
            'position': (4, 34),
            'regex': '^firmware version for bay \d+ is "(?P<value>.*)"$',
            'effects': [
                {
                    'regex': '.*2.64.*$',
                    'color': 3
                }
            ],
            'table': 'bay_table'
        },
        'warning': {
            'text': '',
            'color': 4,
            'position': (4, 41),
            'keep_count': True,
            'regex': '^WARN:.*$',
            'offset': {},
            'table': True,
        },
        'message': {
            'text': '',
            'color': 0,
            'position': (4, 48),
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
            'table': 'bay_table'
        }
    }


def get_current_firmware():

    return random.choice(['1.01', '2.01', '2.00', '2.02', '2.03', '2.04', '2.05', '2.06'])


def get_messages(servers):
    messages = []
    for server in servers:
        offset = server['offset']
        bay = server['bay']
        servername = server['servername']
        messages.append('#{}-servername for bay {} is "{}"'.format(
            offset, bay, servername))
        messages.append('#{}-firmware version for bay {} is "{}"'.format(
            offset, bay, get_current_firmware()))
        messages.append('#{}-'.format(offset))
    return messages


def main():
    """ main program
    """
    bays = range(1,17)
    servers = get_servers(bays)
    execute(
        function=process_update,
        process_data=[
            (server['offset'], server) for server in servers
        ],
        shared_data={
            'image_url': '-some-image-url-',
            'novc': False,
            'messages': get_messages(servers)
        },
        number_of_processes=5,
        screen_layout=get_screen_map())


if __name__ == '__main__':
    main()
