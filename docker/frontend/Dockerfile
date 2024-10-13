FROM node:16

WORKDIR /opt/star-burger

COPY package.json package-lock.json /opt/star-burger/

RUN npm ci

COPY ./bundles-src /opt/star-burger/bundles-src

RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
