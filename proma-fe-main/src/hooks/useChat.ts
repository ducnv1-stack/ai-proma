// file: src/hooks/useChat.ts
'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { aiService } from '@/services/AI.service';
import { User, FunctionCall, Message } from '@/libs/types';
import { ChatSession } from '@/components/chat/ChatHistory';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const router = useRouter();
  const didInitialize = useRef(false);
  const aiMessageIdRef = useRef<string | null>(null);
  const thinkingStepsRef = useRef<FunctionCall[]>([]); // Dùng ref để lưu các bước suy nghĩ

  const initialize = useCallback(async () => {
    setIsInitializing(true);
    try {
      // Check workspace
      if (!localStorage.getItem('famarex_workspace')) {
        router.push('/workspace');
        return;
      }
      // Load user data
      const cachedUser = localStorage.getItem('famarex_user');
      if (cachedUser) {
        const user = JSON.parse(cachedUser);
        setCurrentUser(user);
        await aiService.createSession(user.id, user.name);
      } else {
        // Nếu không có user, không thể chat -> quay về login
        router.push('/login');
        return;
      }

      // Load history
      const historyData = await aiService.getChatHistory();
      if (historyData.sessions && Array.isArray(historyData.sessions)) {
        const transformedSessions: ChatSession[] = historyData.sessions.map((session: any) => ({
          ...session,
          timestamp: new Date(session.create_time),
          title: session.title || `Chat from ${new Date(session.create_time).toLocaleDateString()}`
        }));
        setChatSessions(transformedSessions);
      }
      
      // Welcome message
      setMessages([{
        id: 'welcome_' + Date.now(),
        content: 'Xin chào! Tôi là Famarex. Tôi có thể giúp bạn tối ưu hóa chiến dịch quảng cáo Facebook như thế nào?',
        sender: 'ai',
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Failed to initialize chat:', error);
    } finally {
      setIsInitializing(false);
    }
  }, [router]);

  useEffect(() => {
    if (didInitialize.current) {
      return;
    }
    didInitialize.current = true;
    
    // Chạy logic khởi tạo
    initialize();
  }, [initialize]);
  
  const loadChatSession = async (sessionId: string) => {
    setIsHistoryLoading(true);
    setMessages([]); // Clear previous messages
    try {
      const eventData = await aiService.getSessionEvents(sessionId);
      if (eventData && eventData.events) {
        const loadedMessages: Message[] = [];
        let pendingThinkingSteps: FunctionCall[] = [];

        // The events are in reverse chronological order, so we process them forwards.
        for (const event of [...eventData.events].reverse()) {
          try {
            const sender: 'user' | 'ai' = event.author === 'user' ? 'user' : 'ai';
            const contentData = JSON.parse(event.content);
            const parts = contentData.parts || [];

            let messageText = '';
            let functionCalls: FunctionCall[] = [];

            for (const part of parts) {
              if (part.text) {
                messageText += part.text;
              }
              if (part.function_call) {
                functionCalls.push(part.function_call);
              }
              // We don't process function_response as a separate message,
              // as it's part of the AI's internal thought process which results in the next text message.
            }

            if (functionCalls.length > 0) {
              // If we find function calls, store them. They will be attached to the *next* AI text message.
              pendingThinkingSteps.push(...functionCalls);
            }

            if (messageText) {
              const newMessage: Message = {
                id: event.id,
                content: messageText,
                sender,
                timestamp: new Date(event.timestamp),
                type: 'message', // Fix: Changed from 'event' to 'message'
              };

              // If this is an AI message and we have pending thinking steps, attach them.
              if (sender === 'ai' && pendingThinkingSteps.length > 0) {
                newMessage.thinkingSteps = pendingThinkingSteps;
                pendingThinkingSteps = []; // Clear the pending steps
              }
              
              loadedMessages.push(newMessage);
            }

          } catch (e) {
            console.error('Failed to parse event content:', event.content, e);
          }
        }

        setMessages(loadedMessages);
        aiService.setCurrentSession(sessionId);
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    } finally {
      setIsHistoryLoading(false);
    }
  };
  
  const sendMessage = async (messageContent: string) => {
    if (!messageContent.trim() || isLoading) return;

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      content: messageContent,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // 2. BẬT TRẠNG THÁI LOADING
    setIsLoading(true);

    aiMessageIdRef.current = null;
    thinkingStepsRef.current = []; // Reset các bước suy nghĩ

    try {
      // Dùng ref để lưu trữ ID của tin nhắn AI sẽ được tạo

      const handleFunctionCall = (functionCallData: FunctionCall) => {
        setMessages(prevMessages => {
          // If this is the first function call, CREATE a new AI message to show the thinking display
          if (aiMessageIdRef.current === null) {
            aiMessageIdRef.current = `ai_${Date.now()}`;
            const newAiMessage: Message = {
              id: aiMessageIdRef.current,
              content: '', // Start with empty content
              sender: 'ai',
              timestamp: new Date(),
              thinkingSteps: [functionCallData], // Add the first step
            };
            return [...prevMessages, newAiMessage];
          }
          // If it's a subsequent function call, UPDATE the existing AI message
          else {
            return prevMessages.map(msg =>
              msg.id === aiMessageIdRef.current
                ? { ...msg, thinkingSteps: [...(msg.thinkingSteps || []), functionCallData] }
                : msg
            );
          }
        });
      };

      const handleNewChunk = (textChunk: string) => {
        setMessages(prevMessages => {
          // If there was no function call, we still need to create the message bubble on the first chunk.
          if (aiMessageIdRef.current === null) {
            aiMessageIdRef.current = `ai_${Date.now()}`;
            const newAiMessage: Message = {
              id: aiMessageIdRef.current,
              content: textChunk,
              sender: 'ai',
              timestamp: new Date(),
              thinkingSteps: [],
            };
            return [...prevMessages, newAiMessage];
          } 
          // Append text to the existing AI message
          else {
            return prevMessages.map(msg => 
              msg.id === aiMessageIdRef.current
                ? { ...msg, content: msg.content + textChunk }
                : msg
            );
          }
        });
      };

      const handleStreamEnd = () => {
        setIsLoading(false); // Tắt loading khi stream kết thúc
      };

      const handleStreamError = (error: Error) => {
        // Có thể thêm một tin nhắn báo lỗi vào đây nếu muốn
        setIsLoading(false);
      };

      await aiService.sendMessage(
        { message: messageContent, userId: currentUser!.id },
        handleNewChunk,
        handleFunctionCall,
        () => {}, // Bỏ qua function response
        handleStreamEnd,
        handleStreamError
      );

    } catch (error) {
      console.error('Failed to send message:', error);
      setIsLoading(false); // Đảm bảo tắt loading nếu có lỗi ngay từ đầu
    }
  };
  
  const startNewChat = () => {
    aiService.resetSession();
    initialize(); // Khởi tạo lại toàn bộ
  };

  return {
    messages,
    inputMessage,
    setInputMessage,
    isLoading,
    isInitializing,
    isHistoryLoading,
    currentUser,
    chatSessions,
    sendMessage,
    startNewChat,
    loadChatSession,
  };
}