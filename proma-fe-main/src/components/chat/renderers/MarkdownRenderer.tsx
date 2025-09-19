'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Box, Paper } from '@mui/material';

interface MarkdownRendererProps {
  content: string;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <Box 
      className="markdown-body"
      sx={{
        fontSize: '0.9rem',
        lineHeight: 1.7,
        '& p': { margin: '0 0 12px 0' },
        '& h1, & h2, & h3': { marginTop: '16px', marginBottom: '8px', borderBottom: '1px solid #eee', paddingBottom: '4px' },
        '& ul, & ol': { paddingLeft: '24px', margin: '0 0 12px 0' },
        '& li': { marginBottom: '4px' },
        '& pre': { 
          backgroundColor: 'grey.100', 
          padding: '12px', 
          borderRadius: '8px', 
          overflowX: 'auto' 
        },
        '& blockquote': {
          borderLeft: '4px solid #ddd',
          paddingLeft: '12px',
          color: 'grey.700',
          margin: '0 0 12px 0'
        }
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code(props) {
            const { children, className, node, ...rest } = props;
            const match = /language-(\w+)/.exec(className || '');
            const inline = !match;

            if (!inline) {
              return (
                <Paper elevation={0} sx={{ p: 2, bgcolor: 'grey.100', overflowX: 'auto' }}>
                  <code style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }} {...rest}>
                    {children}
                  </code>
                </Paper>
              );
            }
            return (
              <code 
                style={{ 
                  backgroundColor: '#f0f0f0', 
                  padding: '2px 6px', 
                  borderRadius: '4px', 
                  fontFamily: 'monospace'
                }}
                {...rest}
              >
                {children}
              </code>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </Box>
  );
}
