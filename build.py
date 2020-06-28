
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

"""
mpcurses is a framework that exposes a simple set of APIs enabling multi-process integration with the curses screen painting library.

With mpcurses, the complexities of setting up multi-processing within a curses environment are abstracted into a few simple APIs and constructs. The main features:

* Execute a method across one or more concurrent processes
* Queue method execution to ensure only a predefined number of processes are running
* Define `curses` screen layout using a Python dict
* Leverage built-in directives for updating screen dynamically
  * Keep numeric counts
  * Update text values
  * Update text colors
  * Maintain visual indicators
  * Update progress bars
  * Display table of data coming from concurrent proceses

**How it works**

The method you wish to execute concurrently is decorated with the queue handler decorator. The queue handler decorator creates a new log handler that will write all logged messages within the decorated method to a thread-safe queue. The main process creates the thread-safe message queue and handles the spawning of the desired number of concurrent processes, each process will be passed the reference to the message queue upon startup. As the process executes it will send all log messages to the message queue. The main process will then read messages from the message queue as they come in and update the curses screen accordingly.

The layout of the curses screen is defined as a dictionary and can leverage builtin constructs for capturing messages, incrementing counters, and processing side effects such as changing text colors when certain messages appear. The result is a screen that is being updated dynamically from one or more concurrent processes running in the background.

For samples checkout our home page: https://github.com/soda480/mpcurses
"""

from pybuilder.core import use_plugin
from pybuilder.core import init
from pybuilder.core import Author
from pybuilder.core import task
from pybuilder.pluginhelper.external_command import ExternalCommandBuilder

use_plugin('python.core')
use_plugin('python.unittest')
use_plugin('python.install_dependencies')
use_plugin('python.flake8')
use_plugin('python.coverage')
use_plugin('python.distutils')

name = 'mpcurses'
authors = [
    Author('Emilio Reyes', 'emilio.reyes@intel.com')
]
summary = 'A framework that exposes a simple set of APIs enabling multi-process integration with the curses screen painting library'
url = 'https://github.com/soda480/mpcurses'
version = '0.0.10'
default_task = [
    'clean',
    'analyze',
    'cyclomatic_complexity',
    'package'
]
license = 'Apache License, Version 2.0'
description = __doc__


@init
def set_properties(project):
    project.set_property('unittest_module_glob', 'test_*.py')
    project.set_property('coverage_break_build', False)
    project.set_property('flake8_max_line_length', 120)
    project.set_property('flake8_verbose_output', True)
    project.set_property('flake8_break_build', True)
    project.set_property('flake8_include_scripts', True)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_ignore', 'E501, F401, F403, E114, E116')
    project.build_depends_on_requirements('requirements-build.txt')
    project.depends_on_requirements('requirements.txt')
    project.set_property('distutils_classifiers', [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration'
    ])


@task('cyclomatic_complexity', description='calculates and publishes cyclomatic complexity')
def cyclomatic_complexity(project, logger):
    try:
        command = ExternalCommandBuilder('radon', project)
        command.use_argument('cc')
        command.use_argument('-a')
        result = command.run_on_production_source_files(logger)
        if len(result.error_report_lines) > 0:
            logger.error('Errors while running radon, see {0}'.format(result.error_report_file))
        for line in result.report_lines[:-1]:
            logger.debug(line.strip())
        if not result.report_lines:
            return
        average_complexity_line = result.report_lines[-1].strip()
        logger.info(average_complexity_line)

    except Exception as exception:
        print('Unable to execute cyclomatic complexity due to ERROR: {}'.format(str(exception)))
