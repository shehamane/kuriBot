FROM python:latest

RUN mkdir /build
WORKDIR /build
COPY requirements.txt /build/
RUN pip install -r requirements.txt
COPY . /build