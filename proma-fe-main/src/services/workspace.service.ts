// file: services/workspace.service.ts

import {webApiClient}  from '../libs/utils/apiClient';
import {
  Workspace,
  WorkspaceProfile,
  WorkspaceMember,
  WorkspaceInvitation,
  WorkspaceNotification,
  CreateWorkspaceRequest,
  UpdateWorkspaceProfileRequest,
  InviteMemberRequest,
  TransferOwnershipRequest,
  ScrapCompanyProfileRequest,
  ApiResponse, // Giả sử bạn có kiểu ApiResponse chung
} from '../libs/types'; // Hoặc '../types/workspace.types'

class WorkspaceService {
  
  // --- Workspace CRUD ---

  public createWorkspace(request: CreateWorkspaceRequest): Promise<Workspace> {
    // Giả sử API trả về trực tiếp đối tượng Workspace
    return webApiClient<Workspace>('/workspaces', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  public getUserWorkspaces(): Promise<Workspace[]> {
    return webApiClient<Workspace[]>('/workspaces');
  }

  public getMyWorkspaces(): Promise<Workspace[]> {
    return webApiClient<Workspace[]>('/workspaces/my');
  }

  public getAllWorkspaces(): Promise<Workspace[]> {
    // Lưu ý: Cần đảm bảo user có quyền admin, backend sẽ kiểm tra
    return webApiClient<Workspace[]>('/workspaces/all');
  }

  public getWorkspaceById(workspaceId: string): Promise<Workspace> {
    return webApiClient<Workspace>(`/workspaces/${workspaceId}`);
  }

  // --- Workspace Profile ---

  public updateWorkspaceProfile(
    workspaceId: string, 
    request: UpdateWorkspaceProfileRequest
  ): Promise<{ message: string }> {
    return webApiClient<{ message: string }>(`/workspaces/${workspaceId}/profile`, {
      method: 'PUT',
      body: JSON.stringify(request),
    });
  }

  public scrapCompanyProfile(
    workspaceId: string, 
    request: ScrapCompanyProfileRequest
  ): Promise<WorkspaceProfile> {
    return webApiClient<WorkspaceProfile>(`/workspaces/${workspaceId}/profile/scrap-url`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // --- Workspace Members ---

  public getWorkspaceMembers(workspaceId: string): Promise<WorkspaceMember[]> {
    return webApiClient<WorkspaceMember[]>(`/workspaces/${workspaceId}/members`);
  }

  public inviteMember(
    workspaceId: string, 
    request: InviteMemberRequest
  ): Promise<{ message: string }> {
    return webApiClient<{ message: string }>(`/workspaces/${workspaceId}/invitations`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  public removeMember(
    workspaceId: string, 
    userId: string
  ): Promise<{ message: string }> {
    return webApiClient<{ message: string }>(`/workspaces/${workspaceId}/members/${userId}`, {
      method: 'DELETE',
    });
  }

  public transferOwnership(
    workspaceId: string, 
    request: TransferOwnershipRequest
  ): Promise<{ message: string }> {
    return webApiClient<{ message: string }>(`/workspaces/${workspaceId}/transfer-ownership`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // --- Invitations ---

  public getMyInvitations(): Promise<WorkspaceInvitation[]> {
    return webApiClient<WorkspaceInvitation[]>(`/workspaces/me/invitations`);
  }

  public acceptInvitation(invitationId: string): Promise<{ message: string }> {
    return webApiClient<{ message: string }>(`/workspaces/invitations/${invitationId}/accept`, {
      method: 'POST',
    });
  }

  public declineInvitation(invitationId: string): Promise<{ message: string }> {
    return webApiClient<{ message: string }>(`/workspaces/invitations/${invitationId}/decline`, {
      method: 'POST',
    });
  }
  
  // --- Notifications ---

  public getNotifications(): Promise<WorkspaceNotification[]> {
    return webApiClient<WorkspaceNotification[]>(`/workspaces/notifications`);
  }

  public markNotificationAsRead(notificationId: string): Promise<{ message: string }> {
    return webApiClient<{ message: string }>(`/workspaces/notifications/${notificationId}/read`, {
      method: 'POST',
    });
  }

  public markAllNotificationsAsRead(): Promise<{ message: string }> {
    return webApiClient<{ message: string }>(`/workspaces/notifications/mark-all-read`, {
      method: 'POST',
    });
  }
}

export const workspaceService = new WorkspaceService();