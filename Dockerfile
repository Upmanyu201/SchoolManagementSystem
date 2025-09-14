FROM node:latest
COPY . /app
COPY package*.json /app
WORKDIR /app
RUN npm install