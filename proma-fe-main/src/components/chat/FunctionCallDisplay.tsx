'use client';

import { Paper, Typography, Stack, CircularProgress } from '@mui/material';
import { Build as BuildIcon } from '@mui/icons-material';
import { FunctionCall } from '@/libs/types';

interface FunctionCallDisplayProps {
  functionCall: FunctionCall;
}

export default function FunctionCallDisplay({ functionCall }: FunctionCallDisplayProps) {
  return (
    <Paper 
      elevation={1}
      sx={{
        p: 2,
        borderRadius: 3,
        border: 1,
        borderColor: 'divider',
        bgcolor: 'grey.100',
        maxWidth: '70%'
      }}
    >
      <Stack direction="row" spacing={2} alignItems="center">
        <CircularProgress size={20} />
        <Stack>
          <Typography variant="body2" fontWeight="bold">
            Đang sử dụng công cụ: {functionCall.function_name}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {functionCall.args.action_description || 'Đang thực thi...'}
          </Typography>
        </Stack>
      </Stack>
    </Paper>
  );
}
