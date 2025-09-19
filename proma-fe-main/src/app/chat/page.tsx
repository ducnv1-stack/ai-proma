// file: src/app/chat/page.tsx
'use client';

import { Box, CircularProgress, Stack, Typography } from '@mui/material';

import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/providers/ProtectedRoute';
import { useChat } from '@/hooks/useChat';
import MessageList from '@/components/chat/MessageList';  
import MessageInput from '@/components/chat/MessageInput';
import ChatHistory from '@/components/chat/ChatHistory'; // Import ChatHistory component


function ChatPageContent() {
  const {
    messages,
    isLoading,
    isInitializing,
    sendMessage,
    chatSessions, // Add chatSessions to the destructured props
    loadChatSession, // Add loadChatSession to the destructured props
    isHistoryLoading, // Add isHistoryLoading to the destructured props
  } = useChat();

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };
  
  if (isInitializing) {
    return (
      <Box sx={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Stack spacing={3} alignItems="center">
          <CircularProgress />
          <Typography variant="h5">Initializing Chat...</Typography>
        </Stack>
      </Box>
    );
  }

  return (
    <AppLayout 
      title="AI Marketing Assistant"
      headerActions={(
        <ChatHistory 
          sessions={chatSessions}
          onSelectSession={loadChatSession}
          isLoading={isHistoryLoading}
        />
      )}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <MessageList messages={messages} isLoading={isLoading} />
        <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </Box>
    </AppLayout>
  );
}


export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatPageContent />
    </ProtectedRoute>
  );
}