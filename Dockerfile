FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /virs
WORKDIR /virs
ADD requirements.txt /virs/
RUN pip install -r requirements.txt
ADD . /virs/
