import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Create a client with custom configuration
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Stale time - how long data is considered "fresh"
      staleTime: 5 * 60 * 1000, // 5 minutes for OCI resources
      
      // Cache time - how long data stays in cache after component unmounts
      gcTime: 10 * 60 * 1000, // 10 minutes (previously cacheTime)
      
      // Retry configuration
      retry: (failureCount, error: any) => {
        // Don't retry on 401/403 errors (auth issues)
        if (error?.response?.status === 401 || error?.response?.status === 403) {
          return false;
        }
        // Retry up to 3 times for other errors
        return failureCount < 3;
      },
      
      // Retry delay with exponential backoff
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      
      // ✅ OPTIMIZED: Reduce unnecessary refetches to prevent API loops
      refetchOnWindowFocus: false, // Disabled to prevent excessive API calls on tab switching
      
      // Refetch on reconnect (keep this for legitimate reconnections)
      refetchOnReconnect: true,
      
      // Don't refetch on mount if data exists and is fresh
      refetchOnMount: false,
    },
    mutations: {
      // Retry mutations once
      retry: 1,
      
      // Retry delay for mutations
      retryDelay: 2000,
    },
  },
});

interface QueryProviderProps {
  children: React.ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* React Query Devtools - only shows in development */}
      <ReactQueryDevtools 
        initialIsOpen={false} 
      />
    </QueryClientProvider>
  );
}

// Export the query client for use in services
export { queryClient }; 