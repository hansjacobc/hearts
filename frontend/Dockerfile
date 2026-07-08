FROM node:24.18.0-alpine

WORKDIR /app

# corepack ships with node but isn't enabled by default in the image
RUN corepack enable

COPY package.json yarn.lock ./
RUN yarn install --immutable

COPY . .

EXPOSE 5173

CMD ["yarn", "dev", "--host"]