
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
from multiprocessing import Queue
from multiprocessing import Process
from queue import Queue as SimpleQueue
from queue import Empty

from mpcurses.handler import queue_handler

logger = logging.getLogger(__name__)


class NoActiveProcesses(Exception):
    """ Raise when NoActiveProcesses is used to signal end
    """
    pass


class MPcontroller():
    """ multi-processing (MP) controller
        execute function across multiple processes
        queue function execution
        queue function log messages to thread-safe message queue
        process messages from log message queue
        maintain result of all executed functions
        terminate execution using keyboard interrupt
    """
    def __init__(self, function, *, process_data=None, shared_data=None, processes_to_start=None):
        """ MPcontroller constructor
        """
        logger.debug('executing MPcontroller constructor')
        logger.debug(f'decorating function {function.__name__} with queue_handler')
        self.function = queue_handler(function)
        self.process_data = [{}] if process_data is None else process_data
        self.shared_data = {} if shared_data is None else shared_data
        self.active_processes = {}
        self.message_queue = Queue()
        self.result_queue = Queue()
        self.process_queue = SimpleQueue()
        self.completed_processes = 0
        self.processes_to_start = processes_to_start if processes_to_start else len(self.process_data)

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

    def active_processes_empty(self):
        """ return True if active processes is empty else False
            method added to facilitate unit testing
        """
        # no active processes means its empty
        return not self.active_processes

    def get_message(self):
        """ return message from top of message queue
        """
        message = self.message_queue.get(False)
        match = re.match(r'^#(?P<offset>\d+)-(?P<control>DONE|ERROR)$', message)
        if match:
            return {
                'offset': match.group('offset'),
                'control': match.group('control'),
                'message': message
            }
        return {
            'offset': None,
            'control': None,
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

    def process_non_control_message(self, offset, message):
        """ process non-control message
            to be overriden by child class
        """
        pass

    def run(self):
        """ run without screen
        """
        self.start_processes()

        while True:
            try:
                message = self.get_message()
                if message['control']:
                    self.process_control_message(message['offset'], message['control'])
                else:
                    self.process_non_control_message(message['offset'], message['message'])

            except NoActiveProcesses:
                logger.info('there are no more active processses - quitting')
                break

            except Empty:
                pass

    def execute_run(self):
        """ wraps call to run
        """
        self.run()

    def final(self):
        """ called in finally block
        """
        pass

    def execute(self):
        """ public execute api
        """
        try:
            self.execute_run()
            self.update_result()

        except KeyboardInterrupt:
            logger.info('Keyboard Interrupt signal received - killing all active processes')
            self.terminate_processes()
            sys.exit(-1)

        finally:
            self.final()
