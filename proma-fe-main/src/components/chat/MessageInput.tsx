// file: src/components/chat/MessageInput.tsx
'use client';

import { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Stack,
  Typography
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

interface MessageInputProps {
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
}

export default function MessageInput({ onSendMessage, isLoading }: MessageInputProps) {
  const [inputMessage, setInputMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const messageToSend = inputMessage;
    setInputMessage(''); // Clear input immediately
    await onSendMessage(messageToSend);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 3, 
        borderTop: 1, 
        borderColor: 'divider',
        bgcolor: 'background.paper'
      }}
    >
      <Box component="form" onSubmit={handleSubmit}>
        <Stack direction="row" spacing={2} alignItems="flex-end">
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Hỏi tôi về chiến lược marketing Facebook, targeting khách hàng, tối ưu quảng cáo..."
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
                bgcolor: 'background.default'
              }
            }}
            onKeyDown={handleKeyDown}
          />
          <IconButton
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              width: 48,
              height: 48,
              '&:hover': {
                bgcolor: 'primary.dark'
              },
              '&:disabled': {
                bgcolor: 'action.disabled',
                color: 'action.disabled'
              }
            }}
          >
            <SendIcon />
          </IconButton>
        </Stack>
      </Box>
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, textAlign: 'center' }}>
        Nhấn Enter để gửi, Shift+Enter để xuống dòng
      </Typography>
    </Paper>
  );
}