'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Stack,
  Typography,
  Chip,
  Box,
  Alert,
  SelectChangeEvent
} from '@mui/material';
import { ContentPlanItem, CreateContentPlanItemRequest } from '../../libs/types';

interface AddContentModalProps {
  open: boolean;
  onClose: () => void;
  onAdd: (item: CreateContentPlanItemRequest) => void;
}

interface ShareModalProps {
  open: boolean;
  onClose: () => void;
  onShare: (email: string, permission: string, message: string) => void;
}

export function AddContentModal({ open, onClose, onAdd }: AddContentModalProps) {
  const [formData, setFormData] = useState<CreateContentPlanItemRequest>({
    task_date: new Date().toISOString().split('T')[0],
    channel_type: 'social_media',
    channel_id: '',
    status: 'draft',
    publish_time: '',
    title: '',
    descript_content: '',
    product: '',
    target_customer: '',
    goals: '',
    media_url: '',
    article_route: ''
  });

  const handleSubmit = () => {
    onAdd(formData);
    onClose();
    // Reset form
    setFormData({
      task_date: new Date().toISOString().split('T')[0],
      channel_type: 'social_media',
      channel_id: '',
      status: 'draft',
      publish_time: '',
      title: '',
      descript_content: '',
      product: '',
      target_customer: '',
      goals: '',
      media_url: '',
      article_route: ''
    });
  };

  const handleChange = (field: keyof CreateContentPlanItemRequest, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSelectChange = (field: keyof CreateContentPlanItemRequest) => (event: SelectChangeEvent<string>) => {
    handleChange(field, event.target.value);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Thêm Nội Dung Mới</DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          <Stack direction="row" spacing={2}>
            <TextField
              label="Ngày Task"
              type="date"
              value={formData.task_date}
              onChange={(e) => handleChange('task_date', e.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
            <TextField
              label="Ngày Đăng"
              type="datetime-local"
              value={formData.publish_time}
              onChange={(e) => handleChange('publish_time', e.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
          </Stack>

          <Stack direction="row" spacing={2}>
            <FormControl fullWidth>
              <InputLabel>Loại Kênh</InputLabel>
              <Select
                value={formData.channel_type}
                onChange={handleSelectChange('channel_type')}
                label="Loại Kênh"
              >
                <MenuItem value="social_media">Social Media</MenuItem>
                <MenuItem value="blog">Blog</MenuItem>
                <MenuItem value="email">Email</MenuItem>
                <MenuItem value="video">Video</MenuItem>
                <MenuItem value="website">Website</MenuItem>
                <MenuItem value="newsletter">Newsletter</MenuItem>
                <MenuItem value="podcast">Podcast</MenuItem>
                <MenuItem value="webinar">Webinar</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="ID Kênh"
              value={formData.channel_id}
              onChange={(e) => handleChange('channel_id', e.target.value)}
              fullWidth
            />
          </Stack>

          <FormControl fullWidth>
            <InputLabel>Trạng Thái</InputLabel>
            <Select
              value={formData.status}
              onChange={handleSelectChange('status')}
              label="Trạng Thái"
            >
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="scheduled">Scheduled</MenuItem>
              <MenuItem value="published">Published</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Tiêu Đề"
            value={formData.title}
            onChange={(e) => handleChange('title', e.target.value)}
            fullWidth
            required
          />

          <TextField
            label="Mô Tả Nội Dung"
            value={formData.descript_content}
            onChange={(e) => handleChange('descript_content', e.target.value)}
            multiline
            rows={4}
            fullWidth
            required
          />

          <Stack direction="row" spacing={2}>
            <TextField
              label="Sản Phẩm"
              value={formData.product}
              onChange={(e) => handleChange('product', e.target.value)}
              fullWidth
              required
            />
            <TextField
              label="Khách Hàng Mục Tiêu"
              value={formData.target_customer}
              onChange={(e) => handleChange('target_customer', e.target.value)}
              fullWidth
              required
            />
          </Stack>

          <TextField
            label="Mục Tiêu"
            value={formData.goals}
            onChange={(e) => handleChange('goals', e.target.value)}
            multiline
            rows={2}
            fullWidth
            required
          />

          <Stack direction="row" spacing={2}>
            <TextField
              label="Media URL"
              value={formData.media_url || ''}
              onChange={(e) => handleChange('media_url', e.target.value)}
              fullWidth
            />
            <TextField
              label="Article Route"
              value={formData.article_route || ''}
              onChange={(e) => handleChange('article_route', e.target.value)}
              fullWidth
            />
          </Stack>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Hủy</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          disabled={!formData.title || !formData.descript_content || !formData.product || !formData.target_customer || !formData.goals}
        >
          Thêm
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export function ShareModal({ open, onClose, onShare }: ShareModalProps) {
  const [email, setEmail] = useState('');
  const [permission, setPermission] = useState<'view' | 'edit' | 'admin'>('view');
  const [message, setMessage] = useState('');

  const handleSubmit = () => {
    if (email.trim()) {
      onShare(email, permission, message);
      onClose();
      // Reset form
      setEmail('');
      setPermission('view');
      setMessage('');
    }
  };

  const handlePermissionChange = (event: SelectChangeEvent<string>) => {
    setPermission(event.target.value as 'view' | 'edit' | 'admin');
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Chia Sẻ Content Plan</DialogTitle>
      <DialogContent>
        <Stack spacing={3} sx={{ mt: 1 }}>
          <Alert severity="info">
            Mời người khác cộng tác trong content plan này
          </Alert>

          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="example@email.com"
            fullWidth
            required
          />

          <FormControl fullWidth>
            <InputLabel>Quyền Truy Cập</InputLabel>
            <Select
              value={permission}
              onChange={handlePermissionChange}
              label="Quyền Truy Cập"
            >
              <MenuItem value="view">
                <Box>
                  <Typography variant="body2" fontWeight="bold">
                    Chỉ Xem
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Có thể xem nội dung nhưng không thể chỉnh sửa
                  </Typography>
                </Box>
              </MenuItem>
              <MenuItem value="edit">
                <Box>
                  <Typography variant="body2" fontWeight="bold">
                    Chỉnh Sửa
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Có thể xem và chỉnh sửa nội dung
                  </Typography>
                </Box>
              </MenuItem>
              <MenuItem value="admin">
                <Box>
                  <Typography variant="body2" fontWeight="bold">
                    Quản Trị
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Toàn quyền quản lý và chia sẻ
                  </Typography>
                </Box>
              </MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="Tin Nhắn (Tùy Chọn)"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            multiline
            rows={3}
            placeholder="Thêm tin nhắn cá nhân..."
            fullWidth
          />

          <Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Quyền được chọn:
            </Typography>
            <Chip 
              label={
                permission === 'view' ? 'Chỉ Xem' :
                permission === 'edit' ? 'Chỉnh Sửa' : 'Quản Trị'
              }
              color={
                permission === 'view' ? 'default' :
                permission === 'edit' ? 'primary' : 'secondary'
              }
              size="small"
            />
          </Box>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Hủy</Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained"
          disabled={!email.trim()}
        >
          Gửi Lời Mời
        </Button>
      </DialogActions>
    </Dialog>
  );
}
