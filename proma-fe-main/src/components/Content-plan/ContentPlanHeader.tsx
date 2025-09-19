// file: src/components/Content-plan/ContentPlanHeader.tsx
'use client';

import {
  Box,
  Typography,
  Button,
  Stack
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';

interface ContentPlanHeaderProps {
  onOpenCreateModal: () => void;
}

export default function ContentPlanHeader({ onOpenCreateModal }: ContentPlanHeaderProps) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
      <Box>
        <Typography variant="h4" fontWeight="bold" sx={{ mb: 1 }}>
          Content Plan Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Quản lý và theo dõi kế hoạch nội dung marketing
        </Typography>
      </Box>
      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={onOpenCreateModal}
        sx={{ borderRadius: 2 }}
      >
        Thêm Nội Dung
      </Button>
    </Stack>
  );
}
