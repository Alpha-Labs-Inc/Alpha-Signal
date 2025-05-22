FROM node:23.5.0-slim

WORKDIR /ui

# Copy package files first to leverage caching
COPY package*.json ./

# Install dependencies using npm install
RUN npm install

# Copy the rest of the UI code
COPY . .

# Expose port used by Vite
EXPOSE 5173

# Ensure the server binds to 0.0.0.0
ENV HOST=0.0.0.0

# Start development server
CMD ["npm", "run", "start"]