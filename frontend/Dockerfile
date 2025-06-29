FROM node:20-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install --production
COPY . .
RUN npm run build
EXPOSE 443
CMD ["npx", "serve", "-s", "build", "-l", "443", "--ssl-cert", "public/cert/cert.pem", "--ssl-key", "public/cert/key.pem"]
