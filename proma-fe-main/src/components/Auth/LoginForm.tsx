// file: src/components/login/LoginForm.tsx
'use client';

import {
  TextField,
  Button,
  Stack,
  CircularProgress,
  InputAdornment,
  Alert,
  Box,
} from '@mui/material';
import { Email as EmailIcon, Lock as LockIcon } from '@mui/icons-material';

// Định nghĩa kiểu cho các props mà component này sẽ nhận
interface LoginFormProps {
  email: string;
  onEmailChange: (value: string) => void;
  password: string;
  onPasswordChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => Promise<void>;
  isLoading: boolean;
  error: string;
}

export function LoginForm({
  email,
  onEmailChange,
  password,
  onPasswordChange,
  onSubmit,
  isLoading,
  error,
}: LoginFormProps) {
  return (
    <>
      {error && (
        <Alert severity="error" sx={{ borderRadius: 2, mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box component="form" onSubmit={onSubmit}>
        <Stack spacing={3}>
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => onEmailChange(e.target.value)}
            required
            disabled={isLoading}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <EmailIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />
          
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={password}
            onChange={(e) => onPasswordChange(e.target.value)}
            required
            disabled={isLoading}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <LockIcon color="action" />
                </InputAdornment>
              ),
            }}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
          />

          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={isLoading}
            sx={{ py: 1.5, borderRadius: 2, fontSize: '1rem', fontWeight: 600 }}
          >
            {isLoading ? (
              <Stack direction="row" alignItems="center" spacing={1}>
                <CircularProgress size={20} color="inherit" />
                <span>Signing in...</span>
              </Stack>
            ) : (
              'Sign In'
            )}
          </Button>
        </Stack>
      </Box>
    </>
  );
}