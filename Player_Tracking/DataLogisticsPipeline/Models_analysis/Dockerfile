FROM python:3.9.14-slim
RUN mkdir script
WORKDIR script
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD consumer.py consumer.py
ADD model_trained.pkl model_trained.pkl

RUN apt-get update

RUN apt-get install -y wget
ENV DOCKERIZE_VERSION v0.6.1
RUN apt-get install -y openssl \
    && wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN apt-get install -y bash bash-doc bash-completion


CMD sh -c "dockerize -wait tcp://zookeeper:2181 -wait tcp://kafka:9092 -wait-retry-interval 3s python3 -u consumer.py"