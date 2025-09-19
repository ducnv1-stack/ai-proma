'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import { Box, CircularProgress, Alert } from '@mui/material';
import { Workspace } from '@/libs/types';

// Dynamic imports to prevent hydration issues
const WorkspaceDashboard = dynamic(() => import('../../components/workspace/dashboard/WorkspaceDashboard'), {
  ssr: false,
  loading: () => (
    <Box 
      sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh' 
      }}
    >
      <CircularProgress size={48} />
    </Box>
  )
});

const WorkspaceModal = dynamic(() => import('../../components/workspace/WorkspaceModal'), {
  ssr: false
});

export default function WorkspacePage() {
  const [currentWorkspace, setCurrentWorkspace] = useState<Workspace | null>(null);
  const [showWorkspaceModal, setShowWorkspaceModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      checkAuthAndWorkspace();
    }
  }, [mounted]);

  const checkAuthAndWorkspace = () => {
    setIsLoading(true);
    setError('');

    try {
      // Check if user is authenticated
      const token = typeof window !== 'undefined' ? localStorage.getItem('famarex_token') : null;
      const user = typeof window !== 'undefined' ? localStorage.getItem('famarex_user') : null;

      if (!token || !user) {
        router.push('/login');
        return;
      }

      // Check if workspace is selected
      const workspaceData = typeof window !== 'undefined' ? localStorage.getItem('famarex_workspace') : null;
      if (workspaceData) {
        const workspace = JSON.parse(workspaceData);
        setCurrentWorkspace(workspace);
      } else {
        setShowWorkspaceModal(true);
      }
    } catch (error) {
      console.error('Error checking auth/workspace:', error);
      setError('Failed to load workspace data');
      router.push('/login');
    } finally {
      setIsLoading(false);
    }
  };

  const handleWorkspaceSelected = (workspace: Workspace) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('famarex_workspace', JSON.stringify(workspace));
    }
    setCurrentWorkspace(workspace);
    setShowWorkspaceModal(false);
  };

  const handleWorkspaceChange = () => {
    setShowWorkspaceModal(true);
  };

  const handleStartChat = () => {
    router.push('/chat');
  };

  // Don't render until mounted to prevent hydration mismatch
  if (!mounted) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}
      >
        <CircularProgress size={48} />
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}
      >
        <CircularProgress size={48} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ borderRadius: 2 }}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {currentWorkspace && (
        <WorkspaceDashboard
          workspace={currentWorkspace}
          onWorkspaceChange={handleWorkspaceChange}
          onStartChat={handleStartChat}
        />
      )}

      {/* Workspace Selection Modal */}
      {mounted && (
        <WorkspaceModal
          isOpen={showWorkspaceModal}
          onClose={() => setShowWorkspaceModal(false)}
          onWorkspaceSelected={handleWorkspaceSelected}
        />
      )}
    </Box>
  );
}
