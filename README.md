
# mpcurses #
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


### Installation ###
```bash
pip install mpcurses
```

### How it works ###

The method you wish to execute concurrently is decorated with the queue handler decorator. The queue handler decorator creates a new log handler that will write all logged messages within the decorated method to a thread-safe queue. The main process creates the thread-safe message queue and handles the spawning of the desired number of concurrent processes, each process will be passed the reference to the message queue upon startup. As the process executes it will send all log messages to the message queue. The main process will then read messages from the message queue as they come in and update the curses screen accordingly. 

![mpcurses](/docs/images/mpcurses.png)

The layout of the curses screen is defined as a dictionary and can leverage builtin constructs for capturing messages, incrementing counters, and processing side effects such as changing text colors when certain messages appear.

The result is a screen that is being updated dynamically from one or more concurrent processes running in the background.

### Samples ###

| Sample             | Description/Features       |
|--------------------|----------------------------|
| samples/sample1.py | prime number counter / single process, screen update, count |
| samples/sample2.py | network name translator/ single process, screen update, count, visual indicator  |
| samples/sample3.py | firmware update simulator / multi-process, screen table update, count, visual indicator, process status |
| samples/sample4.py | prime number counter / multi-process, screen update, count, progress bar |
| samples/sample5.py | prime number counter / multi-process, no screen |
| samples/sample6.py | wrap-around table / multi-process, screen table update, process status |
| samples/colors.py  | displays available colors - most common ones |


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

python samples/sample1.py
```
NOTE: replace sample1.py with any of the samples described above (1-6).

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
