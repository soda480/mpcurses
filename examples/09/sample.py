import sys
import random
import logging
from datetime import datetime
from time import sleep
from faker import Faker
from mpcurses import MPcurses
from layout import screen_layout

logger = logging.getLogger(__name__)

def get_servers(bays=None):
    """ getting server data from enclosure
    """
    servers = []
    for bay in bays:
        servers.append({
            'bay': str(bay).zfill(2),
            'firmware_version': random.choice(['1.01', '2.01', '2.00', '2.02', '2.03', '2.04', '2.05', '2.06']),
            'servername': Faker().name().replace(' ', '').lower() + '.scn.com',
        })
    sleep(3.5)
    return (servers, {'bays': bays, 'derived_key': 'derived_value'})

def execute_task(message):
    message = 'EX5: ' + message
    lookup = {
        'turning': 'turned',
        'applying': 'applied',
        'recycling': 'recycled',
        'verifying': 'verified'
    }
    logger.debug(message)
    # simulate work
    sleep_time = random.choice(range(1, 11))
    sleep(sleep_time)
    # simulate random error
    if sleep_time >= 10:
        raise Exception(message.replace('EX5: ', 'EX5: failed: '))
    # log completed message
    for key, value in lookup.items():
        if key in message:
            logger.debug(message.replace(key, value))
            break

def update_firmware(bay=None, firmware_version=None, servername=None, bays=None, derived_key=None):
    bay_number = str(bay)
    try:
        current_datetime = datetime.now().strftime('%H:%M:%S')
        sleep(random.choice([.1, .2, .3, .4, .5, .6, .7, .8]))
        logger.debug(f'executing firmware update on server at bay {bay_number} at {current_datetime}')

        logger.debug(f"'firmware version' is '{firmware_version}'")
        execute_task(f'turning maintenance mode ON for server at bay {bay_number}')
        execute_task(f'applying firmware update for server at bay {bay_number}')
        execute_task(f'recycling server at bay {bay_number}')
        execute_task(f'verifying firmware update for server at bay {bay_number}')
        logger.debug(f"'firmware version' is '2.64'")
        execute_task(f'turning maintenance mode OFF for server at bay {bay_number}')

        logger.debug(f'EX5: firmware update on server {servername} at bay {bay_number} was successful')
    except Exception as exception:
        logger.error(str(exception))
        return exception
    finally:
        logger.debug('processing next bay')

def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('example5.log')
    file_formatter = logging.Formatter("%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)

def main():
    """ main program
    """
    configure_logging()
    mpcurses = MPcurses(
        function=update_firmware,
        get_process_data=get_servers,
        processes_to_start=5,
        screen_layout=screen_layout,
        shared_data={'bays': range(1, 17)})
    results = mpcurses.execute()
    if any([result for result in results]):
        sys.exit(1)

if __name__ == '__main__':
    main()
