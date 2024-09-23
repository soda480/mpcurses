
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
from mpmq.mpmq import NoActiveProcesses
from mpmq.handler import queue_handler

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

    @patch('mpcurses.mpcurses.datetime')
    def test__init_Should_SetDefaults_When_Called(self, datetime_patch, *patches):
        datetime_patch.now.return_value.strftime.return_value = 'current-time'
        client = MPcurses(function=Mock(__name__='mockfunc'))
        self.assertEqual(client.process_data, [{}])
        self.assertEqual(client.shared_data, {})
        self.assertEqual(client.processes_to_start, 1)
        self.assertEqual(client.init_messages, ['mpcurses: Started:current-time'])

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

    @patch('mpcurses.mpcurses.update_screen_status')
    def test__on_state_change_Should_CallExpected_When_Called(self, update_screen_status_patch, *patches):
        screen_mock = Mock()
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data, screen_layout={'_screen': {}})
        client.screen = screen_mock
        client.on_state_change()
        update_screen_status_patch.assert_called()

    @patch('mpcurses.mpcurses.update_screen')
    def test__on_state_change_Should_CallExpected_When_NoScreen(self, update_screen_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}, {'range': '2-3'}, {'range': '4-5'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        client.on_state_change()
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
        get_process_data_mock = Mock(__name__='get_my_process_data', __doc__='getting data')
        get_process_data_mock.return_value = ([{'data': 1}, {'data': 2}], {'key1', 'value1'})
        client = MPcurses(function=function_mock, get_process_data=get_process_data_mock, screen_layout={'_screen': {}})
        client.execute_get_process_data()
        client.screen = None
        call1 = call(client.screen, 'get-process-data', {}, data='getting data')
        self.assertTrue(call1 in update_screen_status_patch.mock_calls)
        get_process_data_mock.assert_called_once_with()
        self.assertEqual(client.process_data, get_process_data_mock.return_value[0])
        self.assertEqual(client.shared_data, get_process_data_mock.return_value[1])
        call2 = call(client.screen, 'get-process-data', {})
        self.assertTrue(call2 in update_screen_status_patch.mock_calls)
        self.assertEqual(client.processes_to_start, 2)

    @patch('mpcurses.mpcurses.update_screen_status')
    def test__execute_get_process_data_Should_CallExpected_When_GetProcessDataStartProcesses(self, update_screen_status_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        get_process_data_mock = Mock(__name__='get_my_process_data', __doc__='getting data')
        get_process_data_mock.return_value = ([{'data': 1}, {'data': 2}], {'arg1': 'value1', 'arg2': 'value2', 'arg3': 'value3'})
        client = MPcurses(function=function_mock, get_process_data=get_process_data_mock, screen_layout={'_screen': {}}, processes_to_start=1, shared_data={'arg1': 'value1', 'arg2': 'value2'})
        client.execute_get_process_data()
        client.screen = None
        call1 = call(client.screen, 'get-process-data', {}, data='getting data')
        self.assertTrue(call1 in update_screen_status_patch.mock_calls)
        get_process_data_mock.assert_called_once_with(arg1='value1', arg2='value2')
        self.assertEqual(client.process_data, get_process_data_mock.return_value[0])
        self.assertEqual(client.shared_data, get_process_data_mock.return_value[1])
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
            'offset': 0,
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
            'offset': 3,
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

    @patch('mpcurses.MPcurses.run')
    def test__execute_run_Should_CallExpected_When_NoScreenLayout(self, run_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=function_mock, process_data=process_data)
        client.execute_run()
        run_patch.assert_called_once_with()

    @patch('mpcurses.MPcurses.run_screen')
    @patch('mpcurses.mpcurses.wrapper')
    def test__execute_run_Should_CallExpected_When_ScreenLayout(self, wrapper_patch, run_screen_patch, *patches):
        function_mock = Mock(__name__='mockfunc')
        process_data = [{'range': '0-1'}]
        client = MPcurses(function=function_mock, process_data=process_data, screen_layout={'_screen': {'blink': False}})
        client.execute_run()
        wrapper_patch.assert_called_once_with(run_screen_patch)
