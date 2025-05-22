FROM node:23.5.0-slim AS node

WORKDIR /ui

# Copy package files first to leverage caching
COPY package*.json ./

# Install dependencies using npm install
RUN npm install

# Copy the rest of the UI code
COPY . .
RUN npm run build

FROM nginx:alpine-slim

# Copy the built files from the previous stage
COPY --from=node /ui/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port used by Vite
EXPOSE 80

# Ensure the server binds to 0.0.0.0
ENV HOST=0.0.0.0

CMD ["nginx", "-g", "daemon off;"]