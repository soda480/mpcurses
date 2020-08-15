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

 Refer to [How It Works](https://github.com/soda480/mpcurses/wiki/How-It-Works) for additional detail.


### Installation ###
```bash
pip install mpcurses
```


### Samples ###

| Sample             | Description/Features       |
|--------------------|----------------------------|
| samples/sample1.py | prime number counter |
| samples/sample2.py | network name translator |
| samples/sample3.py | firmware update simulator |
| samples/sample4.py | prime number counter at scale |
| samples/sample5.py | prime number counter with no screen |
| samples/sample6.py | scaled execution showing a wrap-around table |
| samples/colors.py  | displays common screen colors |


#### Running the samples ####

Build the Docker image:
```bash
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t \
mpcurses:latest .
```

Execute the sample scripts:

```bash
docker container run \
--rm \
-it \
mpcurses:latest \
/bin/sh

python samples/sample#.py
```
NOTE: replace # with any of the samples described above (1-6).

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
