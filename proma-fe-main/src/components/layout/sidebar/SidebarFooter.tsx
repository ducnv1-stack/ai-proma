// file: src/components/layout/SidebarFooter.tsx
'use client';

import {
  Box,
  Button,
  Stack
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';
import { useAppContext } from '@/contexts/AppContext';

export default function SidebarFooter() {
  const { logout } = useAppContext();

  return (
    <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
      <Stack spacing={1}>
        <Button
          fullWidth
          variant="text"
          startIcon={<SettingsIcon />}
          sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
        >
          Settings
        </Button>
        <Button
          fullWidth
          variant="text"
          startIcon={<LogoutIcon />}
          onClick={logout}
          color="error"
          sx={{ justifyContent: 'flex-start', textTransform: 'none' }}
        >
          Logout
        </Button>
      </Stack>
    </Box>
  );
}
