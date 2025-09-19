// file: src/hooks/useContentPlan.ts
'use client';

import { useState, useEffect, useCallback } from 'react';
import { ContentPlanItem, CreateContentPlanItemRequest } from '@/libs/types'; // Cập nhật đường dẫn
import { contentPlanService } from '@/services/content-plan.service'; // Cập nhật đường dẫn
import { ApiError } from '@/libs/utils/ApiError';


export function useContentPlan() {
  const [planItems, setPlanItems] = useState<ContentPlanItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchPlans = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      // Service mới trả về trực tiếp mảng dữ liệu
      const items = await contentPlanService.getContentPlans({ limit: 50 });
      setPlanItems(items.data); // Giả sử response là { data: items }
    } catch (err) {
      console.error('Failed to load content plans:', err);
      if (err instanceof ApiError) {
        setError(err.body?.message || 'Failed to load content plans.');
      } else if (err instanceof Error) {
        setError(err.message);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlans();
  }, [fetchPlans]);

  const createPlanItem = async (newItemData: CreateContentPlanItemRequest) => {
    try {
      const newItem = await contentPlanService.createContentPlan(newItemData);
      // Cập nhật state một cách lạc quan (optimistic update)
      setPlanItems(prev => [...prev, newItem]);
    } catch (err) {
      console.error('Failed to create content plan item:', err);
      // Ném lỗi ra để component UI có thể bắt và hiển thị thông báo
      throw err;
    }
  };

  const deletePlanItem = async (itemId: string) => {
    try {
      await contentPlanService.deleteContentPlan(itemId);
      // Cập nhật UI sau khi xóa thành công
      setPlanItems(prev => prev.filter(item => item.id !== itemId));
    } catch (err) {
      console.error('Failed to delete content plan item:', err);
      throw err;
    }
  };
  
  return {
    planItems,
    isLoading,
    error,
    fetchPlans, // Export ra để có thể refresh thủ công
    createPlanItem,
    deletePlanItem,
  };
}