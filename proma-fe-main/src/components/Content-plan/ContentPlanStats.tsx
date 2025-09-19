// file: src/components/Content-plan/ContentPlanStats.tsx
'use client';

import {
  Stack,
  Card,
  CardContent,
  Typography
} from '@mui/material';
import { ContentPlanItem } from '@/libs/types';

interface ContentPlanStatsProps {
  planItems: ContentPlanItem[];
}

export default function ContentPlanStats({ planItems }: ContentPlanStatsProps) {
  const totalItems = planItems.length;
  const publishedItems = planItems.filter(item => item.status === 'published').length;
  const scheduledItems = planItems.filter(item => item.status === 'scheduled').length;
  const draftItems = planItems.filter(item => item.status === 'draft').length;

  return (
    <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
      <Card sx={{ flex: 1 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">
            {totalItems}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Tổng nội dung
          </Typography>
        </CardContent>
      </Card>
      <Card sx={{ flex: 1 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">
            {publishedItems}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Đã đăng
          </Typography>
        </CardContent>
      </Card>
      <Card sx={{ flex: 1 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">
            {scheduledItems}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Đã lên lịch
          </Typography>
        </CardContent>
      </Card>
      <Card sx={{ flex: 1 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold">
            {draftItems}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Bản nháp
          </Typography>
        </CardContent>
      </Card>
    </Stack>
  );
}
