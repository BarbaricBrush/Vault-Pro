FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# We use dev mode for now to support hot reloading during this process
CMD ["npm", "run", "dev"]
