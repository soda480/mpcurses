
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

import unittest
from mock import patch
from mock import call
from mock import Mock
from mock import MagicMock

from mpcurses.handler import QueueHandler
from mpcurses.handler import queue_handler

import sys
import logging
logger = logging.getLogger(__name__)

consoleHandler = logging.StreamHandler(sys.stdout)
logFormatter = logging.Formatter("%(asctime)s %(threadName)s %(name)s [%(funcName)s] %(levelname)s %(message)s")
consoleHandler.setFormatter(logFormatter)
rootLogger = logging.getLogger()
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.DEBUG)


class TestHandler(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('mpcurses.handler.logging.Formatter')
    @patch('mpcurses.handler.logging.getLogger')
    @patch('mpcurses.handler.QueueHandler')
    def test__queue_handler_Should_AddAndRemoveQueueHandler_When_DecoratedFunctionIsPassedMessageQueue(self, queue_handler_class, get_logger_mock, *patches):
        root_logger_mock = Mock()
        get_logger_mock.return_value = root_logger_mock

        queue_handler_object = Mock()
        queue_handler_class.return_value = queue_handler_object

        function_mock = Mock(__name__='fn1')
        function_mock.return_value = 'return'
        message_queue_mock = Mock()
        result = queue_handler(function_mock)(message_queue=message_queue_mock, offset=3)
        self.assertEqual(result, function_mock.return_value)

        queue_handler_object.setFormatter.assert_called()
        root_logger_mock.addHandler.assert_called_with(queue_handler_object)
        root_logger_mock.setLevel.assert_called_with(logging.DEBUG)
        root_logger_mock.removeHandler.assert_called_with(queue_handler_object)

    def test__queue_handler_Should_AddResultToResultQueue_When_DecoratedFunctionIsPassedResultQueue(self, *patches):
        function_mock = Mock(__name__='fn1')
        function_mock.return_value = 'function return value'
        result_queue_mock = Mock()
        result = queue_handler(function_mock)(offset=3, result_queue=result_queue_mock)
        self.assertEqual(result, function_mock.return_value)
        result_queue_mock.put.assert_called_once_with({3: function_mock.return_value})

    def test__queue_handler_Should_AddDoneToMessageQueue_When_DecoratedFunctionIsPassedMessageQueueAndCompletes(self, *patches):
        function_mock = Mock(__name__='fn1')
        function_mock.return_value = 'function return value'
        message_queue_mock = Mock()
        result = queue_handler(function_mock)(offset=3, message_queue=message_queue_mock)
        self.assertEqual(result, function_mock.return_value)
        message_queue_mock.put.assert_called_once_with('#3-DONE')

    def test__queue_handler_Should_AddErrorMessagesToMessageQueue_When_FunctionThrowsException(self, *patches):
        function_mock = Mock(__name__='fn1')
        function_mock.side_effect = Exception('function exception')
        message_queue_mock = Mock()
        queue_handler(function_mock)(offset=3, message_queue=message_queue_mock)
        call1 = call('#3-ERROR: function exception')
        call2 = call('#3-ERROR')
        call3 = call('#3-DONE')
        self.assertEqual(message_queue_mock.put.mock_calls, [call1, call2, call3])

    def test__queue_handler_Should_AddExceptionToResultQueue_When_FunctionThrowsException(self, *patches):
        function_mock = Mock(__name__='fn1')
        function_mock.side_effect = Exception('function exception')
        message_queue_mock = Mock()
        result_queue_mock = Mock()
        queue_handler(function_mock)(offset=3, message_queue=message_queue_mock, result_queue=result_queue_mock)
        result_queue_mock.put.assert_called_once_with({3: function_mock.side_effect})

    @patch('mpcurses.handler.Handler')
    def test__QueueHandler_Should_PutInfoMessageToMessageQueue_When_EmitInfoRecord(self, *patches):
        message_queue_mock = Mock()
        process_number = 1
        queue_handler_object = QueueHandler(message_queue_mock, process_number)

        record_mock = Mock(msg='some message', levelno=20)

        queue_handler_object.emit(record_mock)
        message_queue_mock.put.assert_called_with('#1-INFO: some message')

    @patch('mpcurses.handler.Handler')
    def test__QueueHandler_Should_PutInfoMessageToMessageQueue_When_EmitWarnRecord(self, *patches):
        message_queue_mock = Mock()
        process_number = 1
        queue_handler_object = QueueHandler(message_queue_mock, process_number)

        record_mock = Mock(msg='some message', levelno=30)

        queue_handler_object.emit(record_mock)
        message_queue_mock.put.assert_called_with('#1-WARN: some message')

    @patch('mpcurses.handler.Handler')
    def test__QueueHandler_Should_PutErrorMessageToMessageQueue_When_EmitErrorRecord(self, *patches):
        message_queue_mock = Mock()
        process_number = 1
        queue_handler_object = QueueHandler(message_queue_mock, process_number)

        record_mock = Mock(msg='some message', levelno=40)

        queue_handler_object.emit(record_mock)
        message_queue_mock.put.assert_called_with('#1-ERROR: some message')
