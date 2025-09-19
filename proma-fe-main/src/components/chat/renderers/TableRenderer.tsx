'use client';

import {
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper,
  Typography
} from '@mui/material';

interface TableRendererProps {
  content: string;
}
//TODO: USING libary to make color for table
// Parser cho bảng Markdown tiêu chuẩn
const parseMarkdownTable = (markdown: string) => {
  const lines = markdown.trim().split('\n').filter(line => line.includes('|'));
  if (lines.length < 2) return { headers: [], data: [] };

  const headerLine = lines[0];
  const dataLines = lines.slice(2);

  const headers = headerLine.split('|').map(h => h.trim()).filter(Boolean);
  const data = dataLines.map(line => 
    line.split('|').map(cell => cell.trim()).filter(Boolean)
  );

  return { headers, data };
};

// Parser cho bảng phức tạp dùng ||
const parseComplexTable = (text: string) => {
  const rows = text.trim().split('||').map(row => row.trim()).filter(Boolean);
  const tableData = rows.map(row => row.split('|').map(cell => cell.trim()).filter(Boolean));

  // Giả sử cột đầu tiên là tiêu đề hàng, các cột còn lại là dữ liệu
  const headers = tableData[0] || [];
  const data = tableData.slice(1);

  return { headers, data };
};

export default function TableRenderer({ content }: TableRendererProps) {
  // Quyết định dùng parser nào
  const isComplex = content.includes('||');
  const { headers, data } = isComplex ? parseComplexTable(content) : parseMarkdownTable(content);

  if (headers.length === 0) return <Typography>Không thể hiển thị bảng.</Typography>;

  // Nếu là bảng phức tạp, render theo cấu trúc hàng (tiêu đề + nội dung)
  if (isComplex) {
    return (
      <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
        <Table size="small">
          <TableHead sx={{ bgcolor: 'grey.100' }}>
            <TableRow>
              {headers.map((header, index) => (
                <TableCell key={index} sx={{ fontWeight: 'bold' }}>{header}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row, rowIndex) => (
              <TableRow key={rowIndex}>
                {row.map((cell, cellIndex) => (
                  <TableCell key={cellIndex} sx={{ fontWeight: cellIndex === 0 ? 'bold' : 'normal' }}>
                    {cell}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }

  // Render bảng Markdown tiêu chuẩn
  return (
    <TableContainer component={Paper} elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
      <Table size="small">
        <TableHead sx={{ bgcolor: 'grey.100' }}>
          <TableRow>
            {headers.map((header, index) => (
              <TableCell key={index} sx={{ fontWeight: 'bold' }}>{header}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row, rowIndex) => (
            <TableRow key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <TableCell key={cellIndex}>{cell}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
