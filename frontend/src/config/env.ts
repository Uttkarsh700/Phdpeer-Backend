/**
 * Environment configuration
 * 
 * Centralizes all environment variables with validation and type safety.
 */

interface EnvironmentConfig {
  apiBaseUrl: string;
  appName: string;
  isDevelopment: boolean;
  isProduction: boolean;
  apiTimeout: number;
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
      'Please check your .env file.'
    );
  }
}

// Validate on load
validateEnv();

/**
 * Application environment configuration
 */
export const env: EnvironmentConfig = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL as string,
  appName: import.meta.env.VITE_APP_NAME || 'PhD Timeline Intelligence Platform',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
};

/**
 * Feature flags (if needed in future)
 */
export const features = {
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  enableDebug: import.meta.env.VITE_ENABLE_DEBUG === 'true',
};

export default env;
