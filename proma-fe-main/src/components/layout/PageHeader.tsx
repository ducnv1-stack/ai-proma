// file: src/components/layout/PageHeader.tsx
'use client';

import {
  Box,
  Typography,
  Stack,
  Paper,
  Chip
} from '@mui/material';
import { Circle as CircleIcon } from '@mui/icons-material';

interface PageHeaderProps {
  title?: string;
  subtitle?: string;
  headerActions?: React.ReactNode;
}

export default function PageHeader({ title, subtitle, headerActions }: PageHeaderProps) {
  // Nếu không có title hoặc subtitle, không render gì cả
  if (!title && !subtitle) {
    return null;
  }

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 3, 
        borderBottom: 1, 
        borderColor: 'divider',
        bgcolor: 'background.paper',
        // Thêm zIndex để đảm bảo nó nằm dưới nút toggle sidebar
        position: 'relative',
        zIndex: 1
      }}
    >
      <Stack direction="row" justifyContent="space-between" alignItems="center">
        <Box>
          {title && (
            <Typography variant="h5" fontWeight="bold">
              {title}
            </Typography>
          )}
          {subtitle && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <Stack direction="row" spacing={2} alignItems="center">
          <Chip
            icon={<CircleIcon sx={{ fontSize: 12, color: 'success.main' }} />}
            label="Online"
            variant="outlined"
            size="small"
          />
          {headerActions}
        </Stack>
      </Stack>
    </Paper>
  );
}