// file: src/app/login/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Container,
  Typography,
  Button,
  Stack,
  Divider,
  Card,
  CardContent,
  Paper
} from '@mui/material';
import {
  Google as GoogleIcon,
  Facebook as FacebookIcon,
  AutoAwesome as SparklesIcon
} from '@mui/icons-material';
import { authService } from '@/services/auth.service';
import { LoginForm } from '@/components/Auth/LoginForm';
import { ApiError } from '@/libs/utils/ApiError';



export default function LoginPage() {
  const [email, setEmail] = useState('admin@superbai.io');
  const [password, setPassword] = useState('Dinhhuy@04');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  // Check if already logged in (giữ nguyên)
  useEffect(() => {
    if (authService.isAuthenticated()) {
      router.push('/workspace');
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      // Logic gọi API giờ đã tinh gọn
      // authService.login sẽ tự động lưu token vào localStorage
      await authService.login({ email, password });
      
      // Chỉ cần điều hướng sau khi thành công
      router.push('/workspace');

    } catch (err) {
      console.error('Login error:', err);
      // Xử lý lỗi từ ApiError một cách tường minh
      if (err instanceof ApiError && err.body?.message) {
          setError(err.body.message);
      } else if (err instanceof Error) {
          setError(err.message);
      } else {
          setError('An unknown error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  // JSX giờ đây rất gọn gàng và mang tính tổng quan
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Container maxWidth="sm">
        <Card elevation={8} sx={{ borderRadius: 4 }}>
          <CardContent sx={{ p: 4 }}>
            {/* Header */}
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Box sx={{ width: 80, height: 80, borderRadius: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3 }}>
                <SparklesIcon sx={{ color: 'white', fontSize: 40 }} />
              </Box>
              <Typography variant="h3" fontWeight="bold" sx={{ mb: 1 }}>Welcome to Famarex</Typography>
              <Typography variant="h6" color="text.secondary">Your AI Marketing Assistant</Typography>
            </Box>

            <Stack spacing={3}>
              <Divider>
                <Typography variant="body2" color="text.secondary">or continue with email</Typography>
              </Divider>

              {/* Sử dụng LoginForm component */}
              <LoginForm
                email={email}
                onEmailChange={setEmail}
                password={password}
                onPasswordChange={setPassword}
                onSubmit={handleSubmit}
                isLoading={isLoading}
                error={error}
              />
            </Stack>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}