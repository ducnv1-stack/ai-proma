// file: src/components/workspace/dashboard/TeamMembersCard.tsx
'use client';

import {
  Card,
  CardContent,
  Stack,
  Typography,
  Button,
  Avatar,
  Box,
  Chip,
  CircularProgress
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { WorkspaceMember } from '@/libs/types';

interface TeamMembersCardProps {
  members: WorkspaceMember[];
  isLoading: boolean;
  onInviteMember?: () => void;
}

export default function TeamMembersCard({ members, isLoading, onInviteMember }: TeamMembersCardProps) {
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
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
          <Typography variant="h6" fontWeight="bold">
            Team Members
          </Typography>
          <Button
            size="small"
            startIcon={<AddIcon />}
            onClick={onInviteMember || (() => console.log('Invite member'))}
          >
            Invite
          </Button>
        </Stack>
        <Stack spacing={2}>
          {Array.isArray(members) && members.slice(0, 5).map((member) => (
            <Stack key={member.id} direction="row" alignItems="center" spacing={2}>
              <Avatar sx={{ width: 32, height: 32 }}>
                {member.user.email.charAt(0).toUpperCase()}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" fontWeight="medium">
                  {member.user.name || member.user.email}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {member.user.email}
                </Typography>
              </Box>
              <Chip
                label={member.role}
                size="small"
                color={member.role === 'owner' ? 'primary' : 'default'}
                variant="outlined"
              />
            </Stack>
          ))}
          {Array.isArray(members) && members.length > 5 && (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', pt: 1 }}>
              +{members.length - 5} more members
            </Typography>
          )}
          {(!Array.isArray(members) || members.length === 0) && (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
              No team members yet
            </Typography>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}