FROM node:23

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the UI code
COPY . .

# Expose port used by Vite
EXPOSE 5173

# Start development server (adjust as needed based on your package.json)
CMD ["npm", "run", "start"]