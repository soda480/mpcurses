
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

import unittest
from mock import patch
from mock import call
from mock import Mock
from mock import MagicMock

from queue import Empty

from mpcurses.mpcurses import MPcurses
from mpcurses.mpcurses import NoActiveProcesses
from mpcurses.mpcurses import OnDict
from mpcurses.handler import queue_handler

import sys
import logging
logger = logging.getLogger(__name__)


class TestMPcurses(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    def test__init_Should_SetDefaults_When_Called(self, *patches):
        client = MPcurses(function=Mock(__name__='mockfunc'))
        self.assertEqual(client.process_data, [{}])
        self.assertEqual(client.shared_data, {})
        self.assertEqual(client.processes_to_start, 1)
        self.assertEqual(client.init_messages, [])

    @patch('mpcurses.mpcurses.queue_handler')
    def test__init_Should_SetDefaults_When_FunctionNotWrapped(self, queue_handler_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        client = MPcurses(function=function_mock)
        self.assertEqual(client.process_data, [{}])
        self.assertEqual(client.shared_data, {})
        self.assertEqual(client.processes_to_start, 1)
        self.assertEqual(client.function, queue_handler_patch(function_mock))

    def test__init__Should_RaiseException_When_ProcessDataAndGetProcessData(self, *patches):
        function_mock = Mock(__name__='_queue_handler')
        with self.assertRaises(Exception):
            MPcurses(function_mock, process_data=[{}], get_process_data=Mock())

    def test__init__Should_RaiseException_When_GetProcessDataNotCallable(self, *patches):
        function_mock = Mock(__name__='_queue_handler')
        get_process_data_mock = 'mock'
        with self.assertRaises(Exception):
            MPcurses(function_mock, get_process_data=get_process_data_mock)

    def test__init__Should_RaiseException_When_GetProcessDataNoScreenLayout(self, *patches):
        function_mock = Mock(__name__='_queue_handler')
        get_process_data_mock = Mock()
        with self.assertRaises(Exception):
            MPcurses(function_mock, get_process_data=get_process_data_mock)

    def test__init_Should_SetDefaults_When_GetProcessData(self, *patches):
        function_mock = Mock(__name__='mockfunc')
        get_process_data_mock = Mock()
        client = MPcurses(function=function_mock, get_process_data=get_process_data_mock, screen_layout={'_screen': {}})
        self.assertIsNone(client.process_data)
        self.assertEqual(client.get_process_data, get_process_data_mock)

    def test__populate_process_queue_Should_AddToProcessQueue_When_Called(self, *patches):
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)
        client.populate_process_queue()
        self.assertEqual(client.process_queue.qsize(), 3)

    @patch('mpcurses.mpcurses.blink')
    @patch('mpcurses.mpcurses.Process')
    def test__start_blink_process_Should_CallExpected_When_ScreenBlink(self, process_patch, blink_patch, *patches):
        function_mock = Mock(__name__='_queue_handler')
        process_mock = Mock()
        process_patch.return_value = process_mock
        screen_layout = {
            '_screen': {
                'blink': True
            }
        }
        client = MPcurses(function=function_mock, screen_layout=screen_layout)
        client.start_blink_process()
        process_patch.assert_called_once_with(
            target=blink_patch,
            args=((client.blink_queue,)))
        process_mock.start.assert_called_once_with()

    @patch('mpcurses.mpcurses.Process')
    def test__start_blink_process_Should_CallExpected_When_NoScreenBlink(self, process_patch, *patches):
        function_mock = Mock(__name__='_queue_handler')
        client = MPcurses(function=function_mock)
        client.start_blink_process()
        process_patch.assert_not_called()

    def test__stop_blink_process_Should_CallExpected_When_BlinkScreenBlinkProces(self, *patches):
        process_mock = Mock()
        function_mock = Mock(__name__='_queue_handler')
        client = MPcurses(function=function_mock)
        client.blink_screen = True
        client.blink_process = process_mock
        client.stop_blink_process()
        process_mock.terminate.assert_called_once_with()

    def test__stop_blink_process_Should_NotCallTerminate_When_NoBlinkScreenBlinkProces(self, *patches):
        process_mock = Mock()
        function_mock = Mock(__name__='_queue_handler')
        client = MPcurses(function=function_mock)
        client.blink_screen = None
        client.blink_process = process_mock
        client.stop_blink_process()
        process_mock.terminate.assert_not_called()

    @patch('mpcurses.MPcurses.start_next_process')
    def test__start_processes_Should_CallStartNextProcess_When_Called(self, start_next_process_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, processes_to_start=2)
        client.start_processes()
        self.assertEqual(len(start_next_process_patch.mock_calls), 2)

    @patch('mpcurses.MPcurses.populate_process_queue')
    @patch('mpcurses.MPcurses.start_next_process')
    def test__start_processes_Should_CallStartNextProcess_When_ProcessesToStartGreaterThanProcessQueueSize(self, start_next_process_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        client.start_processes()
        self.assertEqual(len(start_next_process_patch.mock_calls), 0)

    @patch('mpcurses.mpcurses.queue_handler')
    @patch('mpcurses.mpcurses.Process')
    def test__start_next_process_Should_CallExpected_When_Called(self, process_patch, queue_handler_mock, *patches):
        process_mock = Mock()
        process_patch.return_value = process_mock

        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, shared_data='--shared-data--')
        client.populate_process_queue()
        client.start_next_process()

        process_patch.assert_called_once_with(
            target=queue_handler_mock(function_mock),
            args=({'range': '0-1'}, '--shared-data--'),
            kwargs={
                'message_queue': client.message_queue,
                'offset': 0,
                'result_queue': client.result_queue
            })

    def test__terminate_processes_Should_CallExpected_When_Called(self, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, shared_data='--shared-data--')
        process1_mock = Mock()
        process2_mock = Mock()
        client.active_processes = {'0': process1_mock, '1': process2_mock}
        client.terminate_processes()
        process1_mock.terminate.assert_called_once_with()
        process2_mock.terminate.assert_called_once_with()

    def test__purge_process_queue_Should_PurgeProcessQueue_When_Called(self, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        client.populate_process_queue()
        self.assertEqual(client.process_queue.qsize(), 3)
        client.purge_process_queue()
        self.assertTrue(client.process_queue.empty())

    @patch('mpcurses.mpcurses.logger')
    def test__remove_active_process_Should_CallExpected_When_Called(self, logger_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        process_mock = Mock(pid=121372)
        client.active_processes['0'] = process_mock
        client.remove_active_process('0')
        logger_patch.info.assert_called_once_with('process at offset 0 process id 121372 has completed')

    def test__update_result_Should_CallExpected_When_Called(self, *patches):
        result_queue_mock = Mock()
        result_queue_mock.get.side_effect = [
            {'0': '--result0--'},
            {'1': '--result1--'},
            {'2': '--result2--'},
            Empty('empty')
        ]
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        client.result_queue = result_queue_mock
        client.update_result()
        expected_process_data = [{'range': '0-1', 'result': '--result0--'}, {'range': '2-3', 'result': '--result1--'}, {'range': '4-5', 'result': '--result2--'}]
        self.assertEqual(client.process_data, expected_process_data)

    @patch('mpcurses.mpcurses.update_screen_status')
    def test__on_state_change_Should_CallExpected_When_Called(self, update_screen_status_patch, *patches):
        screen_mock = Mock()
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, screen_layout={'_screen': {}})
        client.screen = screen_mock
        client.on_state_change()
        update_screen_status_patch.assert_called()

    @patch('mpcurses.mpcurses.update_screen_status')
    def test__on_state_change_Should_CallExpected_When_NoProcessCompleted(self, update_screen_status_patch, *patches):
        screen_mock = Mock()
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, screen_layout={'_screen': {}})
        client.screen = screen_mock
        client.on_state_change(process_completed=False)
        update_screen_status_patch.assert_called()

    @patch('mpcurses.mpcurses.update_screen')
    def test__on_state_change_Should_CallExpected_When_NoScreen(self, update_screen_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        client.on_state_change(process_completed=False)
        update_screen_patch.assert_not_called()

    @patch('mpcurses.mpcurses.update_screen_status')
    def test__execute_get_process_data_Should_CallExpected_When_NoGetProcessData(self, update_screen_status_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        client = MPcurses(function=function_mock)
        client.execute_get_process_data()
        update_screen_status_patch.assert_not_called()

    @patch('mpcurses.mpcurses.update_screen_status')
    def test__execute_get_process_data_Should_CallExpected_When_GetProcessData(self, update_screen_status_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        get_process_data_mock = Mock(__doc__='getting data')
        get_process_data_mock.return_value = [{'data': 1}, {'data': 2}]
        client = MPcurses(function=function_mock, get_process_data=get_process_data_mock, screen_layout={'_screen': {}})
        client.execute_get_process_data()
        client.screen = None
        call1 = call(client.screen, 'get-process-data', {}, data='getting data')
        self.assertTrue(call1 in update_screen_status_patch.mock_calls)
        get_process_data_mock.assert_called_once_with()
        self.assertEqual(client.process_data, get_process_data_mock.return_value)
        call2 = call(client.screen, 'get-process-data', {})
        self.assertTrue(call2 in update_screen_status_patch.mock_calls)
        self.assertEqual(client.processes_to_start, 2)

    @patch('mpcurses.mpcurses.update_screen_status')
    def test__execute_get_process_data_Should_CallExpected_When_GetProcessDataStartProcesses(self, update_screen_status_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        get_process_data_mock = Mock(__doc__='getting data')
        get_process_data_mock.return_value = [{'data': 1}, {'data': 2}]
        client = MPcurses(function=function_mock, get_process_data=get_process_data_mock, screen_layout={'_screen': {}}, processes_to_start=1, shared_data={'arg1': 'value1', 'arg2': 'value2'})
        client.execute_get_process_data()
        client.screen = None
        call1 = call(client.screen, 'get-process-data', {}, data='getting data')
        self.assertTrue(call1 in update_screen_status_patch.mock_calls)
        get_process_data_mock.assert_called_once_with(arg1='value1', arg2='value2')
        self.assertEqual(client.process_data, get_process_data_mock.return_value)
        call2 = call(client.screen, 'get-process-data', {})
        self.assertTrue(call2 in update_screen_status_patch.mock_calls)
        self.assertEqual(client.processes_to_start, 1)

    @patch('mpcurses.mpcurses.initialize_screen_offsets')
    @patch('mpcurses.MPcurses.start_blink_process')
    @patch('mpcurses.mpcurses.initialize_screen')
    @patch('mpcurses.mpcurses.echo_to_screen')
    @patch('mpcurses.mpcurses.update_screen')
    def test__setup_screen_Should_CallExpected_When_Called(self, update_screen_patch, echo_to_screen_patch, *patches):
        screen_mock = Mock()
        function_mock = Mock(__name__='mockfunc')
        screen_layout_mock = {'_screen': {}}
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, shared_data='--shared-data--', init_messages=['--message1--', '--message2--'], screen_layout=screen_layout_mock)
        client.screen = screen_mock
        client.setup_screen()

        update_screen_call1 = call('--message1--', screen_mock, screen_layout_mock)
        self.assertTrue(update_screen_call1 in update_screen_patch.mock_calls)

        echo_to_screen_call1 = call(screen_mock, {'range': '0-1'}, screen_layout_mock, offset=0)
        self.assertTrue(echo_to_screen_call1 in echo_to_screen_patch.mock_calls)

        echo_to_screen_call2 = call(screen_mock, '--shared-data--', screen_layout_mock)
        self.assertTrue(echo_to_screen_call2 in echo_to_screen_patch.mock_calls)

    @patch('mpcurses.mpcurses.initialize_screen_offsets')
    @patch('mpcurses.MPcurses.start_blink_process')
    @patch('mpcurses.mpcurses.initialize_screen')
    @patch('mpcurses.mpcurses.echo_to_screen')
    @patch('mpcurses.mpcurses.update_screen')
    def test__setup_screen_Should_CallExpected_When_NoInitMessages(self, update_screen_patch, echo_to_screen_patch, *patches):
        screen_mock = Mock()
        function_mock = Mock(__name__='mockfunc')
        screen_layout_mock = {'_screen': {}}
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, screen_layout=screen_layout_mock)
        client.screen = screen_mock
        client.setup_screen()

        echo_to_screen_call1 = call(screen_mock, {'range': '0-1'}, screen_layout_mock, offset=0)
        self.assertTrue(echo_to_screen_call1 in echo_to_screen_patch.mock_calls)

    @patch('mpcurses.mpcurses.initialize_screen_offsets')
    @patch('mpcurses.MPcurses.stop_blink_process')
    @patch('mpcurses.mpcurses.finalize_screen')
    @patch('mpcurses.mpcurses.update_screen')
    def test__teardown_screen_Should_CallExpected_When_Called(self, update_screen_patch, finalize_screen_patch, *patches):
        screen_mock = Mock()
        function_mock = Mock(__name__='mockfunc')
        screen_layout_mock = {'_screen': {}}
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, screen_layout=screen_layout_mock)
        client.screen = screen_mock
        client.teardown_screen()
        update_screen_patch.assert_called()
        finalize_screen_patch.assert_called_once_with(client.screen, client.screen_layout)

    def test__active_processes_empty_Should_ReturnExpected_When_Called(self, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        client.active_processes = {'1': True}
        self.assertFalse(client.active_processes_empty())
        client.active_processes = {}
        self.assertTrue(client.active_processes_empty())

    @patch('mpcurses.mpcurses.initialize_screen_offsets')
    def test__get_blink_message_Should_ReturnExpected_When_Empty(self, *patches):
        function_mock = Mock(__name__='_queue_handler')
        screen_layout = {
            '_screen': {
                'blink': True
            }
        }
        client = MPcurses(function=function_mock, screen_layout=screen_layout)
        result = client.get_blink_message()
        self.assertIsNone(result)

    @patch('mpcurses.mpcurses.update_screen_status')
    @patch('mpcurses.MPcurses.get_blink_message')
    def test__get_message_Should_ReturnExpected_When_BlinkScreen(self, get_blink_message_patch, update_screen_status_patch, *patches):
        get_blink_message_patch.return_value = 'blink-on'
        function_mock = Mock(__name__='_queue_handler')
        screen_layout = {
            '_screen': {
                'blink': True
            }
        }
        client = MPcurses(function=function_mock, screen_layout=screen_layout)
        message_queue_mock = Mock()
        message_queue_mock.get.return_value = '#0-DONE'
        client.message_queue = message_queue_mock
        client.get_message()
        update_screen_status_patch.assert_called_once_with(client.screen, 'blink-on', screen_layout['_screen'])

    @patch('mpcurses.mpcurses.update_screen_status')
    @patch('mpcurses.MPcurses.get_blink_message')
    def test__get_message_Should_ReturnExpected_When_BlinkScreenNoMessage(self, get_blink_message_patch, update_screen_status_patch, *patches):
        get_blink_message_patch.return_value = None
        function_mock = Mock(__name__='_queue_handler')
        screen_layout = {
            '_screen': {
                'blink': True
            }
        }
        client = MPcurses(function=function_mock, screen_layout=screen_layout)
        message_queue_mock = Mock()
        message_queue_mock.get.return_value = '#0-DONE'
        client.message_queue = message_queue_mock
        client.get_message()
        update_screen_status_patch.assert_not_called()

    def test__get_message_Should_ReturnExpected_When_ControlDone(self, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        message_queue_mock = Mock()
        message_queue_mock.get.return_value = '#0-DONE'
        client.message_queue = message_queue_mock

        result = client.get_message()
        expected_result = {
            'offset': '0',
            'control': 'DONE',
            'message': '#0-DONE'
        }
        self.assertEqual(result, expected_result)

    def test__get_message_Should_ReturnExpected_When_ControlError(self, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        message_queue_mock = Mock()
        message_queue_mock.get.return_value = '#3-ERROR'
        client.message_queue = message_queue_mock

        result = client.get_message()
        expected_result = {
            'offset': '3',
            'control': 'ERROR',
            'message': '#3-ERROR'
        }
        self.assertEqual(result, expected_result)

    def test__get_message_Should_ReturnExpected_When_NotControlMessage(self, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        message_queue_mock = Mock()
        message_queue_mock.get.return_value = '#4-This is a log message'
        client.message_queue = message_queue_mock

        result = client.get_message()
        expected_result = {
            'offset': None,
            'control': None,
            'message': '#4-This is a log message'
        }
        self.assertEqual(result, expected_result)

    @patch('mpcurses.MPcurses.remove_active_process')
    @patch('mpcurses.MPcurses.active_processes_empty', return_value=True)
    def test__process_control_message_Should_RaiseNoActiveProcesses_When_ControlDoneAndProcessQueueEmptyAndNoActiveProcesses(self, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        process_queue_mock = Mock()
        process_queue_mock.empty.return_value = True
        client.process_queue = process_queue_mock

        with self.assertRaises(NoActiveProcesses):
            client.process_control_message('0', 'DONE')

    @patch('mpcurses.MPcurses.active_processes_empty', return_value=False)
    @patch('mpcurses.MPcurses.remove_active_process')
    @patch('mpcurses.MPcurses.start_next_process')
    def test__process_control_message_Should_StartNextProcess_When_ControlDoneAndProcessQueueNotEmpty(self, start_next_process_patch, remove_active_process_patch, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        process_queue_mock = Mock()
        process_queue_mock.empty.return_value = False
        client.process_queue = process_queue_mock

        client.process_control_message('0', 'DONE')
        start_next_process_patch.assert_called_once_with()
        remove_active_process_patch.assert_called_once_with('0')

    @patch('mpcurses.MPcurses.purge_process_queue')
    def test__process_control_message_Should_PurgeProcessQueue_When_ControlError(self, purge_process_queue_patch, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        client.process_control_message('0', 'ERROR')
        purge_process_queue_patch.assert_called_once_with()

    @patch('mpcurses.MPcurses.remove_active_process')
    @patch('mpcurses.MPcurses.active_processes_empty', return_value=False)
    def test__process_control_message_Should_DoNothing_When_ControlDoneAndProcessQueueEmptyAndActiveProcesses(self, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        process_queue_mock = Mock()
        process_queue_mock.empty.return_value = True
        client.process_queue = process_queue_mock

        client.process_control_message('0', 'DONE')

    @patch('mpcurses.MPcurses.start_processes')
    @patch('mpcurses.mpcurses.logger')
    @patch('mpcurses.MPcurses.get_message')
    def test__run_Should_CallExpected_When_EmptyAndNoActiveProcesses(self, get_message_patch, logger_patch, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        get_message_patch.side_effect = [
            Empty('empty'),
            NoActiveProcesses()
        ]
        client.run()
        logger_patch.info.assert_called_once_with('there are no more active processses - quitting')

    @patch('mpcurses.MPcurses.start_processes')
    @patch('mpcurses.MPcurses.process_control_message')
    @patch('mpcurses.MPcurses.get_message')
    def test__run_Should_ProcessControlMessage_When_ControlMessage(self, get_message_patch, process_control_message_patch, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data)

        get_message_patch.side_effect = [
            {'offset': None, 'control': None, 'message': '#0-this is message1'},
            {'offset': None, 'control': None, 'message': '#0-this is message2'},
            {'offset': '0', 'control': 'DONE', 'message': '#0-DONE'},
            NoActiveProcesses()
        ]
        client.run()
        process_control_message_patch.assert_called_once_with('0', 'DONE')

    @patch('mpcurses.mpcurses.validate_screen_layout_processes')
    @patch('mpcurses.MPcurses.teardown_screen')
    @patch('mpcurses.MPcurses.setup_screen')
    @patch('mpcurses.MPcurses.start_processes')
    @patch('mpcurses.mpcurses.refresh_screen')
    @patch('mpcurses.mpcurses.update_screen')
    @patch('mpcurses.mpcurses.logger')
    @patch('mpcurses.MPcurses.process_control_message')
    @patch('mpcurses.MPcurses.get_message')
    def test__run_screen_Should_CallExpected_When_Called(self, get_message_patch, process_control_message_patch, logger_patch, update_screen_patch, refresh_screen_patch, *patches):
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=Mock(__name__='mockfunc'), process_data=process_data, screen_layout={'_screen': {'blink': False}})

        get_message_patch.side_effect = [
            # 1
            {'offset': None, 'control': None, 'message': '#0-this is message1'},
            # 2
            Empty('empty'),
            # 3
            {'offset': None, 'control': None, 'message': '#0-this is message2'},
            # 4
            {'offset': '0', 'control': 'DONE', 'message': '#0-DONE'},
            # 5
            NoActiveProcesses()
        ]
        screen_mock = Mock()
        client.run_screen(screen_mock)
        client.screen = screen_mock
        # 1
        update_screen_call1 = call('#0-this is message1', client.screen, client.screen_layout)
        self.assertTrue(update_screen_call1 in update_screen_patch.mock_calls)
        # 2
        refresh_screen_patch.assert_called_once_with(client.screen)
        # 3
        update_screen_call2 = call('#0-this is message2', client.screen, client.screen_layout)
        self.assertTrue(update_screen_call2 in update_screen_patch.mock_calls)
        # 4
        process_control_message_patch.assert_called_once_with('0', 'DONE')
        # 5
        logger_patch.info.assert_called_once_with('there are no more active processses - quitting')

    @patch('mpcurses.mpcurses.validate_screen_layout_processes')
    @patch('mpcurses.MPcurses.terminate_processes')
    @patch('mpcurses.mpcurses.sys')
    @patch('mpcurses.mpcurses.wrapper')
    def test__execute_Should_CallTerminateProcesses_When_KeyboardInterrupt(self, wrapper_patch, sys_patch, terminate_processes_patch, *patches):
        wrapper_patch.side_effect = [
            KeyboardInterrupt('keyboard interrupt')
        ]
        function_mock = Mock(__name__='mockfunc')
        screen_layout_mock = {'_screen': {}}
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=function_mock, process_data=process_data, screen_layout=screen_layout_mock)
        client.execute()
        terminate_processes_patch.assert_called_once_with()
        sys_patch.exit.assert_called_once_with(-1)

    @patch('mpcurses.MPcurses.update_result')
    @patch('mpcurses.MPcurses.run')
    def test__execute_Should_CallExpected_When_NoScreenLayout(self, run_patch, update_result_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        client.execute()
        run_patch.assert_called_once_with()
        update_result_patch.assert_called_once_with()


class TestOnDict(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    def test__init_Should_SetOnChange_When_Called(self, *patches):
        on_change_mock = Mock()
        onDict = OnDict(on_change=on_change_mock)
        self.assertEqual(onDict.on_change, on_change_mock)

    def test__init_Should_RaiseValueError_When_OnChangeNotSpecified(self, *patches):
        with self.assertRaises(ValueError):
            OnDict()

    def test__setitem_Should_CallOnChange_When_Called(self, *patches):
        on_change_mock = Mock()
        onDict = OnDict(on_change=on_change_mock)
        onDict['key1'] = 'value1'
        on_change_mock.assert_called_once_with(False)

    def test__deltitem_Should_CallOnChange_When_Called(self, *patches):
        on_change_mock = Mock()
        onDict = OnDict(on_change=on_change_mock)
        onDict['key1'] = 'value1'
        del onDict['key1']
        self.assertTrue(call(True) in on_change_mock.mock_calls)

    def test__pop_Should_CallOnChange_When_Called(self, *patches):
        on_change_mock = Mock()
        onDict = OnDict(on_change=on_change_mock)
        onDict['key1'] = 'value1'
        onDict.pop('key1', None)
        self.assertTrue(call(True) in on_change_mock.mock_calls)

    def test__pop_Should_NotCallOnChange_When_NoValue(self, *patches):
        on_change_mock = Mock()
        onDict = OnDict(on_change=on_change_mock)
        onDict.pop('key1', None)
        on_change_mock.assert_not_called()
