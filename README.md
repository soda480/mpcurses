[![GitHub Workflow Status](https://github.com/soda480/mpcurses/workflows/build/badge.svg)](https://github.com/soda480/mpcurses/actions)
[![Code Coverage](https://codecov.io/gh/soda480/mpcurses/branch/master/graph/badge.svg)](https://codecov.io/gh/soda480/mpcurses)
[![Code Quality Score](https://www.code-inspector.com/project/12270/score/svg)](https://frontend.code-inspector.com/project/12270/dashboard)
[![Code Grade](https://www.code-inspector.com/project/12270/status/svg)](https://frontend.code-inspector.com/project/12270/dashboard)
[![PyPI version](https://badge.fury.io/py/mpcurses.svg)](https://badge.fury.io/py/mpcurses)

# mpcurses #
The mpcurses framework enables visualization of function execution. It consists of a simple set of APIs that provide an abstraction for multiprocessing and the curses screen painting library. The main features:

* Execute a function across one or more concurrent processes
* Queue execution to ensure a predefined number of processes are running
* Visualize function execution using curses screen
* Define a screen layout using a Python dict
* Leverage built-in directives for dynamically updating the screen using the executing function log messages
  * Keep numeric counts
  * Update text values
  * Update text colors
  * Maintain visual indicators
  * Update progress bars
  * Display tables

The framework can be used on any ordinary Python function. The only requirement for enabling the visualization of the function execution is to ensure the function implements logging. The framework takes care of setting up the multiprocessing, the curses screen and the thread-safe queues required for communication.

Refer to [How It Works](https://github.com/soda480/mpcurses/wiki/How-It-Works) for additional detail.


### Installation ###
```bash
pip install mpcurses
```

### Samples ###
Serveral [samples](/samples) are included to help introduce the mpcurses framework. Note the functions executed in the samples below are ordinary Python functions that have no context about multiprocessing or curses, they simply perform a function on a given dataset.

#### [sample1](/samples/sample1.py)
Execute a function that counts the prime numbers between 1 and 10K. The screen keeps track of the current number and count the number of primes and non-primes have been processed.
![sample1](/docs/images/sample1.gif)

#### [sample2](/samples/sample2.py)
Execute a function that translates the name of multiple networks. The screen keeps track of the number of networks that have been translated, blacklisted and not translated. It also maintains a visual of the aforementioned indicators.
![sample2](/docs/images/sample2.gif)

#### [sample3](/samples/sample3.py)
Execute a function that upgrades server firmware on a rack consisting of multiple servers. The upgrade consists of several tasks, the screen keeps track of the current task being executed and its status. The execution is scaled and runs on three servers at a time.
![sample3](/docs/images/sample3.gif)

#### [sample4](/samples/sample4.py)
Execute the same prime number function as in first sample, but now execution is scaled across 10 different processes where each process owns computing the primes on a different set of numbers. For example, the first process computes primes for numbers 1-10K, second process 10K-20K, third process 20K-30K, etc. The screen also maintains a progress bar of where each process is currently at.
![sample4](/docs/images/sample4.gif)

#### Running the samples ####

Build the Docker image and run the Docker container using the instructions below in the [Development](#development) section. Run the sample scripts, replace the # with any of the samples (1-6):

```bash
python samples/sample#.py
```

### Real Use Cases ###

Synchronize GitHub labels and milestones:

https://github.com/edgexfoundry/cd-management/tree/git-label-sync

Prune GitHub release and commit tags:

https://github.com/edgexfoundry/cd-management/tree/prune-github-tags

### Development ###

Ensure the latest version of Docker is installed on your development server.

Clone the repository:
```sh
cd
git clone https://github.com/soda480/mpcurses.git
cd mpcurses
```

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
-v $PWD:/mpcurses \
mpcurses:latest \
/bin/sh
```

Execute the build:
```sh
pyb -X
```

NOTE: commands above assume working behind a proxy, if not then the proxy arguments to both the docker build and run commands can be removed.
