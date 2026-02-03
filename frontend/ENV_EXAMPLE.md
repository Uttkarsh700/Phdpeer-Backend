# Environment Variables Example

This file documents the required and optional environment variables for the frontend application.

**Note:** Create a `.env` file in the `frontend/` directory with these variables.

## Required Variables

```bash
# API Configuration
# Required: Base URL for the backend API
# Examples:
#   Development: http://localhost:8000
#   Production: https://api.yourdomain.com
#   Staging: https://staging-api.yourdomain.com
VITE_API_BASE_URL=http://localhost:8000
```

## Optional Variables

```bash
# API Configuration
VITE_API_TIMEOUT=30000          # API request timeout (milliseconds)
VITE_API_VERSION=v1            # API version

# Application Configuration
VITE_APP_NAME=PhD Timeline Intelligence Platform
VITE_APP_VERSION=0.1.0

# Development Server Configuration
VITE_DEV_SERVER_PORT=3000       # Port for Vite dev server
VITE_DEV_SERVER_PROXY_TARGET=http://localhost:8000  # Backend URL for proxy

# Feature Flags
VITE_ENABLE_ANALYTICS=false     # Enable analytics tracking
VITE_ENABLE_DEBUG=true          # Enable debug logging
VITE_ENABLE_MOCK_API=false      # Enable mock API for testing
```

## Quick Start

1. Copy this content to a `.env` file in the `frontend/` directory
2. Update `VITE_API_BASE_URL` to match your backend server
3. Restart the development server

## Environment-Specific Configuration

### Development (`.env.development`)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
VITE_DEV_SERVER_PROXY_TARGET=http://localhost:8000
```

### Production (`.env.production`)
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
```

### Staging (`.env.staging`)
```bash
VITE_API_BASE_URL=https://staging-api.yourdomain.com
VITE_ENABLE_DEBUG=true
```
