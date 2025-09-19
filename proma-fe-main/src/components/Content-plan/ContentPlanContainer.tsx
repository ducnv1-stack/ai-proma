// file: src/components/Content-plan/ContentPlanContainer.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import { ContentPlanItem } from '@/libs/types';
import { useContentPlan } from '@/hooks/useContentPlan';
import ContentPlanView from './ContentPlanView';

export default function ContentPlanContainer() {
  const {
    planItems,
    isLoading,
    error,
    createPlanItem,
    deletePlanItem,
    fetchPlans
  } = useContentPlan();

  const [mounted, setMounted] = useState(false);
  
  // Modals state
  const [showCreateItem, setShowCreateItem] = useState(false);
  const [showShareDialog, setShowShareDialog] = useState(false);

  // Handle client-side mounting
  useEffect(() => {
    setMounted(true);
  }, []);

  const handleAddContent = async (newItem: Partial<ContentPlanItem>) => {
    try {
      const createRequest = {
        task_date: newItem.task_date || new Date().toISOString().split('T')[0],
        channel_id: newItem.channel_id || '',
        title: newItem.title || '',
        descript_content: newItem.descript_content || '',
        media_url: newItem.media_url || '',
        status: newItem.status || 'draft' as const,
        meta_data: newItem.meta_data || '',
        publish_time: newItem.publish_time || new Date().toISOString(),
        product: newItem.product || '',
        target_customer: newItem.target_customer || '',
        goals: newItem.goals || '',
        article_route: newItem.article_route || '',
        channel_type: newItem.channel_type || 'blog' as const
      };

      await createPlanItem(createRequest);
      setShowCreateItem(false);
    } catch (error) {
      console.error('Failed to create content plan:', error);
      throw error;
    }
  };

  const handleEditItem = (item: ContentPlanItem) => {
    console.log('Edit item:', item);
    // TODO: Implement edit functionality with API
  };

  const handleDeleteItem = async (item: ContentPlanItem) => {
    try {
      await deletePlanItem(item.id);
    } catch (error) {
      console.error('Failed to delete content plan:', error);
      throw error;
    }
  };

  const handleImportItems = (importedItems: ContentPlanItem[]) => {
    // TODO: Implement import functionality
    console.log('Import items:', importedItems);
  };

  const handleShare = (email: string, permission: string, message: string) => {
    console.log('Share with:', { email, permission, message });
    // TODO: Implement sharing functionality
    setShowShareDialog(false);
  };

  const handleOpenCreateModal = () => setShowCreateItem(true);
  const handleCloseCreateModal = () => setShowCreateItem(false);
  const handleOpenShareModal = () => setShowShareDialog(true);
  const handleCloseShareModal = () => setShowShareDialog(false);

  return (
    <ContentPlanView
      // Data
      planItems={planItems}
      isLoading={isLoading}
      error={error}
      mounted={mounted}
      
      // Modal states
      showCreateItem={showCreateItem}
      showShareDialog={showShareDialog}
      
      // Event handlers
      onAddContent={handleAddContent}
      onEditItem={handleEditItem}
      onDeleteItem={handleDeleteItem}
      onImportItems={handleImportItems}
      onShare={handleShare}
      onOpenCreateModal={handleOpenCreateModal}
      onCloseCreateModal={handleCloseCreateModal}
      onOpenShareModal={handleOpenShareModal}
      onCloseShareModal={handleCloseShareModal}
    />
  );
}
