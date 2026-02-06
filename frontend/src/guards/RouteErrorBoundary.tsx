/**
 * Route Error Boundary
 * 
 * Catches errors in route guards and prevents crashes.
 * Provides graceful fallback UI.
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';

interface Props {
  children: ReactNode;
  fallbackRoute?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Route Error Fallback Component
 * Wrapped in a component that can use hooks
 */
function RouteErrorFallbackWrapper({ 
  error, 
  fallbackRoute = '/home' 
}: { 
  error: Error | null;
  fallbackRoute?: string;
}) {
  // useNavigate hook - should work since RouteErrorBoundary is inside BrowserRouter
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate(fallbackRoute, { replace: true });
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="max-w-md w-full">
        <CardHeader>
          <CardTitle>Navigation Error</CardTitle>
          <CardDescription>
            An error occurred while navigating. This has been logged for review.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="text-sm text-muted-foreground">
              <p className="font-medium">Error details:</p>
              <p className="mt-1 font-mono text-xs">{error.message}</p>
            </div>
          )}
          <Button onClick={handleGoHome} className="w-full">
            Go to Home
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Route Error Boundary Class Component
 * 
 * Catches errors in route guards and navigation.
 * Prevents app crashes by showing fallback UI.
 */
class RouteErrorBoundaryClass extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error for debugging
    console.error('Route error boundary caught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <RouteErrorFallbackWrapper 
          error={this.state.error} 
          fallbackRoute={this.props.fallbackRoute}
        />
      );
    }

    return this.props.children;
  }
}

/**
 * Route Error Boundary Component
 * 
 * Wraps routes to catch errors and prevent crashes.
 * 
 * Usage:
 * ```tsx
 * <RouteErrorBoundary fallbackRoute="/home">
 *   <Routes>
 *     ...
 *   </Routes>
 * </RouteErrorBoundary>
 * ```
 */
export function RouteErrorBoundary({ children, fallbackRoute }: Props) {
  return (
    <RouteErrorBoundaryClass fallbackRoute={fallbackRoute}>
      {children}
    </RouteErrorBoundaryClass>
  );
}
