# Use official node image as base
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy frontend source code
COPY ./frontend .

# Install serve to serve static files
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Serve the frontend
CMD ["serve", "-s", ".", "-l", "3000"]
