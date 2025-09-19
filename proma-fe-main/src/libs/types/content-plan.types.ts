// Content Plan Management types

export interface ContentPlan {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  status: 'draft' | 'active' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface ContentPlanItem {
  id: string;
  task_date: string;
  last_updated_date: string;
  channel_id: string;
  title: string;
  descript_content: string;
  media_url?: string;
  status: 'draft' | 'scheduled' | 'published' | 'cancelled' | 'failed';
  publish_post_id?: string;
  meta_data?: string;
  user_id: string;
  publish_time: string;
  product: string;
  target_customer: string;
  goals: string;
  article_route?: string;
  channel_type: 'social_media' | 'blog' | 'email' | 'video' | 'website' | 'newsletter' | 'podcast' | 'webinar';
}

export interface CreateContentPlanRequest {
  name: string;
  description?: string;
  workspace_id: string;
}

export interface UpdateContentPlanRequest {
  name?: string;
  description?: string;
  status?: 'draft' | 'active' | 'completed' | 'archived';
}

export interface CreateContentPlanItemRequest {
  task_date: string;
  channel_id: string;
  title: string;
  descript_content: string;
  media_url?: string;
  status: 'draft' | 'scheduled' | 'published' | 'cancelled' | 'failed';
  meta_data?: string;
  publish_time: string;
  product: string;
  target_customer: string;
  goals: string;
  article_route?: string;
  channel_type: 'social_media' | 'blog' | 'email' | 'video' | 'website' | 'newsletter' | 'podcast' | 'webinar';
}

export interface UpdateContentPlanItemRequest {
  task_date?: string;
  channel_id?: string;
  title?: string;
  descript_content?: string;
  media_url?: string;
  status?: 'draft' | 'scheduled' | 'published' | 'cancelled' | 'failed';
  meta_data?: string;
  publish_time?: string;
  product?: string;
  target_customer?: string;
  goals?: string;
  article_route?: string;
  channel_type?: 'social_media' | 'blog' | 'email' | 'video' | 'website' | 'newsletter' | 'podcast' | 'webinar';
}

export interface ContentPlanFilters {
  status?: string[];
  channel_type?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  producer?: string;
  target_source?: string;
}

export interface ContentPlanStats {
  total: number;
  draft: number;
  scheduled: number;
  published: number;
  cancelled: number;
}

export interface ShareContentPlanRequest {
  plan_id: string;
  user_emails: string[];
  permission: 'view' | 'edit';
}

export interface ExportContentPlanRequest {
  plan_id: string;
  format: 'excel' | 'csv';
  include_filters?: {
    date_range?: {
      start: string;
      end: string;
    };
    platforms?: string[];
    status?: string[];
  };
}
