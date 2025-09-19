// file: src/components/chat/MessageList.tsx
'use client';

import { useRef, useEffect } from 'react';
import {
  Box,
  Stack,
  Paper,
  Typography,
  Avatar,
  CircularProgress
} from '@mui/material';
import {
  AutoAwesome as SparklesIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { Message } from '@/libs/types';
import ThinkingDisplay from './ThinkingDisplay';
import MessageContent from './MessageContent';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <Box 
      sx={{ 
        flex: 1, 
        overflow: 'auto', 
        p: 3,
        bgcolor: 'grey.50'
      }}
    >
      {messages.length === 0 ? (
        <Box 
          sx={{ 
            height: '100%', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center' 
          }}
        >
          <Stack spacing={3} alignItems="center" sx={{ textAlign: 'center' }}>
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: 3,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <SparklesIcon sx={{ color: 'white', fontSize: 40 }} />
            </Box>
            <Typography variant="h5" fontWeight="bold">
              Chào mừng đến với Famarex!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Bắt đầu cuộc trò chuyện với AI Marketing Assistant
            </Typography>
          </Stack>
        </Box>
      ) : (
        <Stack spacing={3}>
          {messages.map((message) => (
            <Stack
              key={message.id}
              direction="row"
              spacing={2}
              sx={{
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              {message.sender === 'ai' && (
                <Avatar
                  sx={{
                    bgcolor: 'primary.main',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  }}
                >
                  <SparklesIcon />
                </Avatar>
              )}
              
              <Stack sx={{ width: '100%', maxWidth: '70%', alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start' }}>
                {message.sender === 'ai' && message.thinkingSteps && message.thinkingSteps.length > 0 && (
                  <ThinkingDisplay steps={message.thinkingSteps} />
                )}
                
                {message.content && (
                  <Paper
                    elevation={message.sender === 'user' ? 2 : 1}
                    sx={{
                      p: 2,
                      bgcolor: message.sender === 'user' ? 'primary.main' : 'background.paper',
                      color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                      borderRadius: 3,
                      ...(message.sender === 'user' && {
                        borderBottomRightRadius: 8
                      }),
                      ...(message.sender === 'ai' && {
                        borderBottomLeftRadius: 8
                      })
                    }}
                  >
                    <MessageContent content={message.content} />
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        display: 'block', 
                        mt: 1,
                        opacity: 0.7
                      }}
                    >
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </Typography>
                  </Paper>
                )}
              </Stack>

              {message.sender === 'user' && (
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <PersonIcon />
                </Avatar>
              )}
            </Stack>
          ))}
          
          {isLoading && (
            <Stack direction="row" spacing={2}>
              <Avatar
                sx={{
                  bgcolor: 'primary.main',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                }}
              >
                <SparklesIcon />
              </Avatar>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  borderRadius: 3,
                  borderBottomLeftRadius: 8,
                  bgcolor: 'background.paper'
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center">
                  <CircularProgress size={16} />
                  <Typography variant="body2" color="text.secondary">
                    AI đang suy nghĩ...
                  </Typography>
                </Stack>
              </Paper>
            </Stack>
          )}
        </Stack>
      )}
      <div ref={messagesEndRef} />
    </Box>
  );
}