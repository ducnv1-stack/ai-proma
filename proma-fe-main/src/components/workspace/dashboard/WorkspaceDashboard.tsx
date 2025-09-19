'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import {
  Box,
  Container,
  Grid,
  Alert,
  Paper,
  Stack,
  Typography,
  Button,
  CircularProgress
} from '@mui/material';
import { Business as BusinessIcon } from '@mui/icons-material';
import { Workspace } from '../../../libs/types';
import AppLayout from '../../layout/AppLayout';
import DashboardHeader from './DashboardHeader';
import QuickActionsGrid from './QuickActionsGrid';
import TeamMembersCard from './TeamMembersCard';
import RecentActivityCard from './RecentActivityCard';
import { useWorkspaceDashboard } from '../../../hooks/useWorkspaceDashboard';

// Dynamic import to prevent hydration issues
const WorkspaceProfileModal = dynamic(() => import('../WorkspaceProfileModal'), {
  ssr: false,
  loading: () => <CircularProgress />
});

interface WorkspaceDashboardProps {
  workspace: Workspace;
  onWorkspaceChange: () => void;
  onStartChat: () => void;
}

export default function WorkspaceDashboard({ workspace, onWorkspaceChange, onStartChat }: WorkspaceDashboardProps) {
  const [showProfileModal, setShowProfileModal] = useState(false);

  const {
    workspace: currentWorkspace,
    members,
    notifications,
    isLoading,
    error,
    handleProfileUpdated
  } = useWorkspaceDashboard(workspace);


  const handleEditWorkspace = () => {
    setShowProfileModal(true);
  };

  const handleSwitchWorkspace = () => {
    onWorkspaceChange();
  };

  // Don't render until mounted to prevent hydration mismatch

  if (isLoading) {
    return (
      <AppLayout title="Loading Workspace...">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <CircularProgress size={48} />
        </Box>
      </AppLayout>
    );
  }

  return (

      <AppLayout 
        title={currentWorkspace?.profile?.brand_name || currentWorkspace?.name}
        subtitle={currentWorkspace?.profile?.brand_description || currentWorkspace?.description || 'Workspace Dashboard'}
      >
        <Container maxWidth="lg" sx={{ py: 4 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          {/* Dashboard Header */}
          {currentWorkspace && (
            <DashboardHeader
              workspace={currentWorkspace}
              members={members || []}
              notifications={notifications || []}
              onEdit={handleEditWorkspace}
              onSwitch={handleSwitchWorkspace}
              onStartChat={onStartChat}
            />
          )}

          {/* Quick Actions */}
          <QuickActionsGrid
            onStartChat={onStartChat}
            onEditWorkspace={handleEditWorkspace}
          />

          {/* Workspace Overview */}
          <Grid container spacing={3}>
            {/* Team Members */}
            <Grid item xs={12} md={6}>
              <TeamMembersCard
                members={members || []}
                isLoading={isLoading}
                onInviteMember={() => console.log('Invite member')}
              />
            </Grid>

            {/* Recent Activity */}
            <Grid item xs={12} md={6}>
              <RecentActivityCard
                notifications={notifications || []}
                isLoading={isLoading}
              />
            </Grid>
          </Grid>

          {/* Workspace Profile Setup Prompt */}
          {currentWorkspace && !currentWorkspace.profile?.brand_name && (
            <Paper 
              elevation={2} 
              sx={{ 
                p: 3, 
                mt: 4, 
                borderRadius: 3,
                bgcolor: 'info.light',
                color: 'info.contrastText'
              }}
            >
              <Stack direction="row" alignItems="center" spacing={2}>
                <BusinessIcon sx={{ fontSize: 32 }} />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h6" fontWeight="bold" sx={{ mb: 1 }}>
                    Complete Your Workspace Profile
                  </Typography>
                  <Typography variant="body2">
                    Set up your brand information to get better AI recommendations and personalized marketing insights.
                  </Typography>
                </Box>
                <Button
                  variant="contained"
                  onClick={handleEditWorkspace}
                  sx={{ bgcolor: 'info.dark', '&:hover': { bgcolor: 'info.main' } }}
                >
                  Setup Profile
                </Button>
              </Stack>
            </Paper>
          )}
        </Container>

        {/* Workspace Profile Modal */}
        {currentWorkspace && (
          <WorkspaceProfileModal
            isOpen={showProfileModal}
            onClose={() => setShowProfileModal(false)}
            workspace={currentWorkspace}
            onProfileUpdated={handleProfileUpdated}
          />
        )}
      </AppLayout>
 
  );
}

