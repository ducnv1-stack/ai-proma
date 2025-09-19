'use client';

import { useEffect, useState, useMemo } from 'react';
import { Typography } from '@mui/material';
import { parseMessageContent, ParsedMessage } from '@/libs/utils/messageParser';
import JsonRenderer from './renderers/JsonRenderer';
import MarkdownRenderer from './renderers/MarkdownRenderer';
import TableRenderer from './renderers/TableRenderer';

interface MessageContentProps {
  content: string;
}

export default function MessageContent({ content }: MessageContentProps) {
  // Chỉ parse lại khi content thay đổi
  const parsedContent = useMemo(() => parseMessageContent(content), [content]);

  switch (parsedContent.type) {
    case 'json':
      return <JsonRenderer data={parsedContent.content} />;
    case 'table':
      return <TableRenderer content={parsedContent.content} />;
    case 'markdown':
      return <MarkdownRenderer content={parsedContent.content} />;
    case 'text':
    default:
      return (
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
          {parsedContent.content}
        </Typography>
      );
  }
}
