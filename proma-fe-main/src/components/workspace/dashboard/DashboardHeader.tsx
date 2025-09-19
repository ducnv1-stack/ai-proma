// file: src/components/workspace/dashboard/DashboardHeader.tsx
'use client';

import { useState } from 'react';
import {
  Paper,
  Stack,
  Avatar,
  Box,
  Typography,
  Chip,
  Badge,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Divider
} from '@mui/material';
import {
  People as PeopleIcon,
  Business as BusinessIcon,
  Notifications as NotificationsIcon,
  Campaign as CampaignIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  ExitToApp as ExitIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { Workspace, WorkspaceMember, WorkspaceNotification } from '@/libs/types';

interface DashboardHeaderProps {
  workspace: Workspace;
  members: WorkspaceMember[];
  notifications: WorkspaceNotification[];
  onEdit: () => void;
  onSwitch: () => void;
  onStartChat: () => void;
}

export default function DashboardHeader({ 
  workspace, 
  members, 
  notifications, 
  onEdit, 
  onSwitch, 
  onStartChat 
}: DashboardHeaderProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEditWorkspace = () => {
    handleMenuClose();
    onEdit();
  };

  const handleSwitchWorkspace = () => {
    handleMenuClose();
    onSwitch();
  };

  const unreadNotifications = Array.isArray(notifications) ? notifications.filter(n => !n.is_read).length : 0;

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 4, borderRadius: 3 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between">
        <Stack direction="row" alignItems="center" spacing={3}>
          <Avatar
            sx={{
              width: 64,
              height: 64,
              bgcolor: 'primary.main',
              fontSize: '1.5rem',
              fontWeight: 'bold'
            }}
            src={workspace.profile?.brand_logo_url}
          >
            {workspace?.name?.charAt(0).toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 1 }}>
              {workspace.profile?.brand_name || workspace.name}
            </Typography>
            {(workspace.description || workspace.profile?.brand_description) && (
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                {workspace.profile?.brand_description || workspace.description}
              </Typography>
            )}
            <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap">
              <Chip
                icon={<PeopleIcon />}
                label={`${members.length} member${members.length !== 1 ? 's' : ''}`}
                size="small"
                variant="outlined"
              />
              {workspace.profile?.business_type && (
                <Chip
                  icon={<BusinessIcon />}
                  label={workspace.profile.business_type}
                  size="small"
                  variant="outlined"
                  color="secondary"
                />
              )}
              {unreadNotifications > 0 && (
                <Badge badgeContent={unreadNotifications} color="error">
                  <Chip
                    icon={<NotificationsIcon />}
                    label="Notifications"
                    size="small"
                    variant="outlined"
                    color="warning"
                  />
                </Badge>
              )}
            </Stack>
          </Box>
        </Stack>

        <Stack direction="row" spacing={1}>
          <Button
            variant="contained"
            startIcon={<CampaignIcon />}
            onClick={onStartChat}
            size="large"
            sx={{ borderRadius: 2 }}
          >
            Start AI Chat
          </Button>
          <IconButton onClick={handleMenuClick}>
            <MoreVertIcon />
          </IconButton>
        </Stack>
      </Stack>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleEditWorkspace}>
          <EditIcon sx={{ mr: 2 }} />
          Edit Workspace Profile
        </MenuItem>
        <MenuItem onClick={handleSwitchWorkspace}>
          <ExitIcon sx={{ mr: 2 }} />
          Switch Workspace
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => console.log('Settings')}>
          <SettingsIcon sx={{ mr: 2 }} />
          Advanced Settings
        </MenuItem>
      </Menu>
    </Paper>
  );
}