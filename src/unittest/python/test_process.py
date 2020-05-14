
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

from mpcurses.process import setup_process_queue
from mpcurses.process import start_process
from mpcurses.process import start_processes
from mpcurses.process import _execute
from mpcurses.process import execute

from queue import Empty


class TestProcess(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @unittest.skip('skip')
    @patch('mpcurses.mpcurseslib.initialize_screen')
    def test__execute_Should_RaiseTypeError_When_SetupNotCallable(self, *patches):
        screen_mock = Mock()
        args_mock = Mock()
        args_mock.setup = 'something that is not callable'
        with self.assertRaises(TypeError):
            _execute(screen_mock, args_mock, [])

    @patch('mpcurses.process.send_process_state')
    @patch('mpcurses.process.blink_running')
    @patch('mpcurses.process.finalize_screen')
    @patch('mpcurses.process.initialize_screen')
    @patch('mpcurses.process.start_process')
    @patch('mpcurses.process.setup_process_queue')
    @patch('mpcurses.process.update_screen')
    @patch('mpcurses.process.start_processes')
    def test__execute_Should_CallScreenRefresh_When_GetRaisesEmpty(self, start_processes_patch, update_screen_patch, setup_process_queue_patch, *patches):
        process_queue_mock = Mock()
        process_queue_mock.qsize.return_value = 0
        setup_process_queue_patch.return_value = process_queue_mock
        message_queue_mock = Mock()
        message_queue_mock.get.side_effect = [
            'message1',
            Empty('empty'),
            'message2',
            '#1-DONE',
        ]
        start_processes_patch.return_value = message_queue_mock

        screen_mock = Mock()
        function_mock = Mock()
        process_data = [(0, {})]
        shared_data = {}
        num_processes = 1
        screen_layout = Mock()
        processes = {}
        messages = []

        _execute(screen_mock, function_mock, process_data, shared_data, num_processes, messages, screen_layout, processes)

        screen_mock.refresh.assert_called_once_with()
        self.assertEqual(len(update_screen_patch.mock_calls), 3)

    @patch('mpcurses.process.refresh_screen')
    @patch('mpcurses.process.send_process_state')
    @patch('mpcurses.process.finalize_screen')
    @patch('mpcurses.process.blink_running')
    @patch('mpcurses.process.echo_to_screen')
    @patch('mpcurses.process.initialize_screen')
    @patch('mpcurses.process.update_screen')
    @patch('mpcurses.process.setup_process_queue')
    @patch('mpcurses.process.start_process')
    @patch('mpcurses.process.start_processes')
    def test__execute_Should_StartProcessFromProcessQueue_When_ActiveProcessesDone(self, start_processes_patch, start_process_patch, setup_process_queue_patch, *patches):
        message_queue_mock = Mock()
        message_queue_mock.get.side_effect = [
            '#1-DONE',
            '#2-DONE',
            '#3-DONE',
            '#4-DONE'
        ]
        start_processes_patch.return_value = message_queue_mock
        process_queue_mock = Mock()
        process_queue_mock.qsize.side_effect = [
            1,
            0,
            0,
            0
        ]
        setup_process_queue_patch.return_value = process_queue_mock
        screen_mock = Mock()
        function_mock = Mock()
        process_data = [(0, {'bay': 1}), (1, {'bay': 2}), (2, {'bay': 3})]
        shared_data = {}
        num_processes = 1
        screen_layout = {}
        active_processes = {}
        messages = []

        _execute(screen_mock, function_mock, process_data, shared_data, num_processes, messages, screen_layout, active_processes)

        start_process_patch.assert_called()
        start_process_patch.assert_called_once_with(function_mock, shared_data, message_queue_mock, process_queue_mock.get.return_value, active_processes)

    @patch('mpcurses.process.finalize_screen')
    @patch('mpcurses.process.update_screen')
    @patch('mpcurses.process.blink_running')
    @patch('mpcurses.process.initialize_screen')
    @patch('mpcurses.process.setup_process_queue')
    @patch('mpcurses.process.start_processes')
    def test__execute_Should_PurgeProcessQueue_When_ErrorDetected(self, start_processes_patch, setup_process_queue_patch, *patches):
        process_queue_mock = Mock()
        process_queue_mock.get.side_effect = [
            (1, 2),
            (2, 3)
        ]
        process_queue_mock.empty.side_effect = [
            False,
            False,
            True
        ]
        process_queue_mock.qsize.return_value = 0
        setup_process_queue_patch.return_value = process_queue_mock
        message_queue_mock = Mock()
        message_queue_mock.get.side_effect = [
            '#1-ERROR',
            '#1-DONE'
        ]
        start_processes_patch.return_value = message_queue_mock

        screen_mock = Mock()
        function_mock = Mock()
        process_data = [(0, {'bay': 1}), (1, {'bay': 2}), (2, {'bay': 3})]
        shared_data = {}
        num_processes = 1
        screen_layout = {}
        processes = {}
        messages = []

        _execute(screen_mock, function_mock, process_data, shared_data, num_processes, messages, screen_layout, processes)

        self.assertEqual(len(process_queue_mock.get.mock_calls), 2)

    @patch('mpcurses.process.wrapper')
    def test__execute_Should_Exit_When_KeyboardInterruptIsCaught(self, wrapper_patch, *patches):
        wrapper_patch.side_effect = [
            KeyboardInterrupt('keyboard interrupt')
        ]
        function_mock = Mock()
        screen_layout = Mock()
        with self.assertRaises(SystemExit):
            execute(function=function_mock, number_of_processes=1, screen_layout=screen_layout)

    @patch('mpcurses.process.Process')
    def test__start_process_Should_StartProcessAndAddToProcesses_When_Called(self, process_patch, *patches):
        process_mock = Mock()
        process_patch.return_value = process_mock

        function_mock = Mock()
        shared_data = {}
        message_queue_mock = Mock()
        to_process = [0, {'bay': 1}]
        processes = {}

        start_process(function_mock, shared_data, message_queue_mock, to_process, processes)

        process_mock.start.assert_called_once_with()
        self.assertEqual(processes, {'0': process_mock})

    def test__setup_process_queue_Should_ReturnExpected_When_Called(self, *patches):
        to_process = [(0, 1), (1, 3), (2, 16)]
        result = setup_process_queue(to_process)

        self.assertEqual(result.qsize(), 3)

    @patch('mpcurses.process.Queue')
    @patch('mpcurses.process.start_process')
    def test__start_processes_Should_CallExpected_When_Called(self, start_process_patch, queue_patch, *patches):
        function_mock = Mock()
        shared_data = {}
        num_processes = 5
        to_process_queue_mock = Mock()
        to_process_queue_mock.get.side_effect = [
            '1',
            '2',
            '3',
            '4',
            '5'
        ]
        to_process_queue_mock.empty.side_effect = [
            False,
            False,
            False,
            False,
            False,
            True
        ]
        processes = []
        result = start_processes(function_mock, shared_data, num_processes, to_process_queue_mock, processes)

        self.assertEqual(result, queue_patch.return_value)
        self.assertEqual(len(start_process_patch.mock_calls), 5)
        self.assertTrue(call(function_mock, shared_data, queue_patch.return_value, '1', processes) in start_process_patch.mock_calls)

    @patch('mpcurses.process.Queue')
    @patch('mpcurses.process.start_process')
    def test__start_processes_Should_Break_When_ProcessQueueEmpty(self, start_process_patch, queue_patch, *patches):
        function_mock = Mock()
        shared_data = {}
        num_processes = 5
        to_process_queue_mock = Mock()
        to_process_queue_mock.get.side_effect = [
            '1',
            '2',
        ]
        to_process_queue_mock.empty.side_effect = [
            False,
            False,
            True
        ]
        processes = {}
        start_processes(function_mock, shared_data, num_processes, to_process_queue_mock, processes)

        self.assertEqual(len(start_process_patch.mock_calls), 2)
