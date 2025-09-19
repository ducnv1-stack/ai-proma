// file: src/components/layout/NavigationList.tsx
'use client';

import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Chat as ChatIcon,
  Campaign as CampaignIcon,
  Business as WorkspaceIcon,
  Analytics as AnalyticsIcon,
  People as PeopleIcon
} from '@mui/icons-material';
import { useRouter, usePathname } from 'next/navigation';

const navigationItems = [
  {
    id: 'chat',
    label: 'AI Chat',
    icon: <ChatIcon />,
    path: '/chat',
    description: 'Trò chuyện với AI Marketing'
  },
  {
    id: 'content-plans',
    label: 'Content Plans',
    icon: <CampaignIcon />,
    path: '/content-plans',
    description: 'Quản lý kế hoạch nội dung'
  },
  {
    id: 'workspace',
    label: 'Workspace',
    icon: <WorkspaceIcon />,
    path: '/workspace',
    description: 'Quản lý workspace'
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: <AnalyticsIcon />,
    path: '/analytics',
    description: 'Phân tích hiệu suất'
  },
  {
    id: 'team',
    label: 'Team',
    icon: <PeopleIcon />,
    path: '/team',
    description: 'Quản lý thành viên'
  }
];

export default function NavigationList() {
  const router = useRouter();
  const pathname = usePathname();

  const isActivePath = (path: string) => {
    return pathname === path || pathname.startsWith(path + '/');
  };

  return (
    <Box sx={{ flex: 1, overflow: 'auto' }}>
      <Typography variant="subtitle2" sx={{ px: 2, py: 1, color: 'text.secondary' }}>
        Navigation
      </Typography>
      <List sx={{ px: 1 }}>
        {navigationItems.map((item) => (
          <ListItem key={item.id} disablePadding>
            <ListItemButton 
              onClick={() => router.push(item.path)}
              selected={isActivePath(item.path)}
              sx={{ 
                borderRadius: 2, 
                mb: 0.5,
                '&.Mui-selected': {
                  bgcolor: 'primary.light',
                  color: 'primary.main',
                  '&:hover': {
                    bgcolor: 'primary.light',
                  }
                }
              }}
            >
              <ListItemIcon sx={{ 
                color: isActivePath(item.path) ? 'primary.main' : 'inherit'
              }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Typography variant="body2" fontWeight={isActivePath(item.path) ? 'bold' : 'medium'}>
                    {item.label}
                  </Typography>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    {item.description}
                  </Typography>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
}
