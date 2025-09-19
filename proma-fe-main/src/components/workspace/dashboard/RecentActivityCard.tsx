// file: src/components/workspace/dashboard/RecentActivityCard.tsx
'use client';

import {
  Card,
  CardContent,
  Stack,
  Typography,
  Box,
  CircularProgress
} from '@mui/material';
import { WorkspaceNotification } from '@/libs/types';

interface RecentActivityCardProps {
  notifications: WorkspaceNotification[];
  isLoading: boolean;
}

export default function RecentActivityCard({ notifications, isLoading }: RecentActivityCardProps) {
  if (isLoading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
          <CircularProgress />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" fontWeight="bold" sx={{ mb: 2 }}>
          Recent Activity
        </Typography>
        <Stack spacing={2}>
          {Array.isArray(notifications) && notifications.slice(0, 5).map((notification) => (
            <Box key={notification.id}>
              <Typography variant="body2" fontWeight="medium">
                {notification.title}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {new Date(notification.created_at).toLocaleDateString()}
              </Typography>
            </Box>
          ))}
          {notifications.length === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
              No recent activity
            </Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}