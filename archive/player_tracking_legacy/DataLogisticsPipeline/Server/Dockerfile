FROM node:19-alpine

RUN mkdir -p ./app

WORKDIR ./app

ADD server.js server.js

EXPOSE 3000

RUN npm i mqtt@4.3.7
RUN npm i mongoose@6.7.2
RUN npm i kafka-node@5.0.0

RUN apk update
ENV DOCKERIZE_VERSION v0.6.1
RUN apk add --no-cache openssl
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN apk add --no-cache bash bash-doc bash-completion


CMD sh -c "dockerize -wait tcp://mosquitto:1883 -wait tcp://zookeeper:2181 -wait tcp://kafka:9092 -wait tcp://mongo:27017 -wait-retry-interval 3s node server.js"
