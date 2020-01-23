FROM node:13.6.0-alpine

COPY newman/ /etc/newman/

RUN npm install -g newman

WORKDIR /etc/newman

ENTRYPOINT ["newman", "run", "collections/collection.json", "-e", "environments/local.json"]