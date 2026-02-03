# Configuration Module

This module provides centralized environment-based configuration for the application.

## Usage

```typescript
import { env, features, getApiUrl } from '@/config';

// Access configuration values
const apiUrl = env.apiBaseUrl;
const timeout = env.apiTimeout;
const isDev = env.isDevelopment;

// Check feature flags
if (features.enableDebug) {
  console.log('Debug mode enabled');
}

// Build full API URLs
const fullUrl = getApiUrl('assessments');
```

## Environment Variables

All environment variables must be prefixed with `VITE_` to be accessible in the browser.

### Required Variables

- `VITE_API_BASE_URL` - Base URL for the backend API (e.g., `http://localhost:8000`)

### Optional Variables

- `VITE_API_TIMEOUT` - API request timeout in milliseconds (default: 30000)
- `VITE_API_VERSION` - API version (default: `v1`)
- `VITE_APP_NAME` - Application name
- `VITE_APP_VERSION` - Application version
- `VITE_DEV_SERVER_PORT` - Development server port (default: 3000)
- `VITE_DEV_SERVER_PROXY_TARGET` - Proxy target for development (default: `http://localhost:8000`)
- `VITE_ENABLE_ANALYTICS` - Enable analytics (default: `false`)
- `VITE_ENABLE_DEBUG` - Enable debug logging (default: `false`)
- `VITE_ENABLE_MOCK_API` - Enable mock API (default: `false`)

## Example .env File

Create a `.env` file in the `frontend/` directory:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_API_VERSION=v1

# Application Configuration
VITE_APP_NAME=PhD Timeline Intelligence Platform
VITE_APP_VERSION=0.1.0

# Development Server
VITE_DEV_SERVER_PORT=3000
VITE_DEV_SERVER_PROXY_TARGET=http://localhost:8000

# Feature Flags
VITE_ENABLE_DEBUG=true
VITE_ENABLE_ANALYTICS=false
```

## Environment-Specific Files

You can create environment-specific files:
- `.env.development` - Loaded in development mode
- `.env.production` - Loaded in production mode
- `.env.local` - Local overrides (ignored by git)
