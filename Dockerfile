FROM python:3.6.5-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

RUN mkdir /mpcurses
COPY . /mpcurses/
WORKDIR /mpcurses

RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb clean
RUN pyb install

CMD echo 'DONE'