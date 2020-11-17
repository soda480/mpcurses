
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
import logging
from datetime import datetime
from curses import wrapper
from multiprocessing import Queue
from multiprocessing import Process
from queue import Queue as SimpleQueue
from queue import Empty

from .screen import initialize_screen
from .screen import finalize_screen
from .screen import update_screen
from .screen import blink_running
from .screen import echo_to_screen
from .screen import refresh_screen
from .screen import validate_screen_layout
from .handler import queue_handler

logger = logging.getLogger(__name__)


class NoActiveProcesses(Exception):
    """ Raise when NoActiveProcesses is used to signal end
    """
    pass


class OnDict(dict):
    """ subclass dict to execute method when items are added or removed changes
    """
    def __init__(self, on_change=None):
        """ override constructor
        """
        if on_change is None:
            raise ValueError('on_change method must be specified')
        super(OnDict, self).__init__()
        self.on_change = on_change

    def __setitem__(self, *args):
        """ override setitem
        """
        super(OnDict, self).__setitem__(*args)
        self.on_change(False)

    def __delitem__(self, *args):
        """ override delitem
        """
        super(OnDict, self).__delitem__(*args)
        self.on_change(True)

    def pop(self, *args):
        """ override pop
        """
        value = super(OnDict, self).pop(*args)
        if value is not None:
            self.on_change(True)
        return value


class MPcurses():
    """ mpcurses process pool
    """
    def __init__(self, function, *, process_data=None, shared_data=None, processes_to_start=None, screen_layout=None, init_messages=None, setup_process_queue=True):
        """ MPCstate constructor
        """
        if getattr(function, '__name__', None) == '_queue_handler':
            # enable backwards compatibility for use cases where
            # function was already decorated with queue_handler
            # NOTE: this does not work for functions with multiple decorators
            logger.debug('function is already decorated with queue_handler')
            self.function = function
        else:
            logger.debug(f'decorating function {function.__name__} with queue_handler')
            self.function = queue_handler(function)

        if not process_data:
            process_data = [{}]
        self.process_data = process_data

        if not shared_data:
            shared_data = {}
        self.shared_data = shared_data

        if not processes_to_start:
            processes_to_start = len(process_data)
        self.processes_to_start = processes_to_start

        self.active_processes = OnDict(on_change=self.on_state_change)

        self.process_data_offset = [(self.process_data.index(item), item) for item in self.process_data]

        self.message_queue = Queue()

        self.result_queue = Queue()

        self.process_queue = SimpleQueue()

        if screen_layout:
            validate_screen_layout(len(self.process_data), screen_layout)
        self.screen_layout = screen_layout

        self.init_messages = init_messages

        if setup_process_queue:
            self.setup_process_queue()

        self.screen = None

    def setup_process_queue(self):
        """ return queue containing data for each process
        """
        logger.debug('populating the process queue')
        for item in self.process_data_offset:
            logger.debug(f'adding {item} to the process queue')
            self.process_queue.put(item)
        logger.debug(f'added {self.process_queue.qsize()} items to the process queue')

    def start_processes(self):
        """ start processes
        """
        logger.debug(f'there are {self.process_queue.qsize()} items in the process queue')
        logger.debug(f'starting {self.processes_to_start} background processes')
        for _ in range(self.processes_to_start):
            if self.process_queue.empty():
                logger.debug('the process queue is empty - no more processes need to be started')
                break
            self.start_next_process()
        logger.info(f'started {len(self.active_processes)} background processes')

    def start_next_process(self):
        """ start next process in the process queue
        """
        process_queue_data = self.process_queue.get()
        offset = process_queue_data[0]
        process_data = process_queue_data[1]
        process = Process(
            target=self.function,
            args=(process_data, self.shared_data),
            kwargs={
                'message_queue': self.message_queue,
                'offset': offset,
                'result_queue': self.result_queue
            })
        # logger.debug(f'starting background process at offset {offset} with data {process_data}')
        process.start()
        logger.info(f'started background process at offset {offset} with process id {process.pid}')
        # update active_processes dictionary with process meta-data for the process offset
        self.active_processes[str(offset)] = process

    def terminate_processes(self):
        """ terminate all active processes
        """
        for offset, process in self.active_processes.items():
            logger.info(f'terminating process at offset {offset} with process id {process.pid}')
            process.terminate()

    def purge_process_queue(self):
        """ purge process queue
        """
        logger.info('purging all items from the to process queue')
        while not self.process_queue.empty():
            logger.info(f'purged {self.process_queue.get()} from the to process queue')

    def remove_active_process(self, offset):
        """ remove active process at offset
        """
        process = self.active_processes.pop(offset, None)
        process_id = process.pid if process else '-'
        logger.info(f'process at offset {offset} process id {process_id} has completed')

    def update_result(self):
        """ update process data with result
        """
        logger.debug('updating process data with result from result queue')
        while True:
            try:
                result_data = self.result_queue.get(False)
                for offset, result in result_data.items():
                    logger.debug(f'adding result of process at offset {offset} to process data')
                    self.process_data[int(offset)]['result'] = result
            except Empty:
                logger.debug('result queue is empty')
                break

    def on_state_change(self, process_completed=True):
        """ update screen on state change
        """
        if not self.screen:
            return
        active_processes = str(len(self.active_processes)).zfill(3)
        process_queue_size = str(self.process_queue.qsize()).zfill(3)
        update_screen(f'mpcurses: number of active processes {active_processes}', self.screen, self.screen_layout)
        update_screen(f'mpcurses: number of queued processes {process_queue_size}', self.screen, self.screen_layout)
        if process_completed:
            update_screen('mpcurses: a process has completed', self.screen, self.screen_layout)

    def setup_screen(self):
        """ update and echo data to screen
        """
        if self.init_messages:
            for init_message in self.init_messages:
                update_screen(init_message, self.screen, self.screen_layout)

        for index, data in enumerate(self.process_data_offset):
            echo_to_screen(self.screen, data[1], self.screen_layout, offset=index)

        echo_to_screen(self.screen, self.shared_data, self.screen_layout)

    def active_processes_empty(self):
        """ return True if active processes is empty else False
            method added to facilitate unit testing
        """
        # no active processes means its empty
        return not self.active_processes

    def get_message(self):
        """ return message from top of message queue
        """
        offset = None
        control = None
        message = self.message_queue.get(False)
        match = re.match(r'^#(?P<offset>\d+)-(?P<control>DONE|ERROR)$', message)
        if match:
            offset = match.group('offset')
            control = match.group('control')
        return {
            'offset': offset,
            'control': control,
            'message': message
        }

    def process_control_message(self, offset, control):
        """ process control message
        """
        if control == 'DONE':
            self.remove_active_process(offset)
            if self.process_queue.empty():
                logger.info('the to process queue is empty')
                if self.active_processes_empty():
                    raise NoActiveProcesses()
            else:
                self.start_next_process()
        else:
            logger.info(f'error detected for process at offset {offset}')
            self.purge_process_queue()

    def run(self):
        """ run without screen
        """
        self.start_processes()
        while True:
            try:
                message = self.get_message()
                if message['control']:
                    self.process_control_message(message['offset'], message['control'])

            except NoActiveProcesses:
                logger.info('there are no more active processses - quitting')
                break

            except Empty:
                pass

    def run_screen(self, screen):
        """ run with screen
        """
        # set screen attribute so on_state_change method will have access to screen
        self.screen = screen
        initialize_screen(screen, self.screen_layout, len(self.process_data_offset))
        self.setup_screen()

        self.start_processes()

        blink_meta = {}
        while True:
            try:
                blink_running(screen, blink_meta)

                message = self.get_message()
                if message['control']:
                    self.process_control_message(message['offset'], message['control'])
                else:
                    update_screen(message['message'], screen, self.screen_layout)

            except NoActiveProcesses:
                logger.info('there are no more active processses - quitting')
                break

            except Empty:
                # queue.Empty exception is raised when nothing is in the multiprocessing message queue
                refresh_screen(screen)

        end_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        update_screen(f'mpcurses: Ended:{end_time}', screen, self.screen_layout)

        finalize_screen(screen, self.screen_layout)

    def execute(self):
        """ public execute api
        """
        try:
            if self.screen_layout:
                wrapper(self.run_screen)
            else:
                self.run()

            self.update_result()

        except KeyboardInterrupt:
            logger.info('Keyboard Interrupt signal received - killing all active processes')
            self.terminate_processes()
            sys.exit(-1)
