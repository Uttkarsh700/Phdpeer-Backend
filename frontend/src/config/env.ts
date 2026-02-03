/**
 * Environment configuration
 * 
 * Centralizes all environment variables with validation and type safety.
 * This is the SINGLE SOURCE OF TRUTH for all environment-based configuration.
 * 
 * IMPORTANT: Never hardcode URLs or API endpoints. Always use this config module.
 */

interface EnvironmentConfig {
  // API Configuration
  apiBaseUrl: string;
  apiTimeout: number;
  apiVersion: string;
  
  // Application Configuration
  appName: string;
  appVersion: string;
  
  // Environment Flags
  isDevelopment: boolean;
  isProduction: boolean;
  isTest: boolean;
  
  // Development Server Configuration (for Vite proxy)
  devServerPort: number;
  devServerProxyTarget: string;
}

/**
 * Validates required environment variables
 */
function validateEnv(): void {
  const required = ['VITE_API_BASE_URL'];
  const missing = required.filter(key => !import.meta.env[key]);
  
  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}\n` +
      'Please check your .env file. See .env.example for reference.'
    );
  }

  // Validate API URL format
  const apiUrl = import.meta.env.VITE_API_BASE_URL as string;
  if (apiUrl && !apiUrl.match(/^https?:\/\//)) {
    console.warn(
      '⚠️  VITE_API_BASE_URL should include protocol (http:// or https://). ' +
      'Current value:', apiUrl
    );
  }
}

// Validate on load
validateEnv();

/**
 * Application environment configuration
 * 
 * All API access should use env.apiBaseUrl - never hardcode URLs!
 */
export const env: EnvironmentConfig = {
  // API Configuration
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL as string,
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
  apiVersion: import.meta.env.VITE_API_VERSION || 'v1',
  
  // Application Configuration
  appName: import.meta.env.VITE_APP_NAME || 'PhD Timeline Intelligence Platform',
  appVersion: import.meta.env.VITE_APP_VERSION || '0.1.0',
  
  // Environment Flags
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  isTest: import.meta.env.MODE === 'test',
  
  // Development Server Configuration
  devServerPort: Number(import.meta.env.VITE_DEV_SERVER_PORT) || 3000,
  devServerProxyTarget: import.meta.env.VITE_DEV_SERVER_PROXY_TARGET || 'http://localhost:8000',
};

/**
 * Feature flags
 */
export const features = {
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
  enableMockApi: import.meta.env.VITE_ENABLE_MOCK_API === 'true',
};

/**
 * Get full API URL for a given endpoint path
 * 
 * @param path - API endpoint path (e.g., '/assessments' or 'assessments')
 * @returns Full URL with base URL and path
 * 
 * @example
 * ```ts
 * const url = getApiUrl('/assessments');
 * // Returns: 'http://localhost:8000/api/v1/assessments'
 * ```
 */
export function getApiUrl(path: string): string {
  // Remove leading slash if present, we'll add it properly
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  const baseUrl = env.apiBaseUrl.endsWith('/') 
    ? env.apiBaseUrl.slice(0, -1) 
    : env.apiBaseUrl;
  
  return `${baseUrl}/api/${env.apiVersion}/${cleanPath}`;
}

/**
 * Log configuration in development mode (for debugging)
 */
if (env.isDevelopment && features.enableDebug) {
  console.log('🔧 Environment Configuration:', {
    apiBaseUrl: env.apiBaseUrl,
    apiVersion: env.apiVersion,
    apiTimeout: env.apiTimeout,
    mode: import.meta.env.MODE,
  });
}

export default env;
