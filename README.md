# mpcurses
[![build+test](https://github.com/soda480/mpcurses/actions/workflows/main.yml/badge.svg)](https://github.com/soda480/mpcurses/actions/workflows/main.yml)
[![coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://pybuilder.io/)
[![complexity](https://img.shields.io/badge/complexity-A-brightgreen)](https://radon.readthedocs.io/en/latest/api.html#module-radon.complexity)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/mpcurses.svg)](https://badge.fury.io/py/mpcurses)
[![python](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.12-teal)](https://www.python.org/downloads/)

The mpcurses package facilitates seamless terminal screen updates from child processes within a multiprocessing worker pool - leveraging the curses library for terminal manipulation. The `MPcurses` class is a subclass of [MPmq](https://pypi.org/project/mpmq/); a multiprocessing message queue which enables inter-process communication (IPC) between child workers and a parent process through queuing and consumption of log messages. Mpcurses provides a lightweight abstraction for the curses terminal screen, representing it as a Python dictionary. It includes predefined directives for updating the screen, encompassing:

- Numeric counter management
- Match messages using regular expressions
- Text value and color updates
- Visual indicator maintenance
- Progress bar rendering
- Table and list displays

 Refer to the MPcurses documentation here: https://soda480.github.io/mpcurses/

### Installation
```bash
pip install mpcurses
```
### Examples

Invoke a single child process to execute a task defined by the `do_something` function. Mpcurses captures all log messages and sends them to a thread-safe queue, the main process consumes messages and uses regular expressions to update the screen which is represented as a dictionary.

```python
from mpcurses import MPcurses
import namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_something(*args):
    for _ in range(0, 400):
        logger.debug(f'processing item "{namegenerator.gen()}"')
        time.sleep(.01)

MPcurses(
    function=do_something,
    screen_layout={
        'display_item': {
            'position': (1, 1), 'text': 'Processing:', 'text_color': 0, 'color': 14,
            'clear': True, 'regex': r'^processing item "(?P<value>.*)"$'}
    }).execute()
 ```

Executing the code above results in the following:
![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/demo.gif)

**NOTE** none of the functions being executed in any of the examples include information about the curses screen, multiprocessing or messaging queue - this is handled seamlessly by mpcurses.

Build the Docker image using the instructions below, run the examples. `python examples/##/sample.py`

#### [Prime Numbers Counter](https://github.com/soda480/mpcurses/blob/master/examples/03/sample.py)

Execute a function that calculates prime numbers for a set range of integers. Execution is scaled across 7 different workers where each process computes the primes for a different range of numbers. For example, the first worker computes primes for the range 1-10K, second worker computes for the range 10K-20K, etc. The main process keeps track of the number of prime numbers encountered for each worker and shows overall progress for each worker using a progress bar.

![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example3.gif)

#### [Item Processor](https://github.com/soda480/mpcurses/blob/master/examples/06/sample.py)

Execute a function that processes a list of random items. Execution is scaled across 3 workers where each worker processes a unique set of items. The main process maintains indicators showing the number of items that have been processed by each worker; counting the number of Successful, Errors and Warnings. Three lists are also maintained, one for each group that list which specific items had Warnings and Failures.

![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example6.gif)

#### [Bay Enclosure Firmware Update](https://github.com/soda480/mpcurses/blob/master/examples/09/sample.py)

Execute a function that contains a workflow containing tasks to update firmware on a server residing in a blade enclosure. Execution is scaled across a worker pool with five active workers. The main process updates the screen showing status of each worker as they execute the workflow tasks for each blade server. 

![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example9.gif)

### Projects using `mpcurses`

* [edgexfoundry/sync-github-labels](https://github.com/edgexfoundry/cd-management/tree/git-label-sync) A script that synchronizes GitHub labels and milestones

* [edgexfoundry/prune-github-tags](https://github.com/edgexfoundry/cd-management/tree/prune-github-tags) A script that prunes GitHub pre-release tags

### Development

Clone the repository and ensure the latest version of Docker is installed on your development server.

Build the Docker image:
```sh
docker image build \
-t mpcurses:latest .
```

Run the Docker container:
```sh
docker container run \
--rm \
-it \
-v $PWD:/code \
mpcurses:latest \
bash
```

Execute the build:
```sh
pyb -X
```
