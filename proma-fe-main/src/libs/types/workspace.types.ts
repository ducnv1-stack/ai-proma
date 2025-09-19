// Workspace-related types and interfaces

export interface Workspace {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  owner_id: string;
  // Profile fields directly in workspace (flat structure)
  brand_name?: string;
  business_type?: string;
  default_language_code?: string;
  default_location_code?: string;
  brand_description?: string;
  brand_products_services?: string;
  website_url?: string;
  brand_logo_url?: string;
  // Keep profile for backward compatibility
  profile?: WorkspaceProfile;
}

export interface WorkspaceProfile {
  brand_name?: string;
  business_type?: string;
  default_language_code?: string;
  default_location_code?: string;
  brand_description?: string;
  brand_products_services?: string;
  website_url?: string;
  brand_logo_url?: string;
}

export interface WorkspaceMember {
  id: string;
  user_id: string;
  workspace_id: string;
  role: 'owner' | 'admin' | 'member';
  joined_at: string;
  user: {
    id: string;
    email: string;
    name?: string;
  };
}

export interface WorkspaceInvitation {
  id: string;
  workspace_id: string;
  invitee_email: string;
  role: 'admin' | 'member';
  status: 'pending' | 'accepted' | 'declined';
  invited_by: string;
  created_at: string;
  workspace: {
    name: string;
  };
}

export interface WorkspaceNotification {
  id: string;
  user_id: string;
  workspace_id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

// Request types
export interface CreateWorkspaceRequest {
  name: string;
  description?: string;
}

export interface UpdateWorkspaceProfileRequest {
  brand_name?: string;
  business_type?: string;
  default_language_code?: string;
  default_location_code?: string;
  brand_description?: string;
  brand_products_services?: string;
  website_url?: string;
  brand_logo_url?: string;
}

export interface InviteMemberRequest {
  invitee_email: string;
  role: 'admin' | 'member';
}

export interface TransferOwnershipRequest {
  new_owner_id: string;
}

export interface ScrapCompanyProfileRequest {
  website_url: string;
}
