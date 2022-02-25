# mpcurses #
[![GitHub Workflow Status](https://github.com/soda480/mpcurses/workflows/build/badge.svg)](https://github.com/soda480/mpcurses/actions)
[![Code Coverage](https://codecov.io/gh/soda480/mpcurses/branch/master/graph/badge.svg)](https://codecov.io/gh/soda480/mpcurses)
[![Code Grade](https://api.codiga.io/project/12270/status/svg)](https://app.codiga.io/public/project/12270/mpcurses/dashboard)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/mpcurses.svg)](https://badge.fury.io/py/mpcurses)
[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)

Mpcurses is an abstraction of the Python curses and multiprocessing libraries providing function execution and runtime visualization capabilities at scale. It contains a simple API to enable any Python function to be executed across one or more background processes and includes built-in directives to visualize the functions execution on a terminal screen. 

The mpcurses API allows for seamless integration since it does not require the target function to include additional context about curses or multiprocessing. The target function does need to implement logging since log messages are the primary means of inter-process communication between the background processes executing the function and the main process updating the curses screen on the terminal.

The main features are:

* Execute a function across one or more concurrent processes
* Queue execution to ensure a predefined number of processes are running
* Visualize function execution on the terminal screen using curses
* Define the screen layout using a Python dict
* Leverage built-in directives to dynamically update the screen when events occur by analyzing log messages
  * Keep numeric counts
  * Update text values and colors
  * Maintain visual indicators
  * Display progress bars
  * Display tables
  * Display lists

 Refer to documentation here: https://soda480.github.io/mpcurses/

 Mpcurses is a subclass of `mpmq`, see [mpmq](https://pypi.org/project/mpmq/) for more information.

### Installation ###
```bash
pip install mpcurses
```

### Examples ###

To run the samples below you need to install the namegenerator module `pip install namegenerator`


A simple example using mpcurses:

```python
from mpcurses import MPcurses
import namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_something(*args):
    for _ in range(0, 600):
        logger.debug(f'processing item "{namegenerator.gen()}"')
        time.sleep(.01)

MPcurses(
    function=do_something,
    screen_layout={
        'display_item': {
            'position': (1, 1),
            'text': 'Processing:',
            'text_color': 0,
            'color': 14,
            'clear': True,
            'regex': r'^processing item "(?P<value>.*)"$'
        }
    }).execute()
 ```

Executing the code above results in the following:
![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example.gif)

To scale execution of the function across multiple processes; we set the `process_data` parameter to a list whose total number of elements represent the number of processes to execute, and each list element represent the data to be passed to each respective process:

```python
from mpcurses import MPcurses
import namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_something(*args):
    group = args[0].get('group', 0)
    for _ in range(0, 600):
        logger.debug(f'processing item "[{group}]: {namegenerator.gen()}"')
        time.sleep(.01)

MPcurses(
    function=do_something,
    process_data=[{'group': 1}, {'group': 2}, {'group': 3}],
    screen_layout={
        'display_item': {
            'position': (1, 1),
            'color': 14,
            'clear': True,
            'regex': r'^processing item "(?P<value>.*)"$',
            'table': True
        }
    }).execute()
```

Executing the code above results in the following:
![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example-multi.gif)

Serveral [examples](https://github.com/soda480/mpcurses/tree/master/examples) are included to help introduce the mpcurses library. Note the functions contained in all the examples are Python functions that have no context about multiprocessing or curses, they simply perform a function on a given dataset. Mpcurses takes care of setting up the multiprocessing, configuring the curses screen and maintaining the thread-safe queues that are required for inter-process communication.

#### [example1](https://github.com/soda480/mpcurses/blob/master/examples/example1.py)
Execute a function that processes a list of random items. The screen maintains indicators showing the number of items that have been processed. Two lists are maintained displaying the items that had errors and warnings.
![example1](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example1.gif)

#### [example2](https://github.com/soda480/mpcurses/blob/master/examples/example2.py)
Execute a function that processes a list of random items. Execution is scaled across three processes where each is responsible for processing items for a particular group. The screen maintains indicators displaying the items that had errors and warnings for each group.
![example2](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example2.gif)

#### [example3](https://github.com/soda480/mpcurses/blob/master/examples/example3.py)
Execute a function that calculates prime numbers for a set range of integers. Execution is scaled across 10 different processes where each process computes the primes on a different set of numbers. For example, the first process computes primes for the set 1-10K, second process 10K-20K, third process 20K-30K, etc. The screen keeps track of the number of prime numbers encountered for each set and maintains a progress bar for each process.
![example3](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example3.gif)

#### Running the examples ####

Build the Docker image and run the Docker container using the instructions described in the [Development](#development) section. Run the example scripts within the container:

```bash
python examples/example#.py
```

### Projects using `mpcurses` ###

* [edgexfoundry/sync-github-labels](https://github.com/edgexfoundry/cd-management/tree/git-label-sync) A script that synchronizes GitHub labels and milestones

* [edgexfoundry/prune-github-tags](https://github.com/edgexfoundry/cd-management/tree/prune-github-tags) A script that prunes GitHub pre-release tags

### Development ###

Clone the repository and ensure the latest version of Docker is installed on your development server.


Build the Docker image:
```sh
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t \
mpcurses:latest .
```

Run the Docker container:
```sh
docker container run \
--rm \
-it \
-e http_proxy \
-e https_proxy \
-v $PWD:/code \
mpcurses:latest \
/bin/bash
```

Execute the build:
```sh
pyb -X
```

NOTE: the commands above assume your working behind a http proxy, if that is not the case then the proxy arguments can be discared from both commands.
