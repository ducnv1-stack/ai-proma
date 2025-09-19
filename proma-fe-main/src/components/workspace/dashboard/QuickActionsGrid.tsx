// file: src/components/workspace/dashboard/QuickActionsGrid.tsx
'use client';

import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Campaign as CampaignIcon,
  Analytics as AnalyticsIcon,
  People as PeopleIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

interface QuickActionsGridProps {
  onStartChat: () => void;
  onEditWorkspace: () => void;
}

export default function QuickActionsGrid({ onStartChat, onEditWorkspace }: QuickActionsGridProps) {
  const quickActions = [
    {
      title: 'Start AI Chat',
      description: 'Begin a conversation with your AI marketing assistant',
      icon: <CampaignIcon sx={{ fontSize: 40 }} />,
      color: 'primary' as const,
      action: onStartChat
    },
    {
      title: 'View Analytics',
      description: 'Check your campaign performance and insights',
      icon: <AnalyticsIcon sx={{ fontSize: 40 }} />,
      color: 'success' as const,
      action: () => console.log('Analytics clicked')
    },
    {
      title: 'Manage Team',
      description: 'Invite members and manage workspace permissions',
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      color: 'warning' as const,
      action: () => console.log('Team management clicked')
    },
    {
      title: 'Workspace Settings',
      description: 'Configure your workspace profile and preferences',
      icon: <SettingsIcon sx={{ fontSize: 40 }} />,
      color: 'secondary' as const,
      action: onEditWorkspace
    }
  ];

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3}>
        {quickActions.map((action, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                '&:hover': {
                  elevation: 6,
                  transform: 'translateY(-4px)'
                }
              }}
              onClick={action.action}
            >
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: 2,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: `${action.color}.light`,
                    color: `${action.color}.main`,
                    mx: 'auto',
                    mb: 2
                  }}
                >
                  {action.icon}
                </Box>
                <Typography variant="h6" fontWeight="bold" sx={{ mb: 1 }}>
                  {action.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.5 }}>
                  {action.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}