
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

from mpcurses.screen import initialize_colors
from mpcurses.screen import create_default_window
from mpcurses.screen import create_windows
from mpcurses.screen import assign_windows
from mpcurses.screen import initialize_counter
from mpcurses.screen import initialize_keep_count
from mpcurses.screen import initialize_screen
from mpcurses.screen import finalize_screen
from mpcurses.screen import get_category_values
from mpcurses.screen import sanitize_message
from mpcurses.screen import update_screen
from mpcurses.screen import blink_running
from mpcurses.screen import echo_to_screen
from mpcurses.screen import refresh_screen
from mpcurses.screen import get_position
from mpcurses.screen import process_counter
from mpcurses.screen import get_category_color
from mpcurses.screen import get_category_count
from mpcurses.screen import get_category_x_pos
from mpcurses.screen import get_category_y_pos
from mpcurses.screen import initialize_text

import sys
import logging
logger = logging.getLogger(__name__)


class TestScreen(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('mpcurses.screen.curses')
    def test__initialize_colors_Should_CallInitPair_When_Called(self, curses_mock, *patches):
        curses_mock.COLORS = 3
        initialize_colors()
        curses_mock.start_color.asset_called_with()
        curses_mock.use_default_colors.assert_called_with()

        init_pair_call_1 = call(0, 0, -1)
        init_pair_call_2 = call(1, 1, -1)
        self.assertEqual(curses_mock.init_pair.mock_calls[0], init_pair_call_1)
        self.assertEqual(curses_mock.init_pair.mock_calls[1], init_pair_call_2)

    def test__create_default_window_Should_ReturnExpected_When_Called(self, *patches):
        screen_layout = {}
        create_default_window(screen_layout)
        expected_result = {
            'default': {
                'window': True,
                'begin_y': 0,
                'begin_x': 0,
                'height': 20,
                'width': 200
            }
        }
        self.assertEqual(screen_layout, expected_result)

    @patch('mpcurses.screen.create_default_window')
    @patch('mpcurses.screen.curses.newwin')
    def test__create_windows_Should_ReturnExpected_When_Called(self, newwin_patch, create_default_window_patch, *patches):
        window1_mock = Mock()
        window2_mock = Mock()
        newwin_patch.side_effect = [
            window1_mock,
            window2_mock,
        ]
        screen_layout = {
            'default': {
                'window': True,
                'begin_y': 0,
                'begin_x': 0,
                'height': 21,
                'width': 300
            },
            'window_legend': {
                'window': True,
                'begin_y': 22,
                'begin_x': 0,
                'height': 3,
                'width': 300
            }
        }
        result = create_windows(screen_layout)
        expected_result = {
            'default': window1_mock,
            'window_legend': window2_mock,
        }
        self.assertEqual(result, expected_result)
        newwin_call1 = call(21, 300, 0, 0)
        newwin_call2 = call(3, 300, 22, 0)
        self.assertTrue(newwin_call1 in newwin_patch.mock_calls)
        self.assertTrue(newwin_call2 in newwin_patch.mock_calls)
        create_default_window_patch.assert_not_called()

    @patch('mpcurses.screen.create_default_window')
    @patch('mpcurses.screen.curses.newwin')
    def test__create_windows_Should_CallExpected_When_NoDefault(self, newwin_patch, create_default_window_patch, *patches):
        window1_mock = Mock()
        newwin_patch.side_effect = [
            window1_mock
        ]
        screen_layout = {
            'window_legend': {
                'window': True,
                'begin_y': 22,
                'begin_x': 0,
                'height': 3,
                'width': 300
            }
        }
        result = create_windows(screen_layout)
        expected_result = {
            'window_legend': window1_mock,
        }
        self.assertEqual(result, expected_result)
        newwin_call = call(3, 300, 22, 0)
        self.assertTrue(newwin_call in newwin_patch.mock_calls)
        create_default_window_patch.assert_called_once_with(screen_layout)

    def test__assign_windows_Should_UpdateScrenLayout_When_Called(self, *patches):
        window1_mock = Mock()
        window2_mock = Mock()
        screen_layout = {
            'default': {
            },
            'window_legend': {
            },
            'procs_complete': {
                'window_id': 'window_legend',
            },
            'bay_header': {
            },
            'server_header': {
            },
        }
        windows = {
            'default': window1_mock,
            'window_legend': window2_mock,
        }
        assign_windows(windows, screen_layout)
        expected_screen_layout = {
            'default': {
                '_window': window1_mock
            },
            'window_legend': {
                '_window': window1_mock
            },
            'procs_complete': {
                'window_id': 'window_legend',
                '_window': window2_mock
            },
            'bay_header': {
                '_window': window1_mock
            },
            'server_header': {
                '_window': window1_mock
            },
        }
        self.assertEqual(screen_layout, expected_screen_layout)

    def test__initialize_counter_Should_UpdateScreenLayout_When_Called(self, *patches):
        screen_layout = {
            '_counter_': {
                'modulus': 5
            }
        }
        initialize_counter(3, screen_layout)
        expected_screen_layout = {
            '_counter_': {
                'modulus': 5,
                0: {
                    '_count': 0,
                    '_modulus_count': 0
                },
                1: {
                    '_count': 0,
                    '_modulus_count': 0
                },
                2: {
                    '_count': 0,
                    '_modulus_count': 0
                }
            }
        }
        self.assertEqual(screen_layout, expected_screen_layout)

    def test__initialize_keep_count_Should_UpdateScreenLayout_When_Table(self, *patches):
        screen_layout = {
            'networks': {
                'table': True
            }
        }
        initialize_keep_count('networks', 3, screen_layout)
        expected_screen_layout = {
            'networks': {
                'table': True,
                0: {
                    '_count': 0
                },
                1: {
                    '_count': 0
                },
                2: {
                    '_count': 0
                }
            }
        }
        self.assertEqual(screen_layout, expected_screen_layout)

    def test__initialize_keep_count_Should_UpdateScreenLayout_When_NoTable(self, *patches):
        screen_layout = {
            'networks': {
            }
        }
        initialize_keep_count('networks', 3, screen_layout)
        expected_screen_layout = {
            'networks': {
                '_count': 0
            }
        }
        self.assertEqual(screen_layout, expected_screen_layout)

    @patch('mpcurses.screen.initialize_colors')
    def test__initialize_screen_Should_Return_When_NoScreen(self, initialize_colors_patch, *patches):
        initialize_screen(None, {}, 3)
        initialize_colors_patch.assert_not_called()

    @patch('mpcurses.screen.assign_windows')
    @patch('mpcurses.screen.create_windows')
    @patch('mpcurses.screen.curses.curs_set')
    @patch('mpcurses.screen.initialize_colors')
    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.initialize_keep_count')
    @patch('mpcurses.screen.initialize_counter')
    def test__initialize_screen_Should_CallExpected_When_Called(self, initialize_counter_patch, initialize_keep_count_patch, color_pair_patch, *patches):
        color_pair_mock = Mock()
        color_pair_patch.return_value = color_pair_mock
        screen_mock = Mock()
        default_window_mock = Mock()
        screen_layout = {
            'default': {
                'window': True,
                'begin_y': 0,
                'begin_x': 0,
                'height': 27,
                'width': 300
            },
            'translated': {
                'position': (3, 0),
                'text': 'Networks Translated: 0',
                'text_color': 244,
                'color': 3,
                'keep_count': True,
                'regex': '^network ".*" was translated$',
                '_window': default_window_mock,
            },
            '_counter_': {
                'position': (6, 0),
                'categories': [
                    'translated',
                    'blacklisted',
                    'not_translated'
                ],
                'counter_text': '|',
                '_window': default_window_mock,
            }
        }
        initialize_screen(screen_mock, screen_layout, 1)
        initialize_counter_patch.assert_called_once_with(1, screen_layout)
        default_window_mock.addstr.assert_called_once_with(3, 0, 'Networks Translated: 0', color_pair_mock)
        initialize_keep_count_patch.assert_called_once_with('translated', 1, screen_layout)

    @patch('mpcurses.screen.assign_windows')
    @patch('mpcurses.screen.create_windows')
    @patch('mpcurses.screen.curses.curs_set')
    @patch('mpcurses.screen.initialize_colors')
    def test__initialize_screen_Should_CallScreenRefresh_When_Called(self, *patches):
        screen_mock = Mock()
        initialize_screen(screen_mock, {}, 1)
        screen_mock.refresh.assert_called_once_with()

    @patch('mpcurses.screen.assign_windows')
    @patch('mpcurses.screen.curses.curs_set')
    @patch('mpcurses.screen.initialize_colors')
    @patch('mpcurses.screen.create_windows')
    def test__initialize_screen_Should_CallWindowRefresh_When_Called(self, create_windows_patch, *patches):
        window1_mock = Mock()
        window2_mock = Mock()
        create_windows_patch.return_value = {
            'category1': window1_mock,
            'category2': window2_mock
        }
        screen_mock = Mock()
        initialize_screen(screen_mock, {}, 1)
        window1_mock.refresh.assert_called_once_with()
        window2_mock.refresh.assert_called_once_with()

    def test__finialize_screen_Should_Return_When_NoScreen(self, *patches):
        window_mock = Mock()
        screen_layout = {
            'default': {
                '_window': window_mock
            }
        }
        finalize_screen(None, screen_layout)
        window_mock.move.assert_not_called()

    @patch('mpcurses.screen.initialize_colors')
    @patch('mpcurses.screen.curses')
    def test__finalize_screen_ShouldCallExpected_When_ScreenLayoutClearEnd(self, curses_patch, *patches):
        window_mock = Mock()
        window_mock.getch.return_value = 113
        screen_layout = {
            'default': {
                'window': True,
                'begin_y': 0,
                'begin_x': 0,
                'height': 20,
                'width': 300,
                '_window': window_mock
            },
            'extracted': {
                'text': 'Status:',
                'color': 4,
                'position': (4, 0),
                'clear_end': True,
                '_window': window_mock
            }
        }
        screen_mock = Mock()
        finalize_screen(screen_mock, screen_layout)

        window_mock.move.assert_called_with(4, 0)
        window_mock.clrtoeol.assert_called_with()
        window_mock.addstr.assert_called_with(0, 0, '[Press q to exit]', curses_patch.color_pair(12))
        window_mock.refresh.assert_called_with()
        window_mock.getch.assert_called_with()
        curses_patch.curs_set.assert_called_with(2)

    def test__get_category_values_Should_ReturnExpected_When_Match(self, *patches):
        screen_layout = {
            'firmware': {
                'regex': '^.* firmware version for bay \\d+ is "(?P<value>.*)"$'
            },
            'start': {
                'regex': '^processing bay \\d+ at: (?P<value>.*)$'
            },
            'message': {
                'regex': '^(?P<value>.*)$',
            },
            'start_new_bay': {
                'regex': '^processing next bay$'
            }
        }

        message = 'processing bay 4 at: -date-time-'
        result = get_category_values(message, 0, screen_layout)
        expected_result = [
            ('start', '-date-time-'),
            ('message', 'processing bay 4 at: -date-time-')
        ]
        self.assertEqual(result, expected_result)

    def test__get_category_values_Should_ReturnExpected_When_LengthGreaterThanWidth(self, *patches):
        screen_layout = {
            'message': {
                'regex': '^(?P<value>.*)$',
            }
        }

        message = 'eramos todos de papel, liso y blanco, sin dolor, y fuimos hechos para andar, de par en par, sin reclamar, hare tiempo me dijeron que aqui no pasa nada'
        result = get_category_values(message, 0, screen_layout)
        expected_result = [
            ('message', 'eramos todos de papel, liso y blanco, sin dolor, y fuimos hechos para andar, de par en par, sin recl...'),
        ]
        self.assertEqual(result, expected_result)

    def test__get_category_values_Should_ReturnExpected_When_RightJustify(self, *patches):
        screen_layout = {
            'message': {
                'width': 20,
                'right_justify': True,
                'regex': '^(?P<value>.*)$',
            }
        }

        message = 'cambridge-limited'
        result = get_category_values(message, 0, screen_layout)
        expected_result = [
            ('message', '   cambridge-limited'),
        ]
        self.assertEqual(result, expected_result)

    @patch('mpcurses.screen.get_category_count', return_value='012')
    def test__get_category_values_Should_ReturnExpected_When_KeepCount(self, *patches):
        screen_layout = {
            'message': {
                'keep_count': True,
                'regex': '^network .* was translated$',
            }
        }

        message = 'network cambridge-limited was translated'
        result = get_category_values(message, 0, screen_layout)
        expected_result = [
            ('message', '012'),
        ]
        self.assertEqual(result, expected_result)

    def test__get_category_values_Should_ReturnExpected_When_ReplaceText(self, *patches):
        screen_layout = {
            'message': {
                'replace_text': '=>',
                'regex': '^processing item .*$',
            }
        }

        message = 'processing item cambridge-limited'
        result = get_category_values(message, 0, screen_layout)
        expected_result = [
            ('message', '=>'),
        ]
        self.assertEqual(result, expected_result)

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_CategoryModulus(self, color_pair_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            'translated': {
                'color': 31,
                '_window': window_mock
            },
            '_counter_': {
                'position': (6, 0),
                'categories': [
                    'translated',
                ],
                'counter_text': '|',
                'modulus': 5,
                'color': 21,
                'regex': '^(?P<value>\\d+) networks extracted$',
                1: {
                    '_count': 44,
                    '_modulus_count': 3
                },
            }
        }
        process_counter(1, 'translated', 10, screen_layout)
        window_mock.addstr.assert_called_once_with(7, 4, '|', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(21)

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_CategoryNoModulus(self, color_pair_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            'translated': {
                'color': 31,
                '_window': window_mock
            },
            '_counter_': {
                'position': (6, 0),
                'categories': [
                    'translated',
                ],
                'counter_text': '|',
                1: {
                    '_count': 44,
                },
            }
        }
        process_counter(1, 'translated', 10, screen_layout)
        window_mock.addstr.assert_called_once_with(7, 44, '|', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(31)

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_Counter(self, color_pair_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            '_counter_': {
                'position': (6, 0),
                'categories': [
                    'translated',
                ],
                'counter_text': '|',
                'modulus': 5,
                'color': 45,
                'regex': '^(?P<value>\\d+) networks extracted$',
                1: {
                    '_count': 0,
                    '_modulus_count': 0
                },
                '_window': window_mock
            }
        }
        process_counter(1, '_counter_', 100, screen_layout)
        spaces = ' ' * 20  # 100/5
        window_mock.addstr.assert_called_once_with(7, 0, '[{}]'.format(spaces), color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(45)

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_Width(self, color_pair_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            'translated': {
                'color': 31,
                '_window': window_mock
            },
            '_counter_': {
                'position': (6, 10),
                'categories': [
                    'translated',
                ],
                'counter_text': '|',
                'width': 5,
                0: {
                    '_count': 44,
                },
            }
        }
        process_counter(0, 'translated', 10, screen_layout)
        window_mock.addstr.assert_called_once_with(6, 54, '|', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(31)
        self.assertEqual(screen_layout['_counter_']['position'], (7, 10))

    def test__get_category_color_Should_ReturnExpected_When_EffectMatch(self, *patches):
        screen_layout = {
            'firmware': {
                'color': 1,
                'effects': [
                    {
                        'regex': '.*2.64.*$',
                        'color': 3
                    }
                ],
            }
        }
        result = get_category_color('firmware', 'firmware is: 2.64.1', screen_layout)
        expected_result = 3
        self.assertEqual(result, expected_result)

    def test__get_category_color_Should_ReturnExpected_When_NoEffectMatch(self, *patches):
        screen_layout = {
            'firmware': {
                'color': 1,
                'effects': [
                    {
                        'regex': '.*2.64.*$',
                        'color': 3
                    }
                ],
            }
        }
        result = get_category_color('firmware', 'firmware is: 4.24.1', screen_layout)
        expected_result = 1
        self.assertEqual(result, expected_result)

    def test__get_category_count_Should_ReturnExpected_When_Table(self, *patches):
        screen_layout = {
            'translated': {
                'table': True,
                3: {
                    '_count': 3201
                }
            }
        }
        result = get_category_count('translated', 3, screen_layout)
        expected_result = '3202'
        self.assertEqual(result, expected_result)

    def test__get_category_count_Should_ReturnExpected_When_NoTableAndZfill(self, *patches):
        screen_layout = {
            'translated': {
                '_count': 21,
                'zfill': 5
            }
        }
        result = get_category_count('translated', 3, screen_layout)
        expected_result = '00022'
        self.assertEqual(result, expected_result)

    @patch('mpcurses.screen.get_position')
    def test__get_category_x_pos_Should_ReturnExpected_When_Text(self, get_position_patch, *patches):
        get_position_patch.return_value = 6
        screen_layout = {
            'start': {
                'position': (5, 12),
                'text': 'Title:',
            }
        }
        result = get_category_x_pos('start', 0, screen_layout)
        expected_result = 19
        self.assertEqual(result, expected_result)

    def test__get_category_x_pos_Should_ReturnExpected_When_NoText(self, *patches):
        screen_layout = {
            'start': {
                'position': (5, 12),
            }
        }
        result = get_category_x_pos('start', 0, screen_layout)
        expected_result = 12
        self.assertEqual(result, expected_result)

    def test__get_category_x_pos_Should_ReturnExpected_When_TableWraparound(self, *patches):
        screen_layout = {
            'table': {
                'rows': 3,
                'width': 40,
                'cols': 3
            },
            'start': {
                'position': (5, 12),
                'table': True
            }
        }
        result = get_category_x_pos('start', 7, screen_layout)
        expected_result = 92
        self.assertEqual(result, expected_result)

    def test__get_category_y_pos_Should_ReturnExpected_When_TableNoWraparound(self, *patches):
        screen_layout = {
            'start': {
                'position': (5, 12),
                'table': True
            }
        }
        result = get_category_y_pos('start', 4, screen_layout)
        expected_result = 9
        self.assertEqual(result, expected_result)

    def test__get_category_y_pos_Should_ReturnExpected_When_NoTable(self, *patches):
        screen_layout = {
            'start': {
                'position': (5, 12),
            }
        }
        result = get_category_y_pos('start', 4, screen_layout)
        expected_result = 5
        self.assertEqual(result, expected_result)

    def test__get_category_y_pos_Should_ReturnExpected_When_TableWraparound(self, *patches):
        screen_layout = {
            'table': {
                'rows': 3,
                'width': 40,
                'cols': 3
            },
            'start': {
                'position': (5, 12),
                'table': True
            }
        }
        result = get_category_y_pos('start', 7, screen_layout)
        expected_result = 6
        self.assertEqual(result, expected_result)

    @patch('mpcurses.screen.sanitize_message')
    def test__update_screen_Should_Return_When_NoScreen(self, sanitize_message_patch, *patches):
        update_screen('message', None, {})
        sanitize_message_patch.assert_not_called()

    @patch('mpcurses.screen.get_category_values', return_value=None)
    @patch('mpcurses.screen.sanitize_message', return_value=(None, None))
    @patch('mpcurses.screen.logger')
    def test__update_screen_Should_LogError_When_Exception(self, logger_patch, *patches):
        update_screen('message', Mock(), {})
        logger_patch.error.assert_called()

    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.get_category_values')
    @patch('mpcurses.screen.sanitize_message')
    def test__update_screen_Should_CallExpected_When_ReplaceText(self, sanitize_message_patch, get_category_values_patch, color_pair_patch, *patches):
        sanitize_message_patch.return_value = (5, 'processing bay 5 at: 01/30/18 13:24')
        get_category_values_patch.return_value = [
            # ['start', 'processing bay 5 at: 01/30/18 13:24'],
            ['start', '*'],
        ]
        window_mock = Mock()
        screen_layout = {
            'start': {
                'position': (5, 57),
                'text': '',
                'replace_text': '*',
                'color': 0,
                'table': True,
                '_window': window_mock
            }
        }
        message = '#5-processing bay 5 at: 01/30/18 13:24'
        screen_mock = Mock()
        update_screen(message, screen_mock, screen_layout)
        window_mock.addstr.assert_called_with(10, 57, '*', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(0)

    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.get_category_values')
    @patch('mpcurses.screen.sanitize_message')
    def test__update_screen_Should_CallExpected_When_Effects(self, sanitize_message_patch, get_category_values_patch, color_pair_patch, *patches):
        sanitize_message_patch.return_value = (5, 'firmware is: 2.64.1')
        get_category_values_patch.return_value = [
            ['firmware', '2.64.1'],
        ]
        window_mock = Mock()
        screen_layout = {
            'firmware': {
                'position': (3, 34),
                'color': 1,
                'effects': [
                    {
                        'regex': '.*2.64.*$',
                        'color': 3
                    }
                ],
                'table': True,
                '_window': window_mock
            }
        }
        message = '#5-firmware is: 2.64.1'
        screen_mock = Mock()
        update_screen(message, screen_mock, screen_layout)
        window_mock.addstr.assert_called_with(8, 34, '2.64.1', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(3)

    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.get_category_values')
    @patch('mpcurses.screen.sanitize_message')
    def test__update_screen_Should_CallExpected_When_Clear(self, sanitize_message_patch, get_category_values_patch, color_pair_patch, *patches):
        sanitize_message_patch.return_value = (4, 'checking 121372')
        get_category_values_patch.return_value = [
            ['number', '121372'],
        ]
        window_mock = Mock()
        screen_layout = {
            'number': {
                'table': True,
                'position': (1, 0),
                'clear': True,
                '_window': window_mock
            }
        }
        message = '#4-checking 121372'
        screen_mock = Mock()
        update_screen(message, screen_mock, screen_layout)
        window_mock.move.assert_called_once_with(5, 0)
        window_mock.clrtoeol.assert_called_once_with()

    @patch('mpcurses.screen.process_counter')
    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.get_category_values')
    @patch('mpcurses.screen.sanitize_message')
    def test__update_screen_Should_CallExpected_When_TextKeepCountCounterTable(self, sanitize_message_patch, get_category_values_patch, color_pair_patch, process_counter_patch, *patches):
        sanitize_message_patch.return_value = (3, 'network powerdac1234 was translated')
        get_category_values_patch.return_value = [
            # ['translated', 'network powerdac1234 was translated'],
            ['translated', '033'],
        ]
        window_mock = Mock()
        screen_layout = {
            'translated': {
                'position': (3, 0),
                'text': 'Networks Translated: 0',
                'color': 241,
                'keep_count': True,
                'table': True,
                '_window': window_mock,
                3: {
                    '_count': 32
                }
            },
            '_counter_': {
            }
        }
        message = '#3-network powerdac1234 was translated'
        screen_mock = Mock()
        update_screen(message, screen_mock, screen_layout)
        window_mock.addstr.assert_called_with(6, 21, '033', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(241)
        process_counter_patch.assert_called_once_with(3, 'translated', '033', screen_layout)

    @patch('mpcurses.screen.process_counter')
    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.get_category_values')
    @patch('mpcurses.screen.sanitize_message')
    def test__update_screen_Should_CallExpected_When_TextKeepCountCounter(self, sanitize_message_patch, get_category_values_patch, color_pair_patch, process_counter_patch, *patches):
        sanitize_message_patch.return_value = (3, 'network powerdac1234 was translated')
        get_category_values_patch.return_value = [
            # ['translated', 'network powerdac1234 was translated'],
            ['translated', '033'],
        ]
        window_mock = Mock()
        screen_layout = {
            'translated': {
                'position': (3, 0),
                'text': 'Networks Translated: 0',
                'color': 241,
                'keep_count': True,
                '_window': window_mock,
                '_count': 32
            },
            '_counter_': {
            }
        }
        message = '#3-network powerdac1234 was translated'
        screen_mock = Mock()
        update_screen(message, screen_mock, screen_layout)
        window_mock.addstr.assert_called_with(3, 21, '033', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(241)
        process_counter_patch.assert_called_once_with(3, 'translated', '033', screen_layout)

    @patch('mpcurses.screen.time')
    def test__blink_running_Should_Return_When_NoScreen(self, time_patch, *patches):
        blink_running(None, {})
        time_patch.assert_not_called()

    @patch('mpcurses.screen.time')
    @patch('mpcurses.screen.curses')
    def test__blink_running_Should_BlinkOff_When_BlinkOnAndTimeDeltaMet(self, curses_patch, time_patch, *patches):
        time_patch.return_value = 1517465190.000000
        blink_meta = {
            'blink_on_time': 1517465187.000000,
            'blink_off_time': 1517465188.000000,
            'blink_on': True
        }

        screen_mock = Mock()
        blink_running(screen_mock, blink_meta)

        screen_mock.addstr.assert_called_once_with(0, 0, ' RUNNING ', curses_patch.color_pair(1))
        self.assertFalse(blink_meta['blink_on'])
        self.assertEqual(blink_meta['blink_off_time'], time_patch.return_value)

    @patch('mpcurses.screen.time')
    @patch('mpcurses.screen.curses')
    def test__blink_running_Should_BlinkOn_When_BlinkOffAndTimeDeltaMet(self, curses_patch, time_patch, *patches):
        time_patch.return_value = 1517465190.000000
        blink_meta = {
            'blink_on_time': 1517465187.000000,
            'blink_off_time': 1517465188.000000,
            'blink_on': False
        }

        screen_mock = Mock()
        blink_running(screen_mock, blink_meta)

        screen_mock.addstr.assert_called_once_with(0, 0, ' RUNNING ', curses_patch.color_pair(12))
        self.assertTrue(blink_meta['blink_on'])
        self.assertEqual(blink_meta['blink_on_time'], time_patch.return_value)

    @patch('mpcurses.screen.time')
    @patch('mpcurses.screen.curses')
    def test__blink_running_Should_DoNothing_When_BlinkOffAndTimeDeltaNotMet(self, curses_patch, time_patch, *patches):
        time_patch.return_value = 1517465188.000001
        blink_meta = {
            'blink_on_time': 1517465187.000000,
            'blink_off_time': 1517465188.000001,
            'blink_on': False
        }

        screen_mock = Mock()
        blink_running(screen_mock, blink_meta)

        screen_mock.addstr.assert_not_called()
        self.assertFalse(blink_meta['blink_on'])

    @patch('mpcurses.screen.time')
    @patch('mpcurses.screen.curses')
    def test__blink_running_Should_SetBlinkMeta_When_BlinkMetaNone(self, curses_patch, time_patch, *patches):
        time_patch.return_value = 1517465188.000001
        blink_meta = {
        }

        screen_mock = Mock()
        blink_running(screen_mock, blink_meta)

        screen_mock.addstr.assert_called_once_with(0, 0, ' RUNNING ', curses_patch.color_pair(12))
        self.assertTrue(blink_meta['blink_on'])
        self.assertEqual(blink_meta['blink_on_time'], time_patch.return_value)
        self.assertEqual(blink_meta['blink_off_time'], time_patch.return_value)

    def test__sanitize_message_Should_ReturnExepcted_When_NoMatchForProcessNumber(self, *patches):
        message = 'INFO: this is an informational log message'
        offset, sanitized_message = sanitize_message(message)
        self.assertEqual(0, offset)
        self.assertEqual(message, sanitized_message)

    def test__sanitize_message_Should_ReturnExepcted_When_MatchForProcessNumber(self, *patches):
        message = '#4-INFO: this is an informational log message'
        offset, sanitized_message = sanitize_message(message)
        self.assertEqual(offset, 4)
        self.assertEqual(sanitized_message, 'INFO: this is an informational log message')

    @patch('mpcurses.screen.update_screen')
    def test__echo_to_screen_Should_NotCallUpdateScreen_When_ScreenIsNone(self, update_screen_patch, *patches):
        echo_to_screen(None, {}, {})
        update_screen_patch.assert_not_called()

    @patch('mpcurses.screen.update_screen')
    def test__echo_to_screen_Should_CallUpdateScreen_When_Screen(self, update_screen_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = Mock()
        data = {
            'key1': True,
            'key2': 1,
            'key3': 3.14,
            'key4': 'the value of key4',
            'key5': {'k1': 'v1', 'k2': 'v2'},
            'key6': ('k1', 'k2', 'k3'),
            'key7': ['k1', 'k2', 'k3', 'k4'],
            'key8': Mock()
        }
        echo_to_screen(screen_mock, data, screen_layout_mock)
        self.assertTrue(call("'key1' is 'True'", screen_mock, screen_layout_mock) in update_screen_patch.mock_calls)
        self.assertTrue(call("'key2' is '1'", screen_mock, screen_layout_mock) in update_screen_patch.mock_calls)
        self.assertTrue(call("'key3' is '3.14'", screen_mock, screen_layout_mock) in update_screen_patch.mock_calls)
        self.assertTrue(call("'key4' is 'the value of key4'", screen_mock, screen_layout_mock) in update_screen_patch.mock_calls)
        self.assertTrue(call("'key5' has 2 items", screen_mock, screen_layout_mock) in update_screen_patch.mock_calls)
        self.assertTrue(call("'key6' has 3 items", screen_mock, screen_layout_mock) in update_screen_patch.mock_calls)
        self.assertTrue(call("'key7' has 4 items", screen_mock, screen_layout_mock) in update_screen_patch.mock_calls)

    def test__refresh_screen_Should_NotCallScreenRefresh_When_ScreenIsNone(self, *patches):
        self.assertIsNone(refresh_screen(None))

    def test__get_position_Should_ReturnExpected_When_Semicolon(self, *patches):
        self.assertEqual(get_position('data: 0'), 5)

    def test__get_position_Should_ReturnExpected_When_NoSemicolon(self, *patches):
        self.assertEqual(get_position('string'), 7)

    def test__get_position_Should_ReturnExpected_When_InitText(self, *patches):
        self.assertEqual(get_position('---'), -1)

    @patch('mpcurses.screen.curses')
    def test__initialize_text_Should_CallExpected_When_Table(self, *patches):
        window_mock = Mock()
        screen_layout = {
            'cat1': {
                'table': True,
                'position': (2, 0),
                'text': '---',
                'text_color': 1,
                '_window': window_mock
            }
        }
        initialize_text(4, 'cat1', screen_layout)
        self.assertTrue(len(window_mock.addstr.mock_calls) == 4)
