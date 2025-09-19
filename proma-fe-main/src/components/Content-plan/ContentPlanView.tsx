// file: src/components/Content-plan/ContentPlanView.tsx
'use client';

import {
  Box,
  Typography,
  Button,
  Stack,
  Card,
  CardContent,
  Fab,
  CircularProgress,
  Alert
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { ContentPlanItem } from '@/libs/types';
import ContentPlanDataGrid from './ContentPlanDataGrid';
import ContentPlanActions from './ContentPlanActions';
import { AddContentModal, ShareModal } from './ContentPlanModals';
import ContentPlanHeader from './ContentPlanHeader';
import ContentPlanStats from './ContentPlanStats';

interface ContentPlanViewProps {
  // Data
  planItems: ContentPlanItem[];
  isLoading: boolean;
  error: string;
  mounted: boolean;
  
  // Modal states
  showCreateItem: boolean;
  showShareDialog: boolean;
  
  // Event handlers
  onAddContent: (newItem: Partial<ContentPlanItem>) => Promise<void>;
  onEditItem: (item: ContentPlanItem) => void;
  onDeleteItem: (item: ContentPlanItem) => Promise<void>;
  onImportItems: (importedItems: ContentPlanItem[]) => void;
  onShare: (email: string, permission: string, message: string) => void;
  onOpenCreateModal: () => void;
  onCloseCreateModal: () => void;
  onOpenShareModal: () => void;
  onCloseShareModal: () => void;
}

export default function ContentPlanView({
  planItems,
  isLoading,
  error,
  mounted,
  showCreateItem,
  showShareDialog,
  onAddContent,
  onEditItem,
  onDeleteItem,
  onImportItems,
  onShare,
  onOpenCreateModal,
  onCloseCreateModal,
  onOpenShareModal,
  onCloseShareModal
}: ContentPlanViewProps) {
  // Don't render until mounted to prevent hydration mismatch
  if (!mounted) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress size={48} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {/* Header */}
      <ContentPlanHeader onOpenCreateModal={onOpenCreateModal} />

      {/* Action Buttons */}
      <ContentPlanActions
        planItems={planItems}
        onImport={onImportItems}
        onShare={onOpenShareModal}
      />

      {/* Stats Cards */}
      <ContentPlanStats planItems={planItems} />

      {/* Data Grid */}
      <ContentPlanDataGrid
        planItems={planItems}
        isLoading={isLoading}
        onEditItem={onEditItem}
        onDeleteItem={onDeleteItem}
      />

      {/* Mobile FAB */}
      <Fab
        color="primary"
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          display: { xs: 'flex', md: 'none' }
        }}
        onClick={onOpenCreateModal}
      >
        <AddIcon />
      </Fab>

      {/* Modals */}
      <AddContentModal
        open={showCreateItem}
        onClose={onCloseCreateModal}
        onAdd={onAddContent}
      />

      <ShareModal
        open={showShareDialog}
        onClose={onCloseShareModal}
        onShare={onShare}
      />
    </Box>
  );
}
