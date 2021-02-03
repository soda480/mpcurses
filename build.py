
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

"""
Mpcurses is an abstraction of the Python curses and multiprocessing libraries providing function execution and runtime visualization capabilities at scale. It contains a simple API to enable any Python function to be executed across one or more background processes and includes built-in directives to visualize the functions execution on a terminal screen. 
The mpcurses API allows for seamless integration since it does not require the target function to include additional context about curses or multiprocessing. The target function does need to implement logging since log messages are the primary means of inter-process communication between the background processes executing the function and the main process updating the curses screen on the terminal.
For examples checkout our home page: https://github.com/soda480/mpcurses
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
version = '0.2.0'
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
