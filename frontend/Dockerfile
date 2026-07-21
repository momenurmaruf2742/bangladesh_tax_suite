FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

# Run Vite dev server with host mapping for external access
CMD ["npm", "run", "dev", "--", "--host"]
