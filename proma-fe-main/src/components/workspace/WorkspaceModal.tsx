'use client';

import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  Stack,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  Avatar,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  Business as BusinessIcon,
  People as PeopleIcon,
  Notifications as NotificationsIcon,
  Check as CheckIcon,
  Cancel as CancelIcon,
  AutoAwesome as SparklesIcon
} from '@mui/icons-material';
import { workspaceService } from '../../services/workspace.service';
import { Workspace, WorkspaceInvitation } from '../../libs/types';

interface WorkspaceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onWorkspaceSelected: (workspace: Workspace) => void;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function WorkspaceModal({ isOpen, onClose, onWorkspaceSelected }: WorkspaceModalProps) {
  const [activeTab, setActiveTab] = useState(0);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [invitations, setInvitations] = useState<WorkspaceInvitation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  
  // Create workspace form
  const [workspaceName, setWorkspaceName] = useState('');
  const [workspaceDescription, setWorkspaceDescription] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const [workspacesResponse, invitationsResponse] = await Promise.all([
        workspaceService.getUserWorkspaces(),
        workspaceService.getMyInvitations()
      ]);
      
      setWorkspaces(workspacesResponse);
      setInvitations(invitationsResponse);
    } catch (error) {
      console.error('Failed to load workspace data:', error);
      setError(error instanceof Error ? error.message : 'Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!workspaceName.trim()) return;

    setIsCreating(true);
    setError('');

    try {
      const response = await workspaceService.createWorkspace({
        name: workspaceName.trim(),
        description: workspaceDescription.trim() || undefined
      });

      onWorkspaceSelected(response);
      onClose();
    } catch (error) {
      console.error('Failed to create workspace:', error);
      setError(error instanceof Error ? error.message : 'Failed to create workspace');
    } finally {
      setIsCreating(false);
    }
  };

  const handleSelectWorkspace = (workspace: Workspace) => {
    onWorkspaceSelected(workspace);
    onClose();
  };

  const handleAcceptInvitation = async (invitationId: string) => {
    try {
      await workspaceService.acceptInvitation(invitationId);
      await loadData(); // Refresh data
    } catch (error) {
      console.error('Failed to accept invitation:', error);
      setError(error instanceof Error ? error.message : 'Failed to accept invitation');
    }
  };

  const handleDeclineInvitation = async (invitationId: string) => {
    try {
      await workspaceService.declineInvitation(invitationId);
      await loadData(); // Refresh data
    } catch (error) {
      console.error('Failed to decline invitation:', error);
      setError(error instanceof Error ? error.message : 'Failed to decline invitation');
    }
  };

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          p: 0,
          maxHeight: '90vh'
        }
      }}
    >
      <DialogTitle sx={{ p: 0 }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          p: 3,
          pb: 1
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
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
              <BusinessIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Box>
              <Typography variant="h5" fontWeight="bold">
                Select Workspace
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Choose or create your workspace to continue
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 3, pt: 1 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs 
            value={activeTab} 
            onChange={(_, newValue) => setActiveTab(newValue)}
            aria-label="workspace tabs"
          >
            <Tab 
              icon={<BusinessIcon />} 
              label="My Workspaces" 
              iconPosition="start"
            />
            <Tab 
              icon={<AddIcon />} 
              label="Create New" 
              iconPosition="start"
            />
            <Tab 
              icon={<NotificationsIcon />} 
              label={`Invitations ${invitations.length > 0 ? `(${invitations.length})` : ''}`}
              iconPosition="start"
            />
          </Tabs>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {/* My Workspaces Tab */}
        <TabPanel value={activeTab} index={0}>
          {workspaces.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <BusinessIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
                No workspaces found
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Create your first workspace to get started
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setActiveTab(1)}
              >
                Create Workspace
              </Button>
            </Box>
          ) : (
            <Grid container spacing={2}>
              {workspaces.map((workspace) => (
                <Grid item xs={12} sm={6} key={workspace.id}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        elevation: 4,
                        transform: 'translateY(-2px)'
                      }
                    }}
                    onClick={() => handleSelectWorkspace(workspace)}
                  >
                    <CardContent>
                      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                        <Avatar
                          sx={{
                            bgcolor: 'primary.main',
                            width: 40,
                            height: 40
                          }}
                        >
                          {workspace.name.charAt(0).toUpperCase()}
                        </Avatar>
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="h6" fontWeight="bold">
                            {workspace.name}
                          </Typography>
                          {workspace.description && (
                            <Typography variant="body2" color="text.secondary">
                              {workspace.description}
                            </Typography>
                          )}
                        </Box>
                      </Stack>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Chip 
                          size="small" 
                          label="Owner" 
                          color="primary" 
                          variant="outlined"
                        />
                        <Typography variant="caption" color="text.secondary">
                          Created {new Date(workspace.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </TabPanel>

        {/* Create New Workspace Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box component="form" onSubmit={handleCreateWorkspace}>
            <Stack spacing={3}>
              <Box sx={{ textAlign: 'center', mb: 2 }}>
                <SparklesIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                <Typography variant="h6" fontWeight="bold">
                  Create New Workspace
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Set up your workspace to organize your marketing campaigns
                </Typography>
              </Box>

              <TextField
                fullWidth
                label="Workspace Name"
                value={workspaceName}
                onChange={(e) => setWorkspaceName(e.target.value)}
                required
                disabled={isCreating}
                placeholder="e.g., My Marketing Agency"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2
                  }
                }}
              />

              <TextField
                fullWidth
                label="Description (Optional)"
                value={workspaceDescription}
                onChange={(e) => setWorkspaceDescription(e.target.value)}
                disabled={isCreating}
                multiline
                rows={3}
                placeholder="Describe your workspace and its purpose..."
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2
                  }
                }}
              />

              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={isCreating || !workspaceName.trim()}
                startIcon={isCreating ? <CircularProgress size={20} /> : <AddIcon />}
                sx={{
                  py: 1.5,
                  borderRadius: 2,
                  fontSize: '1rem',
                  fontWeight: 600
                }}
              >
                {isCreating ? 'Creating...' : 'Create Workspace'}
              </Button>
            </Stack>
          </Box>
        </TabPanel>

        {/* Invitations Tab */}
        <TabPanel value={activeTab} index={2}>
          {invitations.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <NotificationsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" sx={{ mb: 1 }}>
                No pending invitations
              </Typography>
              <Typography variant="body2" color="text.secondary">
                You'll see workspace invitations here when you receive them
              </Typography>
            </Box>
          ) : (
            <Stack spacing={2}>
              {invitations.map((invitation) => (
                <Card key={invitation.id} variant="outlined">
                  <CardContent>
                    <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                      <Avatar sx={{ bgcolor: 'secondary.main' }}>
                        {invitation.workspace.name.charAt(0).toUpperCase()}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" fontWeight="bold">
                          {invitation.workspace.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Invited as {invitation.role}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Invited on {new Date(invitation.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                      <Chip 
                        size="small" 
                        label={invitation.role} 
                        color="secondary" 
                        variant="outlined"
                      />
                    </Stack>
                  </CardContent>
                  <CardActions sx={{ px: 2, pb: 2 }}>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<CheckIcon />}
                      onClick={() => handleAcceptInvitation(invitation.id)}
                      sx={{ mr: 1 }}
                    >
                      Accept
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<CancelIcon />}
                      onClick={() => handleDeclineInvitation(invitation.id)}
                    >
                      Decline
                    </Button>
                  </CardActions>
                </Card>
              ))}
            </Stack>
          )}
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
}
