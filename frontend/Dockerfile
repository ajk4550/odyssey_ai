FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["node_modules/.bin/next", "dev", "-H", "0.0.0.0"]
