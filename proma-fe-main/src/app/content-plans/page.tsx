'use client';

import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/providers/ProtectedRoute';
import ContentPlanContainer from '@/components/Content-plan/ContentPlanContainer';

function ContentPlanContent() {
  return (
    <AppLayout
      title="Content Plan Management" 
      subtitle="Quản lý kế hoạch nội dung"
    >
      <ContentPlanContainer />
    </AppLayout>
  );
}

export default function ContentPlanPage() {
  return (
    <ProtectedRoute>
      <ContentPlanContent />
    </ProtectedRoute>
  );
}
