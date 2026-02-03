FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy configuration files
COPY config-overrides.js .
COPY postcss.config.js .
COPY tailwind.config.js .

# Copy application code
COPY public ./public
COPY src ./src

# Expose port
EXPOSE 3001

# Start the application
CMD ["npm", "start"]
