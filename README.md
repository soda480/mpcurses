[![ci](https://github.com/soda480/mpcurses/actions/workflows/ci.yml/badge.svg)](https://github.com/soda480/mpcurses/actions/workflows/ci.yml)
![Coverage](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/badges/coverage.svg)
[![PyPI version](https://badge.fury.io/py/mpcurses.svg)](https://badge.fury.io/py/mpcurses)

# mpcurses

`mpcurses` is a Python package for running work in multiple processes and visualizing that work live in the terminal using `curses`.

It is built for programs where multiple workers are running in parallel and you need a clean, real-time view of what’s happening. Under the hood, `MPcurses` builds on [mpmq](https://pypi.org/project/mpmq/) to move messages from child processes back to the parent process. Your workers emit normal log messages. `mpcurses` consumes those messages, matches them with regular expressions, and updates specific parts of the screen based on a declarative `screen_layout`.

## Why use `mpcurses`

Parallel workloads usually break terminal output:

- logs get mixed together
- progress is hard to track
- building a clean UI takes too much effort

`mpcurses` fixes that by separating concerns:

- workers do the work  
- workers log messages  
- the main process renders the UI  

You get structured, readable output without polluting your worker code.

`mpcurses` gives you a practical way to build terminal dashboards for multiprocessing workloads without forcing curses logic into your worker functions. If your automation or CLI already emits useful log messages, `mpcurses` lets you turn those messages into a structured, real-time terminal UI.

Refer to the MPcurses documentation here: https://soda480.github.io/mpcurses/

## Installation

```bash
pip install mpcurses
```

## Quick Start

Run a simple example:

```Python
from mpcurses import MPcurses
from time import sleep
import logging
import uuid
import random

logger = logging.getLogger(__name__)

def do_work(worker_id=None, num_items=None):
    logger.debug(f'worker {worker_id} will process {num_items} items')
    for _ in range(num_items):
        logger.debug(f'processing item "{uuid.uuid4()}"')
        sleep(.01)

def main():
    MPcurses(
        function=do_work,
        process_data=[{'worker_id': f'Worker-{i}', 'num_items': random.randint(100, 200)} for i in range(3)],
        screen_layout={
            'worker': {'position': (1, 1), 'color': 2, 'table': True, 'clear': True, 'regex': r'^worker (?P<value>.*) will process \d+ items$'},
            'num_items': {'position': (1, 10), 'color': 4, 'table': True, 'clear': True, 'regex': r'^worker .* will process (?P<value>\d+) items$'},
            'item': {'position': (1, 14), 'color': 6, 'table': True, 'clear': True, 'regex': r'^processing item "(?P<value>.*)"$'},
        }).execute()

if __name__ == '__main__':
    main()
```

![demo](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/demo.gif)

### What this example does

Runs 3 workers in parallel and displays their activity as a live table in the terminal.

### How it works

Each worker receives its own worker_id and a random number of items, then logs when it starts and as it processes each item. mpcurses captures those log messages from all processes and uses the screen_layout regex rules to extract values and render them into a table, where each row represents a worker and updates in real time.

### Result

You get a real-time table showing all workers updating independently as they run. No interleaved logs. No manual curses code. Just structured output driven by log messages.

## Examples

Build the Docker image using the instructions below, run the examples. `python examples/##/sample.py`

### [Prime Numbers Counter](https://github.com/soda480/mpcurses/blob/master/examples/03/sample.py)

Execute a function that calculates prime numbers for a set range of integers. Execution is scaled across 7 different workers where each process computes the primes for a different range of numbers. For example, the first worker computes primes for the range 1-10K, second worker computes for the range 10K-20K, etc. The main process keeps track of the number of prime numbers encountered for each worker and shows overall progress for each worker using a progress bar.

![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example3.gif)

### [Item Processor](https://github.com/soda480/mpcurses/blob/master/examples/06/sample.py)

Execute a function that processes a list of random items. Execution is scaled across 3 workers where each worker processes a unique set of items. The main process maintains indicators showing the number of items that have been processed by each worker; counting the number of Successful, Errors and Warnings. Three lists are also maintained, one for each group that list which specific items had Warnings and Failures.

![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example6.gif)

### [Bay Enclosure Firmware Update](https://github.com/soda480/mpcurses/blob/master/examples/09/sample.py)

Execute a function that contains a workflow containing tasks to update firmware on a server residing in a blade enclosure. Execution is scaled across a worker pool with five active workers. The main process updates the screen showing status of each worker as they execute the workflow tasks for each blade server. 

![example](https://raw.githubusercontent.com/soda480/mpcurses/master/docs/images/example9.gif)

## Projects using `mpcurses`

* [edgexfoundry/sync-github-labels](https://github.com/edgexfoundry/cd-management/tree/git-label-sync) A script that synchronizes GitHub labels and milestones

* [edgexfoundry/prune-github-tags](https://github.com/edgexfoundry/cd-management/tree/prune-github-tags) A script that prunes GitHub pre-release tags

## Development

Clone the repository and ensure the latest version of Docker is installed on your development server.

Build the Docker image:
```sh
docker image build \
--target build-image \
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
make dev
```
