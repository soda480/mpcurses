
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


import logging
from logging import Handler

logger = logging.getLogger(__name__)


class QueueHandler(Handler):

    def __init__(self, message_queue, offset):
        super(QueueHandler, self).__init__()
        self.message_queue = message_queue
        self.offset = offset

    def emit(self, record):
        message = record.msg

        if record.levelno >= 40:
            message = 'ERROR: {}'.format(message)
        elif record.levelno >= 30:
            message = 'WARN: {}'.format(message)
        elif record.levelno == 20:
            message = 'INFO: {}'.format(message)

        message = '#{}-{}'.format(self.offset, message)
        self.message_queue.put(message)


def queue_handler(function):
    """ adds QueueHandler to rootLogger in order to send log messages to a message queue
    """

    def _queue_handler(*args, **kwargs):
        """ internal decorator for message queue handler
        """
        root_logger = logging.getLogger()

        offset = kwargs.pop('offset', 0)
        message_queue = kwargs.pop('message_queue', None)
        result_queue = kwargs.pop('result_queue', None)
        result = None

        if message_queue:
            handler = QueueHandler(message_queue, offset)
            log_formatter = logging.Formatter('%(asctime)s %(processName)s %(name)s [%(funcName)s] %(levelname)s %(message)s')
            handler.setFormatter(log_formatter)
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.DEBUG)

        try:
            result = function(*args, **kwargs)
            return result

        except Exception as exception:
            result = exception
            logger.error(str(exception), exc_info=True)
            # log control message that an error occurred
            logger.debug('ERROR')

        finally:
            # add result to result queue with offset index
            if result_queue:
                result_queue.put({
                    offset: result
                })
            # log control message that method completed
            logger.debug('DONE')
            if message_queue:
                root_logger.removeHandler(handler)

    return _queue_handler
