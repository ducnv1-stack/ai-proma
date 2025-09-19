// file: src/components/layout/UserProfileCard.tsx
'use client';

import {
  Box,
  Typography,
  Stack,
  Card,
  CardContent,
  Avatar,
  Chip
} from '@mui/material';
import {
  Person as PersonIcon,
  Circle as CircleIcon,
  AutoAwesome as SparklesIcon
} from '@mui/icons-material';
import { useAppContext } from '@/contexts/AppContext';

export default function UserProfileCard() {
  const { currentUser } = useAppContext();

  return (
    <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
        <Box
          sx={{
            width: 48,
            height: 48,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <SparklesIcon sx={{ color: 'white', fontSize: 28 }} />
        </Box>
        <Typography variant="h5" fontWeight="bold">
          Famarex
        </Typography>
      </Stack>
      
      {/* User Profile */}
      <Card elevation={0} sx={{ bgcolor: 'primary.light', color: 'primary.contrastText' }}>
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Avatar sx={{ bgcolor: 'primary.main', width: 48, height: 48 }}>
              {currentUser?.picture ? (
                <img src={currentUser.picture} alt={currentUser.name} style={{ width: '100%', height: '100%', borderRadius: '50%' }} />
              ) : (
                <PersonIcon />
              )}
            </Avatar>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle1" fontWeight="bold">
                {currentUser?.name || 'Loading...'}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                {currentUser?.email || 'Loading...'}
              </Typography>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 0.5 }}>
                <CircleIcon sx={{ fontSize: 8, color: 'success.main' }} />
                <Typography variant="caption">Online</Typography>
                {currentUser?.credit && (
                  <Chip 
                    label={`${currentUser.credit} credits`} 
                    size="small" 
                    sx={{ ml: 1, fontSize: '0.7rem', height: 20 }}
                  />
                )}
              </Stack>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
