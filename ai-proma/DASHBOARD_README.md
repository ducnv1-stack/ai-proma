# Proma AI Dashboard - Hướng dẫn sử dụng

## Tổng quan
Dashboard mới với sidebar navigation và tích hợp chat AI, được thiết kế theo modern UI/UX principles với Tailwind CSS.

## Cấu trúc Dashboard

### 🏠 **Sidebar Navigation**
- **Dashboard**: Trang chính với thống kê và overview
- **Chat AI**: Trang chat với AI agents (tích hợp typing indicator)
- **Agents**: Quản lý AI agents
- **File Management**: Quản lý files và tài liệu
- **Tasks**: Quản lý công việc và nhiệm vụ

### 📊 **Dashboard Home**
- **Stats Cards**: Hiển thị thống kê realtime
  - Tin nhắn hôm nay
  - Agents hoạt động
  - Số người dùng
  - Hiệu suất hệ thống
- **Hover Effects**: Cards có animation khi hover
- **Responsive Design**: Tối ưu cho mọi thiết bị

### 💬 **Chat AI Section**
- **Typing Indicator**: Hiệu ứng bong bóng soạn thảo mượt mà
- **Agent Status**: Hiển thị trạng thái realtime
  - "Đang suy nghĩ..." (vàng)
  - "Đang trả lời..." (xanh)
  - "Online" (xanh lá)
- **Message Streaming**: Hiển thị tin nhắn realtime
- **File Upload**: Hỗ trợ upload hình ảnh
- **Auto Scroll**: Tự động cuộn xuống tin nhắn mới

## Files Structure

```
frontend/
├── dashboard.html          # Main dashboard page
├── dashboard-script.js     # Dashboard JavaScript logic
├── dashboard-styles.css    # Custom CSS styles
├── index.html             # Original chat page (still available)
├── script.js              # Original chat script
└── styles.css             # Original chat styles
```

## Cách sử dụng

### 1. **Khởi động ứng dụng**
```bash
cd D:\CTY-Xcelbot\ai-proma\ai-proma
scripts\run_simple.bat
```

### 2. **Truy cập Dashboard**
- **URL chính**: `http://localhost:8000` (redirect to dashboard)
- **Dashboard trực tiếp**: `http://localhost:8000/frontend/dashboard.html`
- **Chat cũ**: `http://localhost:8000/frontend/index.html`
- **Demo**: `http://localhost:8000/demo`

### 3. **Đăng nhập**
- Sử dụng form đăng nhập với:
  - Username
  - Password  
  - Workspace ID
  - Agent selection

### 4. **Navigation**
- Click vào các mục trong sidebar để chuyển đổi giữa các section
- Section "Chat AI" sẽ hiển thị interface chat đầy đủ
- Các section khác hiện tại là placeholder để mở rộng

## Tính năng nổi bật

### ✨ **Modern UI/UX**
- **Tailwind CSS**: Framework CSS hiện đại
- **Inter Font**: Typography chuyên nghiệp
- **FontAwesome Icons**: Icons đẹp và nhất quán
- **Gradient Headers**: Header với gradient đẹp mắt

### 🎨 **Animations & Effects**
- **Smooth Transitions**: Chuyển đổi mượt mà giữa các section
- **Hover Effects**: Cards và buttons có hover animation
- **Typing Indicator**: Hiệu ứng typing với shimmer effect
- **Message Animations**: Tin nhắn xuất hiện với slide-in effect

### 📱 **Responsive Design**
- **Mobile First**: Tối ưu cho mobile trước
- **Breakpoints**: Responsive cho tablet và desktop
- **Touch Friendly**: UI elements phù hợp cho touch
- **Sidebar Collapse**: Sidebar thu gọn trên mobile

### 🚀 **Performance**
- **Lazy Loading**: Chỉ load section khi cần
- **Optimized CSS**: CSS được tối ưu và tách riêng
- **Efficient DOM**: Manipulation DOM hiệu quả
- **Memory Management**: Quản lý memory tốt

## Customization

### 🎨 **Thay đổi màu sắc**
Chỉnh sửa trong `dashboard-styles.css`:
```css
/* Primary colors */
.bg-purple-600 { background-color: #your-color; }
.text-purple-600 { color: #your-color; }
```

### 📐 **Thay đổi layout**
Chỉnh sửa Tailwind classes trong `dashboard.html`:
```html
<!-- Sidebar width -->
<aside class="w-64"> <!-- Change to w-72 for wider -->

<!-- Grid columns -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
```

### ⚡ **Thêm section mới**
1. Thêm navigation item trong sidebar
2. Tạo section content trong main area
3. Cập nhật JavaScript navigation logic

## API Integration

Dashboard tích hợp với các API endpoints:
- `POST /api/v1/auth/login` - Authentication
- `POST /api/v1/chat` - Chat streaming
- `GET /api/v1/agents` - Get agents list
- `POST /api/v1/sessions` - Create session

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ IE không được hỗ trợ

## Troubleshooting

### 🔧 **Dashboard không load**
1. Kiểm tra server đang chạy
2. Clear browser cache
3. Check console errors

### 💬 **Chat không hoạt động**
1. Kiểm tra authentication
2. Verify API endpoints
3. Check network connectivity

### 🎨 **Styles bị lỗi**
1. Kiểm tra `dashboard-styles.css` đã load
2. Verify Tailwind CDN
3. Check CSS conflicts

## Development

### 🛠️ **Local Development**
```bash
# Start server
python main_simple.py

# Or use batch file
scripts\run_simple.bat
```

### 📝 **Adding Features**
1. Update HTML structure
2. Add CSS styles
3. Implement JavaScript logic
4. Test across devices

### 🧪 **Testing**
- Test all navigation flows
- Verify responsive design
- Check typing indicator timing
- Test error scenarios

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Real-time notifications
- [ ] Advanced agent management
- [ ] File upload progress
- [ ] Chat history search
- [ ] Multi-language support
- [ ] Keyboard shortcuts
- [ ] Voice input support

## Support

Nếu gặp vấn đề, hãy kiểm tra:
1. Console logs trong browser
2. Server logs
3. Network requests trong DevTools
4. Authentication status

Dashboard mới này cung cấp trải nghiệm người dùng hiện đại và chuyên nghiệp cho hệ thống Proma AI! 🚀
