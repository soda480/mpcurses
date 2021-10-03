FROM python:3.9-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color
WORKDIR /code
COPY . /code/
RUN pip install pybuilder namegenerator
RUN pyb install