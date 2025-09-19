'use client';

import { useState } from 'react';
import { Button, Menu, MenuItem, ListItemIcon, ListItemText, CircularProgress } from '@mui/material';
import { History as HistoryIcon } from '@mui/icons-material';

// Define a type for the session object, based on what the API will return
export interface ChatSession {
  id: string; // Unique identifier for the session
  title: string; // The title of the chat, likely the first user message
  timestamp: Date; // The creation date as a Date object
  create_time: string; // The original timestamp string from the API
}

interface ChatHistoryProps {
  sessions: ChatSession[];
  onSelectSession: (sessionId: string) => void;
  isLoading: boolean;
}

export default function ChatHistory({ sessions, onSelectSession, isLoading }: ChatHistoryProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleSelect = (sessionId: string) => {
    onSelectSession(sessionId);
    handleClose();
  };

  return (
    <div>
      <Button
        variant="outlined"
        onClick={handleClick}
        startIcon={isLoading ? <CircularProgress size={20} /> : <HistoryIcon />}
        disabled={isLoading}
      >
        Chat History
      </Button>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'basic-button',
        }}
      >
        {sessions && sessions.length > 0 ? (
          sessions
            .filter(session => session && session.id)
            .map((session) => (
              <MenuItem key={session.id} onClick={() => handleSelect(session.id)}>
                <ListItemText 
                  primary={`Session ${session.id.substring(0, 8)}...`} 
                  secondary={new Date(session.create_time).toLocaleString()}
                />
              </MenuItem>
            ))
        ) : (
          <MenuItem disabled>No history found</MenuItem>
        )}
      </Menu>
    </div>
  );
}
