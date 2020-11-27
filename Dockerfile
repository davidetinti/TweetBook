FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /cointainer
WORKDIR /container
COPY requirements.txt /container/
RUN pip install -r requirements.txt
ADD . /container/
