'use client';

import { useState, useEffect } from 'react';
import { Button, Stack, Alert, Snackbar } from '@mui/material';
import { 
  FileDownload as ExportIcon, 
  FileUpload as ImportIcon, 
  Share as ShareIcon 
} from '@mui/icons-material';
import { ContentPlanItem } from '@/libs/types';

interface ContentPlanActionsProps {
  planItems: ContentPlanItem[];
  onImport: (items: ContentPlanItem[]) => void;
  onShare: () => void;
}

export default function ContentPlanActions({ planItems, onImport, onShare }: ContentPlanActionsProps) {
  const [mounted, setMounted] = useState(false);
  const [notification, setNotification] = useState<{ message: string; severity: 'success' | 'error' } | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleExportExcel = async () => {
    if (!mounted) return;
    
    try {
      const [{ default: XLSX }, { saveAs }] = await Promise.all([
        import('xlsx'),
        import('file-saver')
      ]);

      const exportData = planItems.map(item => ({
        'Ngày Task': item.task_date ? new Date(item.task_date).toLocaleDateString('vi-VN') : '',
        'Loại Kênh': item.channel_type || '',
        'ID Kênh': item.channel_id || '',
        'Trạng Thái': item.status || '',
        'Thời Gian Đăng': item.publish_time ? new Date(item.publish_time).toLocaleString('vi-VN') : '',
        'Tiêu Đề': item.title || '',
        'Mô Tả Nội Dung': item.descript_content || '',
        'Sản Phẩm': item.product || '',
        'Khách Hàng Mục Tiêu': item.target_customer || '',
        'Mục Tiêu': item.goals || '',
        'Media URL': item.media_url || '',
        'Article Route': item.article_route || '',
        'Cập Nhật Cuối': item.last_updated_date ? new Date(item.last_updated_date).toLocaleString('vi-VN') : ''
      }));

      const worksheet = XLSX.utils.json_to_sheet(exportData);
      const workbook = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(workbook, worksheet, 'Content Plan');

      const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
      const data = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      
      saveAs(data, `content-plan-${new Date().toISOString().split('T')[0]}.xlsx`);
      setNotification({ message: 'Xuất Excel thành công!', severity: 'success' });
    } catch (error) {
      console.error('Export Excel error:', error);
      setNotification({ message: 'Lỗi khi xuất Excel', severity: 'error' });
    }
  };

  const handleExportCSV = async () => {
    if (!mounted) return;
    
    try {
      const [{ default: Papa }, { saveAs }] = await Promise.all([
        import('papaparse'),
        import('file-saver')
      ]);

      const exportData = planItems.map(item => ({
        'Ngày Task': item.task_date ? new Date(item.task_date).toLocaleDateString('vi-VN') : '',
        'Loại Kênh': item.channel_type || '',
        'ID Kênh': item.channel_id || '',
        'Trạng Thái': item.status || '',
        'Thời Gian Đăng': item.publish_time ? new Date(item.publish_time).toLocaleString('vi-VN') : '',
        'Tiêu Đề': item.title || '',
        'Mô Tả Nội Dung': item.descript_content || '',
        'Sản Phẩm': item.product || '',
        'Khách Hàng Mục Tiêu': item.target_customer || '',
        'Mục Tiêu': item.goals || '',
        'Media URL': item.media_url || '',
        'Article Route': item.article_route || '',
        'Cập Nhật Cuối': item.last_updated_date ? new Date(item.last_updated_date).toLocaleString('vi-VN') : ''
      }));

      const csv = Papa.unparse(exportData);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      saveAs(blob, `content-plan-${new Date().toISOString().split('T')[0]}.csv`);
      setNotification({ message: 'Xuất CSV thành công!', severity: 'success' });
    } catch (error) {
      console.error('Export CSV error:', error);
      setNotification({ message: 'Lỗi khi xuất CSV', severity: 'error' });
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!mounted) return;
    
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls');
      
      if (isExcel) {
        const { default: XLSX } = await import('xlsx');
        const reader = new FileReader();
        
        reader.onload = (e) => {
          try {
            const data = new Uint8Array(e.target?.result as ArrayBuffer);
            const workbook = XLSX.read(data, { type: 'array' });
            const sheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet);
            
            const importedItems: ContentPlanItem[] = jsonData.map((row: any, index: number) => ({
              id: `imported_${Date.now()}_${index}`,
              task_date: String(row['Ngày Task'] || ''),
              channel_type: row['Loại Kênh'] || 'social_media',
              channel_id: String(row['ID Kênh'] || ''),
              status: row['Trạng Thái'] || 'draft',
              publish_time: String(row['Thời Gian Đăng'] || ''),
              title: String(row['Tiêu Đề'] || ''),
              descript_content: String(row['Mô Tả Nội Dung'] || ''),
              product: String(row['Sản Phẩm'] || ''),
              target_customer: String(row['Khách Hàng Mục Tiêu'] || ''),
              goals: String(row['Mục Tiêu'] || ''),
              media_url: row['Media URL'] ? String(row['Media URL']) : undefined,
              article_route: row['Article Route'] ? String(row['Article Route']) : undefined,
              last_updated_date: new Date().toISOString(),
              user_id: 'imported_user',
              meta_data: JSON.stringify({ imported: true, source: 'excel' })
            }));
            
            onImport(importedItems);
            setNotification({ message: `Nhập thành công ${importedItems.length} mục từ Excel!`, severity: 'success' });
          } catch (error) {
            console.error('Excel import error:', error);
            setNotification({ message: 'Lỗi khi đọc file Excel', severity: 'error' });
          }
        };
        
        reader.readAsArrayBuffer(file);
      } else if (file.name.endsWith('.csv')) {
        const { default: Papa } = await import('papaparse');
        const reader = new FileReader();
        
        reader.onload = (e) => {
          try {
            const csv = e.target?.result as string;
            const results = Papa.parse(csv, { header: true });
            
            const importedItems: ContentPlanItem[] = results.data.map((row: any, index: number) => ({
              id: `imported_${Date.now()}_${index}`,
              task_date: String(row['Ngày Task'] || ''),
              channel_type: row['Loại Kênh'] || 'social_media',
              channel_id: String(row['ID Kênh'] || ''),
              status: row['Trạng Thái'] || 'draft',
              publish_time: String(row['Thời Gian Đăng'] || ''),
              title: String(row['Tiêu Đề'] || ''),
              descript_content: String(row['Mô Tả Nội Dung'] || ''),
              product: String(row['Sản Phẩm'] || ''),
              target_customer: String(row['Khách Hàng Mục Tiêu'] || ''),
              goals: String(row['Mục Tiêu'] || ''),
              media_url: row['Media URL'] ? String(row['Media URL']) : undefined,
              article_route: row['Article Route'] ? String(row['Article Route']) : undefined,
              last_updated_date: new Date().toISOString(),
              user_id: 'imported_user',
              meta_data: JSON.stringify({ imported: true, source: 'csv' })
            }));
            
            onImport(importedItems);
            setNotification({ message: `Nhập thành công ${importedItems.length} mục từ CSV!`, severity: 'success' });
          } catch (error) {
            console.error('CSV import error:', error);
            setNotification({ message: 'Lỗi khi đọc file CSV', severity: 'error' });
          }
        };
        
        reader.readAsText(file);
      } else {
        setNotification({ message: 'Chỉ hỗ trợ file .xlsx, .xls, hoặc .csv', severity: 'error' });
      }
    } catch (error) {
      console.error('Import error:', error);
      setNotification({ message: 'Lỗi khi nhập file', severity: 'error' });
    }

    // Reset input
    event.target.value = '';
  };

  if (!mounted) {
    return null;
  }

  return (
    <>
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <Button
          variant="outlined"
          startIcon={<ExportIcon />}
          onClick={handleExportExcel}
          disabled={planItems.length === 0}
        >
          Xuất Excel
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<ExportIcon />}
          onClick={handleExportCSV}
          disabled={planItems.length === 0}
        >
          Xuất CSV
        </Button>
        
        <Button
          variant="outlined"
          component="label"
          startIcon={<ImportIcon />}
        >
          Nhập File
          <input
            type="file"
            hidden
            accept=".xlsx,.xls,.csv"
            onChange={handleImport}
          />
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<ShareIcon />}
          onClick={onShare}
        >
          Chia Sẻ
        </Button>
      </Stack>

      {/* Notification Snackbar */}
      <Snackbar
        open={!!notification}
        autoHideDuration={4000}
        onClose={() => setNotification(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setNotification(null)} 
          severity={notification?.severity}
          sx={{ width: '100%' }}
        >
          {notification?.message}
        </Alert>
      </Snackbar>
    </>
  );
}
