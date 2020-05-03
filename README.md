
# mpcurses #
mpcurses is a framework that exposes a simple set of APIs enabling multi-process integration with the curses screen painting library.

With the mpcurses APIs, the complexities of setting up multi-processing within a curses environment are abstracted away. The only requirement is that the target method needs to implement logging. 

### How it works ###

The method you wish to execute concurrently is decorated with the queue handler decorator. The queue handler decorator creates a new log handler that will write all logged messages within the decorated method to a thread-safe queue. The main process creates the thread-safe message queue and handles the spawning of the desired number of concurrent processes, each process will be passed the reference to the message queue upon startup. The main process will then read messages from the message queue as they come in and update the curses screen accordingly. 

![mpcurses](/docs/images/mpcurses.png)

The layout of the curses screen is defined as a dictionary and can leverage builtin constructs for capturing messages, incrementing counters, and processing side effects such as changing text colors when certain messages appear.

The result is a dynamic screen that is being updated dynamically from any number of concurrent processes running in the background.

### Running the samples ###

| Sample             | Description/Features       |
|--------------------|----------------------------|
| samples/sample1.py | Prime number counter / single process, screen update, count  |
| samples/sample2.py | Network name translator/ single proces, screen update, count, ticker   |
| samples/sample3.py | Firmware update simulator / multi-process, screen update, count, indicator, process status |


Build the Docker image:
```bash
docker image build \
--build-arg http_proxy \
--build-arg https_proxy \
-t mpcurses:latest .
```

Execute the sample scripts:

```bash
docker container run \
--rm \
-it \
mpcurses:latest \
python samples/sample1.py
```

```bash
docker container run \
--rm \
-it \
mpcurses:latest \
python samples/sample2.py
```

```bash
docker container run \
--rm \
-it \
mpcurses:latest \
python samples/sample3.py
```

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
-t mpcurses:latest .
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
