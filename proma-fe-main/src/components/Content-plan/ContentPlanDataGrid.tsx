'use client';

import { useState } from 'react';
import { Box, Chip, IconButton, Menu, MenuItem } from '@mui/material';
import { MoreVert as MoreIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { DataGrid, GridToolbar, GridColDef } from '@mui/x-data-grid';
import { ContentPlanItem } from '@/libs/types';

interface ContentPlanDataGridProps {
  planItems: ContentPlanItem[];
  isLoading: boolean;
  onEditItem: (item: ContentPlanItem) => void;
  onDeleteItem: (item: ContentPlanItem) => void;
}

export default function ContentPlanDataGrid({ 
  planItems, 
  isLoading, 
  onEditItem, 
  onDeleteItem 
}: ContentPlanDataGridProps) {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedItem, setSelectedItem] = useState<ContentPlanItem | null>(null);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, item: ContentPlanItem) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedItem(item);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedItem(null);
  };

  const handleEdit = () => {
    if (selectedItem) {
      onEditItem(selectedItem);
    }
    handleMenuClose();
  };

  const handleDelete = () => {
    if (selectedItem) {
      onDeleteItem(selectedItem);
    }
    handleMenuClose();
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'published': return 'success';
      case 'scheduled': return 'primary';
      case 'draft': return 'default';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'task_date',
      headerName: 'Ngày Task',
      width: 120,
      valueGetter: (value, row) => {
        try {
          return value ? new Date(value).toLocaleDateString('vi-VN') : '';
        } catch {
          return '';
        }
      }
    },
    {
      field: 'channel_type',
      headerName: 'Loại Kênh',
      width: 120,
      renderCell: (params) => (
        <Chip 
          label={params.value || 'N/A'} 
          size="small" 
          variant="outlined"
          color="primary"
        />
      )
    },
    {
      field: 'channel_id',
      headerName: 'ID Kênh',
      width: 100
    },
    {
      field: 'status',
      headerName: 'Trạng Thái',
      width: 120,
      renderCell: (params) => (
        <Chip 
          label={params.value || 'Draft'} 
          size="small" 
          color={getStatusColor(params.value || 'draft')}
        />
      )
    },
    {
      field: 'publish_time',
      headerName: 'Thời Gian Đăng',
      width: 140,
      valueGetter: (value, row) => {
        try {
          return value ? new Date(value).toLocaleString('vi-VN') : '';
        } catch {
          return '';
        }
      }
    },
    {
      field: 'title',
      headerName: 'Tiêu Đề',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ 
          overflow: 'hidden', 
          textOverflow: 'ellipsis', 
          whiteSpace: 'nowrap',
          maxWidth: '100%'
        }}>
          {params.value || ''}
        </Box>
      )
    },
    {
      field: 'descript_content',
      headerName: 'Mô Tả Nội Dung',
      width: 250,
      renderCell: (params) => (
        <Box sx={{ 
          overflow: 'hidden', 
          textOverflow: 'ellipsis', 
          whiteSpace: 'nowrap',
          maxWidth: '100%'
        }}>
          {params.value || ''}
        </Box>
      )
    },
    {
      field: 'product',
      headerName: 'Sản Phẩm',
      width: 150
    },
    {
      field: 'target_customer',
      headerName: 'Khách Hàng Mục Tiêu',
      width: 180,
      renderCell: (params) => (
        <Box sx={{ 
          overflow: 'hidden', 
          textOverflow: 'ellipsis', 
          whiteSpace: 'nowrap',
          maxWidth: '100%'
        }}>
          {params.value || ''}
        </Box>
      )
    },
    {
      field: 'goals',
      headerName: 'Mục Tiêu',
      width: 200,
      renderCell: (params) => (
        <Box sx={{ 
          overflow: 'hidden', 
          textOverflow: 'ellipsis', 
          whiteSpace: 'nowrap',
          maxWidth: '100%'
        }}>
          {params.value || ''}
        </Box>
      )
    },
    {
      field: 'media_url',
      headerName: 'Media URL',
      width: 120,
      renderCell: (params) => (
        params.value ? (
          <Chip label="Có Media" size="small" color="info" variant="outlined" />
        ) : (
          <Chip label="Không có" size="small" variant="outlined" />
        )
      )
    },
    {
      field: 'article_route',
      headerName: 'Article Route',
      width: 130,
      renderCell: (params) => (
        params.value ? (
          <Chip label="Có Link" size="small" color="success" variant="outlined" />
        ) : (
          <Chip label="Không có" size="small" variant="outlined" />
        )
      )
    },
    {
      field: 'last_updated_date',
      headerName: 'Cập Nhật Cuối',
      width: 140,
      valueGetter: (value, row) => {
        try {
          return value ? new Date(value).toLocaleString('vi-VN') : '';
        } catch {
          return '';
        }
      }
    },
    {
      field: 'actions',
      headerName: 'Thao Tác',
      width: 100,
      sortable: false,
      filterable: false,
      renderCell: (params) => (
        <IconButton
          size="small"
          onClick={(e) => handleMenuClick(e, params.row)}
          sx={{ ml: 1 }}
        >
          <MoreIcon />
        </IconButton>
      )
    }
  ];

  return (
    <>
      <Box sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={planItems}
          columns={columns}
          loading={isLoading}
          pageSizeOptions={[25, 50, 100]}
          initialState={{
            pagination: { paginationModel: { pageSize: 25 } }
          }}
          slots={{
            toolbar: GridToolbar
          }}
          slotProps={{
            toolbar: {
              showQuickFilter: true,
              quickFilterProps: { debounceMs: 500 }
            }
          }}
          sx={{
            '& .MuiDataGrid-cell': {
              borderRight: 1,
              borderColor: 'divider'
            },
            '& .MuiDataGrid-columnHeaders': {
              borderBottom: 2,
              borderColor: 'primary.main',
              bgcolor: 'primary.light',
              color: 'black'
            }
          }}
          disableRowSelectionOnClick
        />
      </Box>

      {/* Action Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem onClick={handleEdit}>
          <EditIcon sx={{ mr: 1 }} />
          Chỉnh sửa
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} />
          Xóa
        </MenuItem>
      </Menu>
    </>
  );
}
