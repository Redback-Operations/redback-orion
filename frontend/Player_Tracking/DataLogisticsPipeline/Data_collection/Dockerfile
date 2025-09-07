FROM node:19-alpine

RUN mkdir -p ./app

WORKDIR ./app

ADD sensor.js sensor.js
ADD data2.csv data2.csv

EXPOSE 3000

RUN npm i mqtt@4.3.7


RUN apk update
ENV DOCKERIZE_VERSION v0.6.1
RUN apk add --no-cache openssl
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz
RUN apk add --no-cache bash bash-doc bash-completion


CMD sh -c "dockerize -wait tcp://mosquitto:1883 -wait-retry-interval 3s node sensor.js"
