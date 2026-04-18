ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS build-image

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TERM=xterm-256color \
    PYTHONPATH=/code/docs/examples

WORKDIR /code
COPY . /code/

RUN apt-get update && \
    apt-get install -y --no-install-recommends make && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip faker && \
    pip install -e .[dev] && \
    make build


FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TERM=xterm-256color \
    PYTHONPATH=/opt/mpcurses/examples

WORKDIR /opt/mpcurses

COPY --from=build-image /code/dist/mpcurses-*.tar.gz /opt/mpcurses
COPY --from=build-image /code/docs/examples /opt/mpcurses/examples

RUN pip install faker mpcurses-*.tar.gz

