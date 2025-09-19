// file: src/hooks/useWorkspaceDashboard.ts
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Workspace, WorkspaceMember, WorkspaceNotification } from '@/libs/types';
import { workspaceService } from '@/services/workspace.service';

export function useWorkspaceDashboard(initialWorkspace: Workspace) {
  const [workspace, setWorkspace] = useState<Workspace>(initialWorkspace);
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  const [notifications, setNotifications] = useState<WorkspaceNotification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const [membersRes, notificationsRes] = await Promise.all([
        workspaceService.getWorkspaceMembers(workspace.id),
        workspaceService.getNotifications() // Cân nhắc xem có nên filter theo workspaceId
      ]);
      setMembers(membersRes);
      setNotifications(notificationsRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setIsLoading(false);
    }
  }, [workspace.id]);

  useEffect(() => {
    setWorkspace(initialWorkspace);
    loadData();
  }, [initialWorkspace, loadData]);

  const handleProfileUpdated = (updatedWorkspace: Workspace) => {
    setWorkspace(updatedWorkspace);
    // Service nên tự xử lý việc cập nhật localStorage
    localStorage.setItem('famarex_workspace', JSON.stringify(updatedWorkspace));
  };
  
  // Trả về state và các hàm xử lý để component UI có thể sử dụng
  return {
    workspace,
    members,
    notifications,
    isLoading,
    error,
    handleProfileUpdated,
    reload: loadData // Cung cấp hàm để tải lại dữ liệu khi cần
  };
}