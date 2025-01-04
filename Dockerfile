ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV TERM=xterm-256color
ENV PYTHONPATH=/code/examples/
WORKDIR /code
COPY . /code/
RUN pip install --upgrade pip && \
    pip install pybuilder namegenerator faker
RUN pyb -X