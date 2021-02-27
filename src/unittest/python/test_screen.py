
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

from mpcurses.screen import initialize_colors
from mpcurses.screen import initialize_counter
from mpcurses.screen import initialize_keep_count
from mpcurses.screen import update_screen_status
from mpcurses.screen import initialize_screen
from mpcurses.screen import initialize_screen_offsets
from mpcurses.screen import finalize_screen
from mpcurses.screen import get_category_values
from mpcurses.screen import sanitize_message
from mpcurses.screen import update_screen
from mpcurses.screen import echo_to_screen
from mpcurses.screen import refresh_screen
from mpcurses.screen import get_position
from mpcurses.screen import process_clear
from mpcurses.screen import process_counter
from mpcurses.screen import get_category_color
from mpcurses.screen import get_category_count
from mpcurses.screen import get_category_x_pos
from mpcurses.screen import get_category_y_pos
from mpcurses.screen import initialize_text
from mpcurses.screen import get_table_position
from mpcurses.screen import get_positions_to_update
from mpcurses.screen import update_positions
from mpcurses.screen import squash_table
from mpcurses.screen import set_screen_defaults
from mpcurses.screen import set_screen_defaults_processes
from mpcurses.screen import validate_screen_layout_processes
from mpcurses.screen import validate_screen_size
from mpcurses.screen import blink

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

    def test__initialize_counter_Should_UpdateScreenLayout_When_Modulus(self, *patches):
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

    def test__initialize_counter_Should_UpdateScreenLayout_When_NoModulus(self, *patches):
        screen_layout = {
            '_counter_': {
            }
        }
        initialize_counter(3, screen_layout)
        expected_screen_layout = {
            '_counter_': {
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

    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.get_category_x_pos')
    @patch('mpcurses.screen.get_category_y_pos')
    def test__initialize_text_Should_CallExpected_When_Table(self, get_category_y_pos_patch, get_category_x_pos_patch, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'category_with_table': {
                'text': 'Text Label',
                'text_color': 0,
                'table': True
            }
        }
        offsets = 2
        initialize_text(offsets, 'category_with_table', screen_layout_mock, screen_mock)
        screen_addstr_call = call(get_category_y_pos_patch.return_value, get_category_x_pos_patch.return_value, 'Text Label', color_pair_patch.return_value)
        self.assertTrue(screen_addstr_call in screen_mock.addstr.mock_calls)
        self.assertTrue(len(screen_mock.addstr.mock_calls) == offsets)

    @patch('mpcurses.screen.curses.color_pair')
    def test__initialize_text_Should_CallExpected_When_NoTable(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'category_without_table': {
                'position': (1, 2),
                'text': 'Text Label',
                'text_color': 0
            }
        }
        offsets = 0
        initialize_text(offsets, 'category_without_table', screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_called_once_with(1, 2, 'Text Label', color_pair_patch.return_value)

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

    @patch('mpcurses.screen.curses.color_pair')
    def test__update_screen_status_Should_CallExpected_When_StateInitialize(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (100, 200)
        config_mock = {
            'title': 'Script A',
            'color': 0,
            'show_process_status': False
        }
        update_screen_status(screen_mock, 'initialize', config_mock)
        call1 = call(0, 0, ' ' * 199, color_pair_patch.return_value)
        call2 = call(0, 200 - len(config_mock['title']) - 1, config_mock['title'], color_pair_patch.return_value)
        self.assertTrue(call1 in screen_mock.addstr.mock_calls)
        self.assertTrue(call2 in screen_mock.addstr.mock_calls)

    @patch('mpcurses.screen.curses.color_pair')
    def test__update_screen_status_Should_CallExpected_When_StateFinalize(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (100, 200)
        config_mock = {
            'color': 0
        }
        update_screen_status(screen_mock, 'finalize', config_mock)
        screen_mock.addstr.assert_called_once_with(0, 1, '[Press q to exit]', color_pair_patch.return_value)

    @patch('mpcurses.screen.curses.color_pair')
    def test__update_screen_status_Should_CallExpected_When_StateBlinkOn(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (100, 200)
        config_mock = {
            'color': 0
        }
        update_screen_status(screen_mock, 'blink-on', config_mock)
        screen_mock.addstr.assert_called_once_with(0, 1, 'RUNNING', color_pair_patch.return_value)

    @patch('mpcurses.screen.curses.color_pair')
    def test__update_screen_status_Should_CallExpected_When_StateBlinkOff(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (100, 200)
        config_mock = {
            'color': 0
        }
        update_screen_status(screen_mock, 'blink-off', config_mock)
        screen_mock.addstr.assert_called_once_with(0, 1, ' ' * len('RUNNING'), color_pair_patch.return_value)

    @patch('mpcurses.screen.curses.color_pair')
    def test__update_screen_status_Should_CallExpected_When_ProcessUpdateNone(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (100, 200)
        config_mock = {
            'color': 0,
            'show_process_status': True,
            'zfill': 2
        }
        update_screen_status(screen_mock, 'process-update', config_mock)
        call1 = call(96, 1, '  Running: 00', color_pair_patch.return_value)
        call2 = call(97, 1, '   Queued: 00', color_pair_patch.return_value)
        call3 = call(98, 1, 'Completed: 00', color_pair_patch.return_value)
        self.assertTrue(call1 in screen_mock.addstr.mock_calls)
        self.assertTrue(call2 in screen_mock.addstr.mock_calls)
        self.assertTrue(call3 in screen_mock.addstr.mock_calls)

    @patch('mpcurses.screen.curses.color_pair')
    def test__update_screen_status_Should_CallExpected_When_ProcessUpdate(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (100, 200)
        config_mock = {
            'color': 0,
            'show_process_status': True,
            'zfill': 2
        }
        update_screen_status(screen_mock, 'process-update', config_mock, running=10, queued=5, completed=2)
        call1 = call(96, 1, '  Running: 10', color_pair_patch.return_value)
        call2 = call(97, 1, '   Queued: 05', color_pair_patch.return_value)
        call3 = call(98, 1, 'Completed: 02', color_pair_patch.return_value)
        self.assertTrue(call1 in screen_mock.addstr.mock_calls)
        self.assertTrue(call2 in screen_mock.addstr.mock_calls)
        self.assertTrue(call3 in screen_mock.addstr.mock_calls)

    @patch('mpcurses.screen.curses.color_pair')
    def test__update_screen_status_Should_CallExpected_When_GetProcessDataWithData(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (100, 200)
        config_mock = {
            'color': 0
        }
        update_screen_status(screen_mock, 'get-process-data', config_mock, data=' getting some data\nrest of\n docstr\n')
        call1 = call(48, 79, 'Getting some data... this may take awhile', color_pair_patch.return_value)
        self.assertTrue(call1 in screen_mock.addstr.mock_calls)

    @patch('mpcurses.screen.curses.color_pair')
    def test__update_screen_status_Should_CallExpected_When_GetProcessDataWithoutData(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (100, 200)
        config_mock = {
            'color': 0
        }
        update_screen_status(screen_mock, 'get-process-data', config_mock)
        screen_mock.move.assert_called_once_with(48, 0)
        screen_mock.clrtoeol.assert_called_once_with()

    @patch('mpcurses.screen.curses.curs_set')
    @patch('mpcurses.screen.initialize_colors')
    @patch('mpcurses.screen.update_screen_status')
    @patch('mpcurses.screen.validate_screen_size')
    @patch('mpcurses.screen.set_screen_defaults')
    def test__initialize_screen_Should_CallExpected_When_Called(self, set_screen_defaults_patch, validate_screen_size_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            '_screen': {
            },
            '_counter_': {
            }
        }
        initialize_screen(screen_mock, screen_layout_mock)
        set_screen_defaults_patch.assert_called_once_with(screen_layout_mock)
        validate_screen_size_patch.assert_called_once_with(screen_mock, screen_layout_mock)

    @patch('mpcurses.screen.update_screen_status')
    @patch('mpcurses.screen.validate_screen_layout_processes')
    @patch('mpcurses.screen.set_screen_defaults_processes')
    def test__initialize_screen_offsets_Should_CallExpected_When_Called(self, set_screen_defaults_processes_patch, validate_screen_layout_processes_patch, update_screen_status_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            '_screen': {
            }
        }
        initialize_screen_offsets(screen_mock, screen_layout_mock, 100, 10)
        set_screen_defaults_processes_patch.assert_called_once_with(100, 10, screen_layout_mock)
        validate_screen_layout_processes_patch.assert_called_once_with(100, screen_layout_mock)
        update_screen_status_patch.assert_called_once_with(screen_mock, 'process-update', screen_layout_mock['_screen'])

    @patch('mpcurses.screen.update_screen_status')
    @patch('mpcurses.screen.validate_screen_layout_processes')
    @patch('mpcurses.screen.set_screen_defaults_processes')
    @patch('mpcurses.screen.initialize_counter')
    def test__initialize_screen_offsets_Should_CallExpected_When_CounterCategory(self, initialize_counter_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            '_screen': {
            },
            '_counter_': {
            }
        }
        initialize_screen_offsets(screen_mock, screen_layout_mock, 1, 1)
        initialize_counter_patch.assert_called_once_with(1, screen_layout_mock)

    @patch('mpcurses.screen.update_screen_status')
    @patch('mpcurses.screen.validate_screen_layout_processes')
    @patch('mpcurses.screen.set_screen_defaults_processes')
    @patch('mpcurses.screen.initialize_text')
    def test__initialize_screen_offsets_Should_CallExpected_When_Text(self, initialize_text_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            '_screen': {
            },
            'category_with_text': {
                'text': 'Text Label'
            }
        }
        initialize_screen_offsets(screen_mock, screen_layout_mock, 1, 1)
        initialize_text_patch.assert_called_once_with(1, 'category_with_text', screen_layout_mock, screen_mock)

    @patch('mpcurses.screen.update_screen_status')
    @patch('mpcurses.screen.validate_screen_layout_processes')
    @patch('mpcurses.screen.set_screen_defaults_processes')
    def test__initialize_screen_offsets_Should_AddKeepCountToCategory_When_List(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            '_screen': {
            },
            'category_with_list': {
                'list': True
            }
        }
        initialize_screen_offsets(screen_mock, screen_layout_mock, 1, 1)
        self.assertTrue(screen_layout_mock['category_with_list']['keep_count'])

    @patch('mpcurses.screen.update_screen_status')
    @patch('mpcurses.screen.validate_screen_layout_processes')
    @patch('mpcurses.screen.set_screen_defaults_processes')
    @patch('mpcurses.screen.initialize_keep_count')
    def test__initialize_screen_offsets_Should_CallExpected_When_KeepCount(self, initialize_keep_count_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            '_screen': {
            },
            'category_with_keep_count': {
                'keep_count': True
            }
        }
        initialize_screen_offsets(screen_mock, screen_layout_mock, 1, 1)
        initialize_keep_count_patch.assert_called_once_with('category_with_keep_count', 1, screen_layout_mock)

    @patch('mpcurses.screen.update_screen_status')
    @patch('mpcurses.screen.curses')
    def test__finalize_screen_ShouldCallExpected_When_ScreenLayoutClearEnd(self, curses_patch, update_screen_status_patch, *patches):
        screen_mock = Mock()
        screen_mock.getch.side_effect = [112, 113]
        screen_layout_mock = {
            '_screen': {
            }
        }
        finalize_screen(screen_mock, screen_layout_mock)
        update_screen_status_patch.assert_called_once_with(screen_mock, 'finalize', screen_layout_mock['_screen'])
        screen_mock.getch.assert_called_with()
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
            },
            'category1': {
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

    @patch('mpcurses.screen.get_category_count', return_value='012')
    def test__get_category_values_Should_ReturnExpected_When_List(self, *patches):
        screen_layout = {
            'items': {
                'position': (6, 35),
                'list': True,
                'keep_count': True,
                'color': 1,
                'regex': r'^processing item "(?P<value>.*)"$'
            }
        }
        message = 'processing item "cambridge-limited"'
        result = get_category_values(message, 0, screen_layout)
        expected_result = [
            ('items', 'cambridge-limited'),
        ]
        self.assertEqual(result, expected_result)

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

    def test__get_position_Should_ReturnExpected_When_Semicolon(self, *patches):

        self.assertEqual(get_position('data: 0'), 5)

    def test__get_position_Should_ReturnExpected_When_NoSemicolon(self, *patches):

        self.assertEqual(get_position('string'), 7)

    def test__get_position_Should_ReturnExpected_When_InitText(self, *patches):

        self.assertEqual(get_position('---'), -1)

    def test__process_clear_Should_CallExpected_When_Clear(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'category': {
                'clear': True
            }
        }
        process_clear('category', 1, 1, screen_layout_mock, screen_mock)
        screen_mock.move.assert_called_once_with(1, 1)
        screen_mock.clrtoeol.assert_called_once_with()

    def test__process_clear_Should_CallExpected_When_NoClear(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'category': {
            }
        }
        process_clear('category', 1, 1, screen_layout_mock, screen_mock)
        screen_mock.clrtoeol.assert_not_called()

    def test__process_clear_Should_CallExpected_When_ClearHorizontalTablePadding(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'table': {
                'orientation': 'horizontal',
                'padding': 10
            },
            'category': {
                'clear': True,
                'table': True
            }
        }
        process_clear('category', 1, 1, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_called_once_with(1, 1, ' ' * 10)

    def test__process_clear_Should_CallExpected_When_ClearHorizontalTableCategoryPadding(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'table': {
                'orientation': 'horizontal',
                'padding': 10
            },
            'category': {
                'clear': True,
                'padding': 20,
                'table': True
            }
        }
        process_clear('category', 1, 1, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_called_once_with(1, 1, ' ' * 20)

    def test__process_clear_Should_CallExpected_When_ClearNonHorizontalTable(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'category': {
                'clear': True,
                'table': True
            }
        }
        process_clear('category', 1, 1, screen_layout_mock, screen_mock)
        screen_mock.move.assert_called_once_with(1, 1)
        screen_mock.clrtoeol.assert_called_once_with()

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_CategoryModulus(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'translated': {
                'color': 31
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
        process_counter(1, 'translated', 10, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_called_once_with(7, 4, '|', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(21)

    def test__process_counter_Should_CallExpected_When_CategoryModulusWithRemainder(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'translated': {
                'color': 31
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
                    '_count': 43,
                    '_modulus_count': 3
                },
            }
        }
        process_counter(1, 'translated', 10, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_not_called()

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_CategoryNoModulus(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'translated': {
                'color': 31
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
        process_counter(1, 'translated', 10, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_called_once_with(7, 44, '|', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(31)

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_Counter(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
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
                }
            }
        }
        process_counter(1, '_counter_', 100, screen_layout_mock, screen_mock)
        spaces = ' ' * 20  # 100/5
        screen_mock.addstr.assert_called_once_with(7, 0, '[{}]'.format(spaces), color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(45)

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_Width(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'translated': {
                'color': 31
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
        process_counter(0, 'translated', 10, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_called_once_with(6, 54, '|', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(31)
        self.assertEqual(screen_layout_mock['_counter_']['position'], (7, 10))

    @patch('mpcurses.screen.curses.color_pair')
    def test__process_counter_Should_CallExpected_When_WidthWithRemainder(self, color_pair_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            'translated': {
                'color': 31
            },
            '_counter_': {
                'position': (6, 10),
                'categories': [
                    'translated',
                ],
                'counter_text': '|',
                'width': 5,
                0: {
                    '_count': 43,
                },
            }
        }
        process_counter(0, 'translated', 10, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_called_once_with(6, 53, '|', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(31)
        self.assertEqual(screen_layout_mock['_counter_']['position'], (6, 10))
        self.assertEqual(screen_layout_mock['_counter_'][0]['_count'], 44)

    def test__process_counter_Should_CallExpected_When_NoCategoryNoCounter(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
        }
        process_counter(1, 'category1', 10, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_not_called()

    def test__process_counter_Should_CallExpected_When_CategoryNotInCounter(self, *patches):
        screen_mock = Mock()
        screen_layout_mock = {
            '_counter_': {
                'categories': [
                    'category2',
                ]
            }
        }
        process_counter(1, 'category1', 10, screen_layout_mock, screen_mock)
        screen_mock.addstr.assert_not_called()

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
    def test__get_category_x_pos_Should_ReturnExpected_When_NoTableText(self, get_position_patch, *patches):
        get_position_patch.return_value = 6
        screen_layout = {
            'start': {
                'position': (5, 12),
                'text': 'this is some text',
            }
        }
        result = get_category_x_pos('start', 0, screen_layout)
        expected_result = 19
        self.assertEqual(result, expected_result)

    def test__get_category_x_pos_Should_ReturnExpected_When_NoTableNoText(self, *patches):
        screen_layout = {
            'start': {
                'position': (5, 12),
            }
        }
        result = get_category_x_pos('start', 0, screen_layout)
        expected_result = 12
        self.assertEqual(result, expected_result)

    def test__get_category_x_pos_Should_ReturnExpected_When_WraparoundTableWrap(self, *patches):
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

    def test__get_category_x_pos_Should_ReturnExpected_When_WraparoundTableNoWrap(self, *patches):
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
        result = get_category_x_pos('start', 2, screen_layout)
        expected_result = 12
        self.assertEqual(result, expected_result)

    def test__get_category_x_pos_Should_ReturnExpected_When_HorizontalTable(self, *patches):
        screen_layout = {
            'table': {
                'orientation': 'horizontal',
                'padding': 10
            },
            'start': {
                'position': (5, 12),
                'table': True
            }
        }
        result = get_category_x_pos('start', 2, screen_layout)
        expected_result = 12 + (2 * 10)
        self.assertEqual(result, expected_result)

    def test__get_category_x_pos_Should_ReturnExpected_When_HorizontalTableCategoryPadding(self, *patches):
        screen_layout = {
            'table': {
                'orientation': 'horizontal',
                'padding': 10
            },
            'start': {
                'position': (5, 12),
                'padding': 20,
                'table': True
            }
        }
        result = get_category_x_pos('start', 2, screen_layout)
        expected_result = 12 + (2 * 20)
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

    def test__get_category_y_pos_Should_ReturnExpected_When_WraparoundTableWrap(self, *patches):
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

    def test__get_category_y_pos_Should_ReturnExpected_When_WraparoundTableNoWrap(self, *patches):
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
        result = get_category_y_pos('start', 2, screen_layout)
        expected_result = 7
        self.assertEqual(result, expected_result)

    def test__get_category_y_pos_Should_ReturnExpected_When_List(self, *patches):
        screen_layout = {
            'items': {
                'position': (6, 35),
                'list': True,
                'color': 1,
                'regex': r'^processing item "(?P<value>.*)"$',
                '_count': 12
            }
        }
        result = get_category_y_pos('items', 0, screen_layout)
        expected_result = 18
        self.assertEqual(result, expected_result)

    def test__get_category_y_pos_Should_ReturnExpected_When_HorizontalTable(self, *patches):
        screen_layout = {
            'table': {
                'orientation': 'horizontal'
            },
            'start': {
                'position': (5, 12),
                'table': True
            }
        }
        result = get_category_y_pos('start', 2, screen_layout)
        expected_result = 5
        self.assertEqual(result, expected_result)

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
        screen_mock = Mock()
        screen_layout_mock = {
            'start': {
                'position': (5, 57),
                'text': '',
                'replace_text': '*',
                'color': 0,
                'table': True
            }
        }
        message = '#5-processing bay 5 at: 01/30/18 13:24'
        update_screen(message, screen_mock, screen_layout_mock)
        screen_mock.addstr.assert_called_with(10, 57, '*', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(0)

    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.get_category_values')
    @patch('mpcurses.screen.sanitize_message')
    def test__update_screen_Should_CallExpected_When_Effects(self, sanitize_message_patch, get_category_values_patch, color_pair_patch, *patches):
        sanitize_message_patch.return_value = (5, 'firmware is: 2.64.1')
        get_category_values_patch.return_value = [
            ['firmware', '2.64.1'],
        ]
        screen_mock = Mock()
        screen_layout_mock = {
            'firmware': {
                'position': (3, 34),
                'color': 1,
                'effects': [
                    {
                        'regex': '.*2.64.*$',
                        'color': 3
                    }
                ],
                'table': True
            }
        }
        message = '#5-firmware is: 2.64.1'
        update_screen(message, screen_mock, screen_layout_mock)
        screen_mock.addstr.assert_called_with(8, 34, '2.64.1', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(3)

    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.get_category_values')
    @patch('mpcurses.screen.sanitize_message')
    def test__update_screen_Should_CallExpected_When_Clear(self, sanitize_message_patch, get_category_values_patch, color_pair_patch, *patches):
        sanitize_message_patch.return_value = (4, 'checking 121372')
        get_category_values_patch.return_value = [
            ['number', '121372'],
        ]
        screen_mock = Mock()
        screen_layout_mock = {
            'number': {
                'table': True,
                'position': (1, 0),
                'clear': True
            }
        }
        message = '#4-checking 121372'
        update_screen(message, screen_mock, screen_layout_mock)
        screen_mock.move.assert_called_once_with(5, 0)
        screen_mock.clrtoeol.assert_called_once_with()

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
        screen_mock = Mock()
        screen_layout_mock = {
            'translated': {
                'position': (3, 0),
                'text': 'Networks Translated: 0',
                'color': 241,
                'keep_count': True,
                'table': True,
                3: {
                    '_count': 32
                }
            },
            '_counter_': {
            }
        }
        message = '#3-network powerdac1234 was translated'
        screen_mock = Mock()
        update_screen(message, screen_mock, screen_layout_mock)
        screen_mock.addstr.assert_called_with(6, 21, '033', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(241)
        process_counter_patch.assert_called_once_with(3, 'translated', '033', screen_layout_mock, screen_mock)

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
        screen_mock = Mock()
        screen_layout_mock = {
            'translated': {
                'position': (3, 0),
                'text': 'Networks Translated: 0',
                'color': 241,
                'keep_count': True,
                '_count': 32
            },
            '_counter_': {
            }
        }
        message = '#3-network powerdac1234 was translated'
        update_screen(message, screen_mock, screen_layout_mock)
        screen_mock.addstr.assert_called_with(3, 21, '033', color_pair_patch.return_value)
        color_pair_patch.assert_called_once_with(241)
        process_counter_patch.assert_called_once_with(3, 'translated', '033', screen_layout_mock, screen_mock)

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

    @patch('mpcurses.screen.update_screen')
    def test__echo_to_screen_Should_CallExpected_When_Offset(self, update_screen_patch, *patches):
        screen_mock = Mock()
        screen_layout_mock = Mock()
        data = {
            'key1': True
        }
        echo_to_screen(screen_mock, data, screen_layout_mock, offset='1')
        self.assertTrue(call("#1-'key1' is 'True'", screen_mock, screen_layout_mock) in update_screen_patch.mock_calls)

    def test__refresh_screen_Should_CallScreenRefresh_When_Screen(self, *patches):
        screen_mock = Mock()
        refresh_screen(screen_mock)
        screen_mock.refresh.assert_called_once_with()

    def test__get_table_position_Should_ReturnExpected_When_Called(self, *patches):
        screen_layout = {
            'category1': {
                'position': (2, 2)
            },
            'category2': {
                'position': (2, 10)
            },
            'category3': {
                'position': (3, 3),
                'table': True
            },
            'category4': {
                'position': (21, 14)
            }
        }
        result = get_table_position(screen_layout)
        expected_result = (3, 3)
        self.assertEqual(result, expected_result)

    def test__get_table_position_Should_ReturnExpected_When_NoTable(self, *patches):
        screen_layout = {
            'category1': {
                'position': (2, 2)
            },
            'category2': {
                'position': (2, 10)
            },
            'category3': {
                'position': (3, 3)
            },
            'category4': {
                'position': (21, 14)
            }
        }
        result = get_table_position(screen_layout)
        self.assertIsNone(result)

    def test__get_positions_to_update_Should_ReturnExpected_When_Called(self, *patches):
        screen_layout = {
            'category1': {
                'position': (2, 2)
            },
            'category2': {
                'position': (2, 10)
            },
            'category3': {
                'position': (3, 3),
                'table': True
            },
            'category4': {
                'position': (21, 14)
            },
            'category5': {
                'position': (22, 8)
            }
        }
        result = get_positions_to_update(screen_layout, 3, 10)
        expected_result = {
            'category4': (11, 14),
            'category5': (12, 8)
        }
        self.assertEqual(result, expected_result)

    def test__update_positions_Should_DoExpected_When_Called(self, *patches):
        screen_layout = {
            'category1': {
                'position': (2, 2)
            },
            'category2': {
                'position': (2, 10)
            },
            'category3': {
                'position': (3, 3),
                'table': True
            },
            'category4': {
                'position': (21, 14)
            },
            'category5': {
                'position': (22, 8)
            }
        }
        positions = {
            'category4': (11, 14),
            'category5': (12, 8)
        }
        update_positions(screen_layout, positions)
        self.assertEqual(screen_layout['category4']['position'], positions['category4'])
        self.assertEqual(screen_layout['category5']['position'], positions['category5'])

    @patch('mpcurses.screen.get_table_position', return_value=(3, 3))
    @patch('mpcurses.screen.get_positions_to_update')
    @patch('mpcurses.screen.update_positions')
    def test__squash_table_Should_CallExpected_When_Called(self, update_positions_patch, get_positions_to_update_patch, *patches):
        screen_layout = {}
        squash_table(screen_layout, 10)
        update_positions_patch.assert_called_once_with(screen_layout, get_positions_to_update_patch.return_value)

    @patch('mpcurses.screen.sys.argv', ['scripta'])
    def test__set_screen_defaults_Should_SetDefaults_When_Called(self, *patches):
        screen_layout = {}
        set_screen_defaults(screen_layout)
        expected_screen_layout = {
            '_screen': {
                'title': 'scripta',
                'color': 11,
                'blink': True
            }
        }
        self.assertEqual(screen_layout, expected_screen_layout)

    def test__set_screen_defaults_Should_NotSetDefaults_When_Called(self, *patches):
        screen_layout = {
            '_screen': {
                'title': 'scriptb',
                'color': 12,
                'blink': False
            }
        }
        set_screen_defaults(screen_layout)
        expected_screen_layout = {
            '_screen': {
                'title': 'scriptb',
                'color': 12,
                'blink': False
            }
        }
        self.assertEqual(screen_layout, expected_screen_layout)

    def test__set_screen_defaults_processes_Should_SetDefaults_When_Called(self, *patches):
        screen_layout = {
            '_screen': {
            }
        }
        set_screen_defaults_processes(10, 2, screen_layout)
        expected_screen_layout = {
            '_screen': {
                'zfill': 2,
                'show_process_status': True
            }
        }
        self.assertEqual(screen_layout, expected_screen_layout)

    def test__set_screen_defaults_processes_Should_NotSetDefaults_When_Called(self, *patches):
        screen_layout = {
            '_screen': {
                'zfill': 2,
                'show_process_status': False
            }
        }
        set_screen_defaults_processes(10, 2, screen_layout)
        expected_screen_layout = {
            '_screen': {
                'zfill': 2,
                'show_process_status': False
            }
        }
        self.assertEqual(screen_layout, expected_screen_layout)

    def test__validate_screen_layout_processes_RaiseException_When_MoreProcessesThanTableEntries(self, *patches):
        screen_layout_mock = {
            'table': {
                'rows': 30,
                'cols': 2
            }
        }
        with self.assertRaises(Exception):
            validate_screen_layout_processes(100, screen_layout_mock)

    @patch('mpcurses.screen.squash_table')
    def test__validate_screen_layout_processes_Should_CallExpected_When_Squash(self, squash_table_patch, *patches):
        screen_layout_mock = {
            'table': {
                'rows': 30,
                'cols': 2,
                'squash': True
            }
        }
        validate_screen_layout_processes(11, screen_layout_mock)
        squash_table_patch.assert_called_once_with(screen_layout_mock, 19)

    @patch('mpcurses.screen.squash_table')
    def test__validate_screen_layout_processes_Should_CallExpected_When_SquashFalse(self, squash_table_patch, *patches):
        screen_layout_mock = {
            'table': {
                'rows': 30,
                'cols': 2,
                'squash': False
            }
        }
        validate_screen_layout_processes(11, screen_layout_mock)
        squash_table_patch.assert_not_called()

    @patch('mpcurses.screen.squash_table')
    def test__validate_screen_layout_processes_Should_CallExpected_When_ProcessesGreaterThanRows(self, squash_table_patch, *patches):
        screen_layout_mock = {
            'table': {
                'rows': 30,
                'cols': 2,
                'squash': True
            }
        }
        validate_screen_layout_processes(30, screen_layout_mock)
        squash_table_patch.assert_not_called()

    @patch('mpcurses.screen.squash_table')
    def test__validate_screen_layout_processes_Should_CallExpected_When_NoTable(self, squash_table_patch, *patches):
        screen_layout_mock = {
        }
        validate_screen_layout_processes(30, screen_layout_mock)
        squash_table_patch.assert_not_called()

    @patch('mpcurses.screen.squash_table')
    def test__validate_screen_layout_processes_Should_CallExpected_When_HorizontalTable(self, squash_table_patch, *patches):
        screen_layout_mock = {
            'table': {
                'orientation': 'horizontal'
            }
        }
        validate_screen_layout_processes(30, screen_layout_mock)

    def test__validate_screen_size_Should_RaiseExeption_When_ScreenNotTallEnough(self, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (10, 10)
        screen_layout_mock = {
            'category1': {
                'position': (5, 5)
            },
            'category2': {
                'position': (15, 5)
            },
            'category3': {
            }
        }
        with self.assertRaises(Exception):
            validate_screen_size(screen_mock, screen_layout_mock)

    def test__validate_screen_size_Should_RaiseExeption_When_ScreenNotWideEnough(self, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (10, 10)
        screen_layout_mock = {
            'category1': {
                'position': (5, 5)
            },
            'category2': {
                'position': (6, 15)
            },
            'category3': {
            }
        }
        with self.assertRaises(Exception):
            validate_screen_size(screen_mock, screen_layout_mock)

    def test__validate_screen_size_Should_NotRaiseExeption_When_Called(self, *patches):
        screen_mock = Mock()
        screen_mock.getmaxyx.return_value = (0, 0)
        screen_layout_mock = {
            'category1': {
                'position': (0, 0)
            }
        }
        validate_screen_size(screen_mock, screen_layout_mock)

    @patch('mpcurses.screen.sleep')
    def test__blink_Should_CallExpected_When_Called(self, *patches):
        queue_mock = Mock()
        blink(queue_mock, terminate=True)
        queue_mock.put.assert_called_with('blink-on')

    @patch('mpcurses.screen.sleep')
    @patch('mpcurses.screen.itertools')
    def test__blink_Should_CallExpected_When_ForBranchCoverage(self, itertools_patch, *patches):
        itertools_patch.cycle.return_value = iter(['blink-on', 'blink-off'])
        queue_mock = Mock()
        with self.assertRaises(StopIteration):
            blink(queue_mock)
