
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
from .mpcurses import MPcurses

logger = logging.getLogger(__name__)


def execute(function=None, process_data=None, shared_data=None, number_of_processes=None, init_messages=None, screen_layout=None):
    """ public execute api - spawns child processes as dictated by process data and manages displaying spawned process messages to screen if screen layout is defined

        wrapped with KeyboardInterrupt exception to enable user to submit Ctrl+C interrupt to kill all running processes
        supports 'silent mode' if caller does not specify a screen layout

        Parameters:
            function (callable): callable object that each spawned process will execute as their target
            process_data (list): list of dict where each dict contains meta-data specific to a process
                [{}, {}, {}]
            shared_data (dict): data to provide all spawned processes
            number_of_processes (int): number of processes to spawn
            init_messages (list): list of messages to send screen upon startup
            screen_layout (dict): dictionary containing meta-data for how logged messages for each spawned process should be displayed on screen
        Returns:
            -

        THIS METHOD WILL BE DEPCRATED - use MPcurses class instead as dictated below
    """
    mpcurses = MPcurses(
        function=function,
        process_data=process_data,
        shared_data=shared_data,
        processes_to_start=number_of_processes,
        init_messages=init_messages,
        screen_layout=screen_layout)
    mpcurses.execute()
