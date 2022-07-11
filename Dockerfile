ARG PYTHON_VERSION=3.9
FROM python:${PYTHON_VERSION}-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color
WORKDIR /code
COPY . /code/
RUN pip install --upgrade pip && pip install pybuilder namegenerator
RUN pyb -X