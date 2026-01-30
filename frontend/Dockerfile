# Multi-stage build for production-ready UI container
# Stage 1: Build
FROM node:20-slim as builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Set API URL for build (defaults to localhost:8080 if not provided)
ARG VITE_API_URL=http://localhost:8080
ENV VITE_API_URL=$VITE_API_URL

# Build for production
RUN npm run build


# Stage 2: Production server with nginx
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration for SPA routing
RUN echo 'server { \
    listen 3000; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Expose port 3000
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
