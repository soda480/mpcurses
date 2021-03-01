
# Copyright (c) 2021 Intel Corporation

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
from .screen import initialize_screen_offsets
from .screen import finalize_screen
from .screen import update_screen
from .screen import echo_to_screen
from .screen import refresh_screen
from .screen import validate_screen_layout_processes
from .screen import update_screen_status
from .screen import blink
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
    def __init__(self, function, *, process_data=None, shared_data=None, processes_to_start=None, screen_layout=None, init_messages=None, get_process_data=None):
        """ MPCstate constructor
        """
        if process_data and get_process_data:
            raise ValueError('process_data and get_process_data values cannot both be set')

        if get_process_data and not callable(get_process_data):
            raise ValueError('get_process_data value must be a callable function')

        if get_process_data and not screen_layout:
            raise ValueError('get_process_data can only be set if screen_layout value is provided')

        logger.debug(f'decorating function {function.__name__} with queue_handler')
        self.function = queue_handler(function)

        self.screen_layout = screen_layout

        self.processes_to_start = processes_to_start

        self.get_process_data = get_process_data

        if self.get_process_data:
            self.process_data = None
        else:
            # things we can set when get_process_data is not specified
            self.process_data = [{}] if process_data is None else process_data
            if not self.processes_to_start:
                self.processes_to_start = len(self.process_data)

        self.shared_data = {} if shared_data is None else shared_data

        self.active_processes = OnDict(on_change=self.on_state_change)

        self.message_queue = Queue()

        self.result_queue = Queue()

        self.process_queue = SimpleQueue()

        self.init_messages = [] if init_messages is None else init_messages

        self.completed_processes = 0

        self.screen = None

        self.blink_screen = False
        if self.screen_layout:
            self.blink_screen = self.screen_layout.get('_screen', {}).get('blink', True)

        self.blink_process = None

        self.blink_queue = None
        if self.blink_screen:
            self.blink_queue = Queue()

    def start_blink_process(self):
        """ start blink process
        """
        if not self.blink_screen:
            return
        self.blink_process = Process(
            target=blink,
            args=(self.blink_queue,))
        self.blink_process.start()
        logger.info(f'started background process for blink with process id {self.blink_process.pid}')

    def stop_blink_process(self):
        """ stop blink process
        """
        if self.blink_screen and self.blink_process:
            self.blink_process.terminate()
            logger.debug('terminated blink process')

    def populate_process_queue(self):
        """ populate process queue from process data offset
        """
        logger.debug('populating the process queue')
        for offset, data in enumerate(self.process_data):
            item = (offset, data)
            logger.debug(f'adding {item} to the process queue')
            self.process_queue.put(item)
        logger.debug(f'added {self.process_queue.qsize()} items to the process queue')

    def start_processes(self):
        """ start processes
        """
        self.populate_process_queue()

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
                'result_queue': self.result_queue})
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

        if process_completed:
            self.completed_processes += 1

        update_screen_status(
            self.screen,
            'process-update',
            self.screen_layout['_screen'],
            running=len(self.active_processes),
            queued=self.process_queue.qsize(),
            completed=self.completed_processes)

    def execute_get_process_data(self):
        """ execute get_process_data function
        """
        if self.get_process_data:
            doc = self.get_process_data.__doc__
            update_screen_status(self.screen, 'get-process-data', self.screen_layout['_screen'], data=doc)
            kwargs = self.shared_data if self.shared_data else {}
            self.process_data = self.get_process_data(**kwargs)
            update_screen_status(self.screen, 'get-process-data', self.screen_layout['_screen'])
            if not self.processes_to_start:
                self.processes_to_start = len(self.process_data)

    def setup_screen(self):
        """ setup screen
        """
        initialize_screen(self.screen, self.screen_layout)

        self.execute_get_process_data()

        # initialize screen with offsets
        initialize_screen_offsets(self.screen, self.screen_layout, len(self.process_data), self.processes_to_start)

        # update screen with all initialization messages if they were provided
        for message in self.init_messages:
            update_screen(message, self.screen, self.screen_layout)

        # echo shared data to screen
        echo_to_screen(self.screen, self.shared_data, self.screen_layout)

        # echo all process data to screen
        for offset, data in enumerate(self.process_data):
            echo_to_screen(self.screen, data, self.screen_layout, offset=offset)

        self.start_blink_process()

    def teardown_screen(self):
        """ tear down screen
        """
        # update screen with end time
        end_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        update_screen(f'mpcurses: Ended:{end_time}', self.screen, self.screen_layout)

        finalize_screen(self.screen, self.screen_layout)

        self.stop_blink_process()

    def active_processes_empty(self):
        """ return True if active processes is empty else False
            method added to facilitate unit testing
        """
        # no active processes means its empty
        return not self.active_processes

    def get_blink_message(self):
        """ return message from blink queue
        """
        try:
            return self.blink_queue.get(False)

        except Empty:
            return None

    def get_message(self):
        """ return message from top of message queue
        """
        if self.blink_screen:
            # if blink is enabled then process blink message first
            blink_message = self.get_blink_message()
            if blink_message:
                update_screen_status(self.screen, blink_message, self.screen_layout['_screen'])

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
            'message': message}

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
        # set screen attribute so instance methods have access to screen
        self.screen = screen
        self.setup_screen()
        self.start_processes()

        while True:
            try:
                message = self.get_message()
                if message['control']:
                    self.process_control_message(message['offset'], message['control'])
                else:
                    update_screen(message['message'], self.screen, self.screen_layout)

            except NoActiveProcesses:
                logger.info('there are no more active processses - quitting')
                break

            except Empty:
                # queue.Empty exception is raised when nothing is in the multiprocessing message queue
                refresh_screen(self.screen)

        self.teardown_screen()

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
