# syntax=docker/dockerfile:1
ARG NODE_VERSION=22.12.0

################################
# Base Stage
################################
FROM node:${NODE_VERSION}-alpine AS base

ARG PORT=3000

ENV NODE_ENV=production

WORKDIR /app

################################
# Dependencies Stage
################################
FROM base AS deps

# Copy package files
COPY --link package.json package-lock.json ./

# Install dependencies with no cache
RUN npm ci --prefer-offline --no-audit --omit=dev

################################
# Build Stage
################################
FROM base AS build

# Copy package files
COPY --link package.json package-lock.json ./

# Install build dependencies for native modules
RUN apk add --no-cache python3 make g++

RUN npm ci --prefer-offline --no-audit --legacy-peer-deps

# Copy application source
COPY --link . .

# Build the application
RUN npm run build

################################
# Production Runtime Stage
################################
FROM node:${NODE_VERSION}-alpine AS runner

ARG PORT=3000

WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nuxtjs -u 1001

# Set environment variables
ENV NODE_ENV=production \
    PORT=$PORT \
    HOST=0.0.0.0

# Copy built application from build stage
COPY --from=build --chown=nuxtjs:nodejs /app/.output /app/.output

# Switch to non-root user
USER nuxtjs

# Expose the application port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:${PORT}', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", ".output/server/index.mjs"]
