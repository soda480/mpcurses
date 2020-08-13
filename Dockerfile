FROM python:3.6-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV TERM xterm-256color

WORKDIR /mpcurses

COPY . /mpcurses/

RUN pip install pybuilder==0.11.17
RUN pyb install_dependencies
RUN pyb clean
RUN pyb install

CMD echo 'DONE'