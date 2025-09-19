'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Box, CircularProgress, Typography, Stack } from '@mui/material';
import { AutoAwesome as SparklesIcon } from '@mui/icons-material';
import { authService } from '@/services/auth.service';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('famarex_token');
        
        if (!token) {
          router.push('/workspace');
          return;
        }

        // Verify token is still valid
        if (authService.isAuthenticated()) {
          // Try to get current user to validate token
          try {
          
            setIsAuthenticated(true);
          } catch (error) {
            console.error('Token validation failed:', error);
            // Token is invalid, redirect to workspace
            localStorage.removeItem('famarex_token');
            localStorage.removeItem('famarex_user');
            localStorage.removeItem('famarex_refresh_token');
            localStorage.removeItem('famarex_workspace');
            router.push('/workspace');
            return;
          }
        } else {
          router.push('/workspace');
          return;
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        router.push('/workspace');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  if (isLoading) {
    return (
      <Box 
        sx={{ 
          height: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          bgcolor: 'background.default'
        }}
      >
        <Stack spacing={3} alignItems="center">
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: 3,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'pulse 2s infinite'
            }}
          >
            <SparklesIcon sx={{ color: 'white', fontSize: 40 }} />
          </Box>
          <Typography variant="h5" fontWeight="bold">
            Authenticating...
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Verifying your credentials
          </Typography>
          <CircularProgress />
        </Stack>
      </Box>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect to workspace
  }

  return <>{children}</>;
}
