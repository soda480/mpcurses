
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
import sys
from curses import wrapper
from multiprocessing import Queue
from multiprocessing import Process
from queue import Queue as SimpleQueue
from queue import Empty
from datetime import datetime

from .screen import initialize_screen
from .screen import finalize_screen
from .screen import update_screen
from .screen import blink_running
from .screen import echo_to_screen
from .screen import refresh_screen

import logging
from logging import Handler

logger = logging.getLogger(__name__)


def setup_process_queue(process_offset_data):
    """ return queue containing data for each process

        Parameters:
            process_offset_data (list): list of lists containing an offset and dictionary of meta-data specific to spawned process at offset
                [[0, {}], [1, {}], [2, {}]]
        Returns:
            queue: queue containing process data for all processes that need to be started
    """
    queue = SimpleQueue()
    logger.debug('populating the process queue')
    for item in process_offset_data:
        logger.debug('adding {} to the process queue'.format(item))
        queue.put(item)
    logger.debug('added {} items to the process queue'.format(queue.qsize()))
    return queue


def start_process(function, shared_data, message_queue, process_offset_data, active_processes, result_queue):
    """ start background process and update active processes dictionary with the process meta-data for the respective process offset

        process target is function - callable object to be invoked

        each process will be started with the following arguments:
            process_data - data specific to the process at offset
            shared_data - data given to all processes

        each process will be started with the following key word arguments:
            message_queue - thread-safe message queue that the process can use to send messages back to the controller
            offset - integer value representing the offset for the process
            result_queue - thread-safe queue were results of process will be stored

        Parameters:
            function (callable): callable object that each spawned process will execute as their target
            shared_data (dict): data to provide all spawned processes
            message_queue (queue): thread-safe queue to serve as message queue between main process and spawned processes
            process_offset_data (list): respresent process offset and data to send spawned process
            active_processes (dict): dictionary maintaining meta-data about all active processes
                will be updated with process meta-data for respective process offset
            result_queue (Queue): thread-safe queue were process results will be stored
        Returns:
            None
    """
    process_offset = process_offset_data[0]
    process_data = process_offset_data[1]
    process = Process(
        target=function,
        args=(process_data, shared_data),
        kwargs={
            'message_queue': message_queue,
            'offset': process_offset,
            'result_queue': result_queue
        })
    logger.debug('starting background process for offset {} with data {}'.format(process_offset, process_data))
    process.start()
    logger.info('started background process for offset {} with process id {}'.format(process_offset, process.pid))
    # update active_processes dictionary with process meta-data for respective process offset
    active_processes[str(process_offset)] = process


def start_processes(function, shared_data, processes_to_start, process_queue, active_processes, result_queue):
    """ start background processes

        Parameters:
            function (callable): callable object that each spawned process will execute as their target
            shared_data (dict): data to provide all spawned processes
            processes_to_start (int): number of processes to spawn
            process_queue (queue): queue representing all processes that need to be started - contains offset and process data for each process
            active_processes (dict): dictionary maintaining meta-data about all active processes
            result_queue (Queue): thread-safe queue were process results will be stored
        Returns:
            queue: thread-safe queue to serve as message queue between main process and spawned processes
    """
    logger.debug('there are {} items in the process queue'.format(process_queue.qsize()))
    message_queue = Queue()
    logger.debug('starting {} background processes'.format(processes_to_start))
    for _ in range(processes_to_start):
        if process_queue.empty():
            logger.debug('the process queue is empty - no more processes need to be started')
            break
        # pop item off of the process_queue - process offset data will be passed to process that is started
        start_process(function, shared_data, message_queue, process_queue.get(), active_processes, result_queue)
    logger.info('started {} background proceses'.format(len(active_processes)))
    return message_queue


def send_process_state(active_processes, process_queue, screen, screen_layout, process_completed=False):
    """ send message regarding processes state
    """
    update_screen('mpcurses: number of active processes {}'.format(str(len(active_processes)).zfill(3)), screen, screen_layout)
    update_screen('mpcurses: number of queued processes {}'.format(str(process_queue.qsize()).zfill(3)), screen, screen_layout)
    if process_completed:
        update_screen('mpcurses: a process has completed', screen, screen_layout)


def _execute(screen, function, process_data, shared_data, number_of_processes, init_messages, screen_layout, active_processes, result_queue):
    """ private execute api

        spawns child processes as dictated by process_data and manages displaying spawned process messages to screen if screen_layout is defined
        the called function is defined by the caller and must be wrapped with a queue handler
        the decorator will send all log messages to the message queue to be processed.

        Parameters:
            screen (object): wrapped mpcurses
            function (callable): callable object that each spawned process will execute as their target
            process_data (list): list of tuples containing an offset and dictionary of meta-data specific to spawned process at offset
                [ (0, {}), (1, {}), (2, {}) ]
            shared_data (dict): data to provide all spawned processes
            number_of_processes (int): number of processes to spawn
            init_messages (list): list of initialization messages to send screen
            screen_layout (dict): dictionary containing meta-data for how logged messages for each spawned process should be displayed on screen
            active_processes (dict): dictionary maintaining meta-data about all active processes
            result_queue (Queue): thread-safe queue were process results will be stored
        Returns:
            None
    """
    initialize_screen(screen, screen_layout, len(process_data))

    for init_message in init_messages:
        update_screen(init_message, screen, screen_layout)
    for index, data in enumerate(process_data):
        echo_to_screen(screen, data[1], screen_layout, offset=index)
    echo_to_screen(screen, shared_data, screen_layout)

    process_queue = setup_process_queue(process_data)
    message_queue = start_processes(function, shared_data, number_of_processes, process_queue, active_processes, result_queue)

    # TODO: figure a better way to send process data
    send_process_state(active_processes, process_queue, screen, screen_layout)

    blink_meta = {}
    while True:
        try:
            blink_running(screen, blink_meta)

            message = message_queue.get(False)
            match = re.match(r'^#(?P<offset>\d+)-(?P<control>DONE|ERROR)$', message)
            if match:
                offset = match.group('offset')
                control = match.group('control')

                if control == 'DONE':
                    process = active_processes.pop(offset, None)
                    logger.info('process with offset {} process id {} has completed'.format(offset, process.pid if process else '-'))
                    send_process_state(active_processes, process_queue, screen, screen_layout, process_completed=True)

                    if process_queue.qsize() == 0:
                        logger.info('the to process queue is empty')
                        if not active_processes:
                            logger.info('there are no more active processses - quitting')
                            break
                    else:
                        # we still have items in the process_queue lets start them
                        start_process(function, shared_data, message_queue, process_queue.get(), active_processes, result_queue)

                    send_process_state(active_processes, process_queue, screen, screen_layout)
                else:
                    logger.info('error detected for process with offset {} - purging all items from the to process queue'.format(offset))
                    while not process_queue.empty():
                        logger.info('purged {} from the to process queue'.format(process_queue.get()))
            else:
                update_screen(message, screen, screen_layout)

        except Empty:
            # queue.Empty exception is raised when nothing is in the multiprocessing message queue
            refresh_screen(screen)

    update_screen('mpcurses: Ended:{}'.format(datetime.now().strftime('%m/%d/%Y %H:%M:%S')), screen, screen_layout)
    finalize_screen(screen, screen_layout)


def terminate_processes(active_processes):
    """ terminate active processes
    """
    for offset, process in active_processes.items():
        logger.info('killing process for offset {} with process id {}'.format(offset, process.pid))
        process.terminate()


def update_result(process_data, result_queue):
    """ populate process data with data from result queue
    """
    while True:
        try:
            item = result_queue.get(False)
            for offset, result in item.items():
                logger.debug('adding result of process with offset {}'.format(offset))
                process_data[int(offset)]['result'] = result
        except Empty:
            break


def validate_process_data(processes, table):
    """ validate wraparound table
    """
    if not table:
        return
    entries = table.get('rows', 0) * table.get('cols', 0)
    if processes > entries:
        raise Exception(f'table definition of {entries} entries not sufficient for {processes} processes')


def execute(function=None, process_data=None, shared_data=None, number_of_processes=None, init_messages=None, screen_layout=None):
    """ public execute api - spawns child processes as dictated by process data and manages displaying spawned process messages to screen if screen layout is defined

        wrapped with KeyboardInterrupt exception to enable user to submit Ctrl+C interrupt to kill all running processes
        supports 'silent mode' if caller does not specify a screen layout

        Parameters:
            function (callable): callable object that each spawned process will execute as their target
            process_data (list): list of dict where each dict contains meta-data specific to a process
                [{}, {}, {}]
            shared_data (dict): data to provide all spawned processes
            number_of_processes (int): number of processes to spawn
            init_messages (list): list of messages to send screen upon startup
            screen_layout (dict): dictionary containing meta-data for how logged messages for each spawned process should be displayed on screen
        Returns:
            int: -1 if user initiated keyboard interrupt to kill processes (Ctrl+C)
    """
    if not process_data:
        process_data = [{}]
    if not shared_data:
        shared_data = {}
    if not init_messages:
        init_messages = []
    active_processes = {}
    process_data_offset = [
        (process_data.index(item), item) for item in process_data
    ]
    result_queue = Queue()
    try:
        if screen_layout:
            validate_process_data(len(process_data), screen_layout.get('_table'))
            wrapper(
                _execute,
                function,
                process_data_offset,
                shared_data,
                number_of_processes,
                init_messages,
                screen_layout,
                active_processes,
                result_queue)
        else:
            _execute(
                None,
                function,
                process_data_offset,
                shared_data,
                number_of_processes,
                init_messages,
                None,
                active_processes,
                result_queue)

        update_result(process_data, result_queue)

    except KeyboardInterrupt:
        logger.info('Keyboard Interrupt signal received - killing all active processes')
        terminate_processes(active_processes)
        sys.exit(-1)
