
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

from mpcurses.process import execute

import logging
logger = logging.getLogger(__name__)


class TestProcess(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('mpcurses.process.MPcurses')
    def test__execute_Should_CallExpected_When_Called(self, mpcurses_patch, *patches):
        function_mock = Mock()
        process_data = [{'range': '0-1'}]
        execute(function=function_mock, process_data=process_data)
        mpcurses_patch.assert_called_once_with(
            function=function_mock,
            process_data=process_data,
            shared_data=None,
            processes_to_start=None,
            init_messages=None,
            screen_layout=None)
