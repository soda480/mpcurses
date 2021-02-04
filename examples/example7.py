import sys
import uuid
import random
import logging
from datetime import datetime
from time import sleep
from os import getenv

from mpcurses import MPcurses
from screen_layouts.example7_sl import get_screen_layout

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


def update_firmware(process_data, *args):
    bay_number = str(process_data['bay'])
    servername = process_data['servername']
    firmware_version = '2.64'

    sleep(random.choice([.1, .2, .3, .4, .5, .6, .7, .8]))

    logger.debug('executing firmware update on server at bay {}'.format(bay_number))
    update_server_firmware(bay_number, servername, firmware_version)
    logger.debug('firmware update on server at bay {} was successful'.format(bay_number))
    logger.debug('processing next bay')


def get_current_firmware():

    return random.choice(['1.01', '2.01', '2.00', '2.02', '2.03', '2.04', '2.05', '2.06'])


def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)

    name = 'example7.log'
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
    MPcurses(
        function=update_firmware,
        process_data=process_data,
        processes_to_start=5,
        screen_layout=get_screen_layout()).execute()

    if any([process.get('result') for process in process_data]):
        sys.exit(-1)


if __name__ == '__main__':

    main()
