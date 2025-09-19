'use client';

import JSONPretty from 'react-json-pretty';
import 'react-json-pretty/themes/monikai.css'; // Import một theme CSS
import { Box } from '@mui/material';

interface JsonRendererProps {
  data: object;
}

// Sử dụng react-json-pretty, tương thích với React 19 và không phụ thuộc MUI
export default function JsonRenderer({ data }: JsonRendererProps) {
  return (
    <Box sx={{ 
      bgcolor: '#272822', // Màu nền phù hợp với theme monikai
      p: 2, 
      borderRadius: 2, 
      fontSize: '0.875rem',
      overflowX: 'auto'
    }}>
      <JSONPretty 
        data={data}
        themeClassName="JSONPretty"
      />
    </Box>
  );
}
