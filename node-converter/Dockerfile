# node-converter/Dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package.json tsconfig.json ./
COPY src ./src

RUN npm install
RUN npx tsc

EXPOSE 3001
CMD ["node", "dist/index.js"]