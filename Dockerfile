FROM python:3.11.4
# FROM python:3.11.4-alpine

WORKDIR /usr/src/app

# prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# ensure Python output is sent to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# Install necessary build dependencies
RUN apt-get update
# RUN apt-get install -y gcc libc6-dev mariadb-client libffi-dev python3-dev
# RUN apt-get install -y coinor-cbc


# Install pip and other Python dependencies
RUN pip install --upgrade pip setuptools wheel

# Copy the requirements file first to leverage Docker cache
COPY ./requirements.txt /usr/src/app/requirements.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the project files
COPY . /usr/src/app/
