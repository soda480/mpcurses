
# Copyright (c) 2020 Emilio Reyes (soda480@gmail.com)

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
from mpcurses.screen import initialize_screen
from mpcurses.screen import finalize_screen
from mpcurses.screen import get_category_values
from mpcurses.screen import sanitize_message
from mpcurses.screen import update_screen
from mpcurses.screen import blink_running
from mpcurses.screen import echo_to_screen
from mpcurses.screen import refresh_screen
from mpcurses.screen import get_position


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

        init_pair_call_1 = call(1, 0, -1)
        init_pair_call_2 = call(2, 1, -1)
        self.assertEqual(curses_mock.init_pair.mock_calls[0], init_pair_call_1)
        self.assertEqual(curses_mock.init_pair.mock_calls[1], init_pair_call_2)

    @patch('mpcurses.screen.initialize_colors')
    @patch('mpcurses.screen.curses.curs_set')
    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.curses.newwin')
    def test__initialize_screen_ShouldDoExpected_When_ScreenLayoutText(self, newwin_patch, color_pair, *patches):
        window_mock = Mock()
        newwin_patch.return_value = window_mock

        color_pair_mock = Mock()
        color_pair.return_value = color_pair_mock
        screen_mock = Mock()
        screen_layout = {
            'default': {
                'window': True,
                'begin_y': 0,
                'begin_x': 0,
                'height': 20,
                'width': 300
            },
            'log_file': {
                'text': 'LOGFILE:',
                'text_color': 1,
                'color': 1,
                'position': (1, 0)
            }
        }
        initialize_screen(screen_mock, screen_layout)

        window_mock.addstr.assert_called_with(1, 0, 'LOGFILE:', color_pair_mock)
        window_mock.refresh.assert_called_with()

    @patch('mpcurses.screen.initialize_colors')
    @patch('mpcurses.screen.curses.curs_set')
    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.curses.newwin')
    def test__initialize_screen_ShouldDoExpected_When_ScreenLayoutNumber(self, newwin_patch, *patches):
        window_mock = Mock()
        newwin_patch.return_value = window_mock

        screen_mock = Mock()
        screen_layout = {
            'default': {
                'window': True,
                'begin_y': 0,
                'begin_x': 0,
                'height': 20,
                'width': 300
            },
            'extracted': {
                'text': 'Networks Extracted:',
                'text_color': 1,
                'color': 4,
                'position': (4, 0),
                'number': True
            }
        }
        initialize_screen(screen_mock, screen_layout)

        window_mock.addstr.assert_called_with(4, 20, '0')
        window_mock.refresh.assert_called_with()

    @patch('mpcurses.screen.initialize_colors')
    @patch('mpcurses.screen.curses.curs_set')
    @patch('mpcurses.screen.curses.color_pair')
    @patch('mpcurses.screen.curses.newwin')
    def test__initialize_screen_ShouldSetWindow_When_WindowIdNotDefault(self, newwin_patch, *patches):
        window_mock = Mock()
        newwin_patch.return_value = window_mock
        screen_layout = {
            'window_legend': {
                'window': True,
                'begin_y': 20,
                'begin_x': 0,
                'height': 3,
                'width': 300
            },
            'extracted': {
                'text': 'Networks Extracted:',
                'text_color': 1,
                'color': 4,
                'position': (4, 0),
                'number': True,
                'window_id': 'window_legend'
            }
        }
        screen_mock = Mock()
        initialize_screen(screen_mock, screen_layout)

        self.assertEqual(screen_layout['extracted']['_window'], window_mock)

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

    @unittest.skip('skip - intermittent error')
    def test__get_category_values_Should_ReturnExpected_When_MessageLessThanAllowedCharacters(self, *patches):
        screen_layout = {
            'firmware': {
                'text': '',
                'color': 0,
                'position': (5, 47),
                'regex': '^.* firmware version for bay \\d+ is "(?P<value>.*)"$'
            },
            'start': {
                'text': '',
                'color': 0,
                'position': (5, 57),
                'regex': '^processing bay \\d+ at: (?P<value>.*)$'
            },
            'message': {
                'text': '',
                'color': 0,
                'position': (5, 67),
                'clear': True,
                'regex': '^(?P<value>.*)$',
                'effects': [
                    {
                        'regex': '.* was successfull.*',
                        'color': 3
                    }, {
                        'regex': '.* failed.*',
                        'color': 2
                    }, {
                        'regex': 'ERROR:.*',
                        'color': 2
                    }, {
                        'regex': '.*already present.*',
                        'color': 16
                    }
                ]
            },
            'start_new_bay': {
                'iterator': True,
                'position': (5, 0),
                'insert_lines': 3,
                'regex': '^processing next bay$'
            }
        }

        message = 'processing bay 1 at: 01/30/18 13:24'
        result = get_category_values(message, screen_layout)
        expected_result = [
            ('start', '01/30/18 13:24'),
            ('message', 'processing bay 1 at: 01/30/18 13:24'),
        ]
        self.assertEqual(result, expected_result)

    def test__get_category_values_Should_ReturnReducedValue_When_MessageGreaterThanAllowedCharacters(self, *patches):
        screen_layout = {
            'firmware': {
                'text': '',
                'color': 0,
                'position': (5, 47),
                'regex': '^.* firmware version for bay \\d+ is "(?P<value>.*)"$'
            },
            'start': {
                'text': '',
                'color': 0,
                'position': (5, 57),
                'regex': '^processing bay \\d+ at: (?P<value>.*)$'
            },
            'message': {
                'text': '',
                'color': 0,
                'position': (5, 67),
                'clear': True,
                'regex': '^(?P<value>.*)$',
                'effects': [
                    {
                        'regex': '.* was successfull.*',
                        'color': 3
                    }, {
                        'regex': '.* failed.*',
                        'color': 2
                    }, {
                        'regex': 'ERROR:.*',
                        'color': 2
                    }, {
                        'regex': '.*already present.*',
                        'color': 16
                    }
                ]
            },
            'start_new_bay': {
                'iterator': True,
                'position': (5, 0),
                'insert_lines': 3,
                'regex': '^processing next bay$'
            }
        }

        message = 'eramos todos de papel, liso y blanco, sin dolor, y fuimos hechos para andar, de par en par, sin reclamar, hare tiempo me dijeron que aqui no pasa nada'
        result = get_category_values(message, screen_layout)
        expected_result = [
            ('message', 'eramos todos de papel, liso y blanco, sin dolor, y fuimos hechos para andar, de par en par, sin recl...'),
        ]
        self.assertEqual(result, expected_result)

    @patch('mpcurses.screen.curses')
    @patch('mpcurses.screen.get_category_values')
    def test__update_screen_Should_Return_When_GetCategoryValuesReturnsEmptyList(self, get_category_values_patch, *patches):
        screen_layout = {
            'firmware': {
                'text': '',
                'color': 0,
                'position': (5, 47),
                'regex': '^.* firmware version for bay \\d+ is "(?P<value>.*)"$'
            },
            'start': {
                'text': '',
                'color': 0,
                'position': (5, 57),
                'regex': '^processing bay \\d+ at: (?P<value>.*)$'
            },
            'message': {
                'text': '',
                'color': 0,
                'position': (5, 67),
                'clear': True,
                'regex': '^(?P<value>.*)$',
                'effects': [
                    {
                        'regex': '.* was successfull.*',
                        'color': 3
                    }, {
                        'regex': '.* failed.*',
                        'color': 2
                    }, {
                        'regex': 'ERROR:.*',
                        'color': 2
                    }, {
                        'regex': '.*already present.*',
                        'color': 16
                    }
                ]
            },
            'start_new_bay': {
                'iterator': True,
                'position': (5, 0),
                'insert_lines': 3,
                'regex': '^processing next bay$'
            }
        }
        get_category_values_patch.return_value = [
        ]
        message = 'processing bay 1 at: 01/30/18 13:24'
        screen_mock = Mock()

        update_screen(message, screen_mock, screen_layout)

        self.assertEqual(len(screen_mock.refresh.mock_calls), 0)

    @patch('mpcurses.screen.curses')
    @patch('mpcurses.screen.get_category_values')
    def test__update_screen_Should_CallExpected_When_Called(self, get_category_values_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            'firmware': {
                'text': '',
                'color': 0,
                'position': (5, 47),
                'regex': '^.* firmware version for bay \\d+ is "(?P<value>.*)"$',
                '_window': window_mock
            },
            'start': {
                'text': '',
                'color': 0,
                'position': (5, 57),
                'regex': '^processing bay \\d+ at: (?P<value>.*)$',
                '_window': window_mock
            },
            'message': {
                'text': '',
                'color': 0,
                'position': (5, 67),
                'clear': True,
                'regex': '^(?P<value>.*)$',
                '_window': window_mock,
                'effects': [
                    {
                        'regex': '.* was successfull.*',
                        'color': 3
                    }, {
                        'regex': '.* failed.*',
                        'color': 2
                    }, {
                        'regex': 'ERROR:.*',
                        'color': 2
                    }, {
                        'regex': '.*already present.*',
                        'color': 16
                    }
                ]
            },
            'start_new_bay': {
                'iterator': True,
                'position': (5, 0),
                'insert_lines': 3,
                'regex': '^processing next bay$',
                '_window': window_mock
            }
        }
        get_category_values_patch.return_value = [
            ('start', '01/30/18 13:24'),
            ('message', 'processing bay 1 at: 01/30/18 13:24'),
        ]
        message = 'processing bay 1 at: 01/30/18 13:24'
        screen_mock = Mock()

        update_screen(message, screen_mock, screen_layout)

        self.assertEqual(len(window_mock.refresh.mock_calls), 2)

    @patch('mpcurses.screen.curses')
    @patch('mpcurses.screen.get_category_values')
    def test__update_screen_Should_CallExpected_When_ReplaceText(self, get_category_values_patch, curses_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            'start': {
                'text': '',
                'replace_text': '*',
                'color': 0,
                'position': (5, 57),
                'regex': '^processing bay \\d+ at: (?P<value>.*)$',
                '_window': window_mock
            }
        }
        get_category_values_patch.return_value = [
            ('start', 'processing bay 1 at: 01/30/18 13:24'),
        ]
        message = 'processing bay 1 at: 01/30/18 13:24'
        screen_mock = Mock()
        update_screen(message, screen_mock, screen_layout)

        window_mock.addstr.assert_called_with(5, 57, '*', curses_patch.color_pair(0))

    @patch('mpcurses.screen.curses')
    @patch('mpcurses.screen.get_category_values')
    def test__update_screen_Should_CallExpected_When_KeepCount(self, get_category_values_patch, curses_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            'things': {
                'text': 'Things',
                'color': 0,
                'text_color': 2,
                'position': (4, 0),
                'keep_count': True,
                'count': 20,
                '_window': window_mock
            },
            'firmware': {
                'text': '',
                'color': 0,
                'position': (5, 47),
                'regex': '^.* firmware version for bay \\d+ is "(?P<value>.*)"$',
                '_window': window_mock
            },
            'start': {
                'text': '',
                'color': 0,
                'position': (5, 57),
                'regex': '^processing bay \\d+ at: (?P<value>.*)$',
                '_window': window_mock
            },
            'message': {
                'text': '',
                'color': 0,
                'position': (5, 67),
                'clear': True,
                'regex': '^(?P<value>.*)$',
                '_window': window_mock,
                'effects': [
                    {
                        'regex': '.* was successfull.*',
                        'color': 3
                    }, {
                        'regex': '.* failed.*',
                        'color': 2
                    }, {
                        'regex': 'ERROR:.*',
                        'color': 2
                    }, {
                        'regex': '.*already present.*',
                        'color': 16
                    }
                ]
            },
            'start_new_bay': {
                'iterator': True,
                'position': (5, 0),
                'insert_lines': 3,
                'regex': '^processing next bay$',
                '_window': window_mock
            }
        }
        get_category_values_patch.return_value = [
            ('things', 'Thing 21'),
        ]
        message = 'message'
        screen_mock = Mock()

        update_screen(message, screen_mock, screen_layout)

        window_mock.addstr.assert_called_with(4, 8, '21', curses_patch.color_pair(0))
        self.assertEqual(len(window_mock.refresh.mock_calls), 1)

    @patch('mpcurses.screen.curses')
    @patch('mpcurses.screen.get_category_values')
    def test__update_screen_Should_CallExpected_When_EffectsMatch(self, get_category_values_patch, curses_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            'things': {
                'text': 'Things',
                'color': 0,
                'text_color': 2,
                'position': (4, 0),
                'keep_count': True,
                'count': 20,
                '_window': window_mock
            },
            'firmware': {
                'text': '',
                'color': 0,
                'position': (5, 47),
                'regex': '^.* firmware version for bay \\d+ is "(?P<value>.*)"$',
                '_window': window_mock
            },
            'start': {
                'text': '',
                'color': 0,
                'position': (5, 57),
                'regex': '^processing bay \\d+ at: (?P<value>.*)$',
                '_window': window_mock
            },
            'message': {
                'text': '',
                'color': 0,
                'position': (5, 67),
                'clear': True,
                'regex': '^(?P<value>.*)$',
                '_window': window_mock,
                'effects': [
                    {
                        'regex': '.* was successfull.*',
                        'color': 3
                    }, {
                        'regex': '.* failed.*',
                        'color': 2
                    }, {
                        'regex': 'ERROR:.*',
                        'color': 2
                    }, {
                        'regex': '.*already present.*',
                        'color': 16
                    }
                ]
            },
            'start_new_bay': {
                'iterator': True,
                'position': (5, 0),
                'insert_lines': 3,
                'regex': '^processing next bay$',
                '_window': window_mock
            }
        }
        get_category_values_patch.return_value = [
            ('message', 'ERROR: it crashed'),
        ]
        message = 'ERROR: it crashed'
        screen_mock = Mock()

        update_screen(message, screen_mock, screen_layout)

        window_mock.addstr.assert_called_with(5, 67, 'ERROR: it crashed', curses_patch.color_pair(2))
        self.assertEqual(len(window_mock.refresh.mock_calls), 1)

    @patch('mpcurses.screen.curses')
    @patch('mpcurses.screen.get_category_values')
    def test__update_screen_Should_CallExpected_When_Counter(self, get_category_values_patch, curses_patch, *patches):
        window_mock = Mock()
        screen_layout = {
            'translated': {
                'position': (6, 0),
                'color': 10,
                '_window': window_mock
            },
            'counter': {
                'categories': ['translated', 'blacklisted', 'not_translated'],
                'text': '.',
                'position': (6, 0),
                'counter': True,
                'ticker': 30,
                '_window': window_mock
            }
        }
        get_category_values_patch.return_value = [
            ('translated', 'something was translated'),
        ]
        message = 'something was translated'
        screen_mock = Mock()

        update_screen(message, screen_mock, screen_layout)

        window_mock.addstr.assert_called_with(6, 30, '.', curses_patch.color_pair(10))
        self.assertEqual(len(window_mock.refresh.mock_calls), 1)

    @patch('mpcurses.screen.curses')
    @patch('mpcurses.screen.sanitize_message')
    @patch('mpcurses.screen.get_category_values')
    def test__update_screen_Should_CallExpected_When_Table(self, get_category_values_patch, sanitize_message_patch, curses_patch, *patches):
        sanitize_message_patch.return_value = (6, 'servername for bay 1 is server1.amr.corp.intel.com')
        window_mock = Mock()
        screen_layout = {
            'server': {
                'text': '',
                'color': 0,
                'position': (4, 7),
                'regex': '^servername for bay \\d+ is "(?P<value>.*)"$',
                'table': True,
                '_window': window_mock
            }
        }
        get_category_values_patch.return_value = [
            ('server', 'server1.amr.corp.intel.com'),
        ]
        message = '#6-servername for bay 1 is server1.amr.corp.intel.com'
        screen_mock = Mock()

        update_screen(message, screen_mock, screen_layout)

        self.assertEqual(window_mock.addstr.mock_calls[0], call(10, 7, 'server1.amr.corp.intel.com', curses_patch.color_pair(0)))

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
