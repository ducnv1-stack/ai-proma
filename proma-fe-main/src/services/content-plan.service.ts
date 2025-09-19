// file: services/contentPlan.service.ts

import  { webApiClient } from '../libs/utils/apiClient';
import { 
  ContentPlanItem, 
  CreateContentPlanItemRequest, 
  UpdateContentPlanItemRequest,
} from '../libs/types/content-plan.types';
import { ContentPlanQueryParams, PaginatedApiResponse, ApiResponse } from '../libs/types/common.types';
import { buildQueryParams } from '@/helpers/BuildQueryParams';


class ContentPlanService {

  // Lấy danh sách content plan với các bộ lọc
  public getContentPlans(params?: ContentPlanQueryParams): Promise<PaginatedApiResponse<ContentPlanItem>> {
    const queryString = params ? buildQueryParams(params) : '';
    const endpoint = `/content-plans${queryString ? `?${queryString}` : ''}`;
    return webApiClient<PaginatedApiResponse<ContentPlanItem>>(endpoint);
  }

  // Lấy content plan theo ID
  public getContentPlanById(id: string): Promise<ContentPlanItem> {
    // Giả sử API trả về trực tiếp ContentPlanItem, không bọc trong ApiResponse
    return webApiClient<ContentPlanItem>(`/content-plans/${id}`);
  }

  // Tạo content plan mới
  public createContentPlan(data: CreateContentPlanItemRequest): Promise<ContentPlanItem> {
    return webApiClient<ContentPlanItem>('/content-plans', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Cập nhật content plan
  public updateContentPlan(id: string, data: UpdateContentPlanItemRequest): Promise<ContentPlanItem> {
    return webApiClient<ContentPlanItem>(`/content-plans/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Xóa content plan
  public deleteContentPlan(id: string): Promise<void> {
    // API xóa thường trả về status 204 No Content, webApiClient sẽ xử lý trả về null/void
    return webApiClient<void>(`/content-plans/${id}`, {
      method: 'DELETE',
    });
  }

  // --- Admin endpoints ---

  public getContentPlansByStatus(status: string, params?: { limit?: number; offset?: number }): Promise<PaginatedApiResponse<ContentPlanItem>> {
    const queryString = params ? buildQueryParams(params) : '';
    const endpoint = `/api/admin/content-plans/status/${status}${queryString ? `?${queryString}` : ''}`;
    return webApiClient<PaginatedApiResponse<ContentPlanItem>>(endpoint);
  }

  public getScheduledContentPlans(limit?: number): Promise<PaginatedApiResponse<ContentPlanItem[]>> {
    const params = limit ? { limit } : {};
    const queryString = buildQueryParams(params);
    const endpoint = `/api/admin/content-plans/scheduled${queryString ? `?${queryString}` : ''}`;
    return webApiClient<PaginatedApiResponse<ContentPlanItem[]>>(endpoint);
  }

  public markAsPublished(id: string, publishPostId: string): Promise<void> {
    return webApiClient<void>(`/api/admin/content-plans/${id}/publish`, {
      method: 'POST',
      body: JSON.stringify({ publish_post_id: publishPostId }),
    });
  }
}

export const contentPlanService = new ContentPlanService();
export default contentPlanService;