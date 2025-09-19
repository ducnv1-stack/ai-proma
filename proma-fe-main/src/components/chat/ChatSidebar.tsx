// file: src/components/chat/ChatSidebar.tsx
'use client';

import {
  Box,
  Button,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  useTheme,
  useMediaQuery,
  Drawer
} from '@mui/material';
import {
  Add as AddIcon,
  Chat as ChatIcon
} from '@mui/icons-material';
import { ChatSession } from './ChatHistory';

interface ChatSidebarProps {
  sessions: ChatSession[];
  onNewChat: () => void;
  isLoading?: boolean;
}

export default function ChatSidebar({ sessions, onNewChat, isLoading = false }: ChatSidebarProps) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const sidebarContent = (
    <Box sx={{ width: 300, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* New Chat Button */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Button
          fullWidth
          variant="contained"
          startIcon={<AddIcon />}
          onClick={onNewChat}
          disabled={isLoading}
          sx={{ 
            py: 1.5,
            borderRadius: 3,
            textTransform: 'none',
            fontSize: '1rem',
            mb: 2
          }}
        >
          New Chat
        </Button>
        
        {sessions.length > 0 && (
          <>
            <Typography variant="subtitle2" sx={{ mb: 1, color: 'text.secondary' }}>
              Recent Chats
            </Typography>
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {sessions.slice(0, 10).map((session) => (
                <ListItem key={session.id} disablePadding>
                  <ListItemButton 
                    sx={{ 
                      borderRadius: 2, 
                      mb: 0.5,
                      '&:hover': {
                        bgcolor: 'action.hover'
                      }
                    }}
                  >
                    <ListItemIcon>
                      <ChatIcon color="action" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2" fontWeight="medium" noWrap>
                          {session.title}
                        </Typography>
                      }
                      secondary={
                        <Typography variant="caption" color="text.disabled">
                          {session.timestamp.toLocaleDateString()}
                        </Typography>
                      }
                    />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </>
        )}
      </Box>

      {/* Empty State */}
      {sessions.length === 0 && (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Chưa có cuộc trò chuyện nào
          </Typography>
          <Typography variant="caption" color="text.disabled">
            Bắt đầu chat mới để tương tác với AI
          </Typography>
        </Box>
      )}
    </Box>
  );

  if (isMobile) {
    // On mobile, this could be a drawer that opens/closes
    // For now, we'll render it normally but you can enhance this later
    return (
      <Paper 
        elevation={1} 
        sx={{ 
          width: 300, 
          height: '100%',
          borderRight: 1,
          borderColor: 'divider',
          bgcolor: 'background.paper'
        }}
      >
        {sidebarContent}
      </Paper>
    );
  }

  return (
    <Paper 
      elevation={1} 
      sx={{ 
        width: 300, 
        height: '100%',
        borderRight: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper'
      }}
    >
      {sidebarContent}
    </Paper>
  );
}
