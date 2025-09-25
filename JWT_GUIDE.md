# 🔐 JWT System đơn giản cho AI-Proma

## Tổng quan
Hệ thống JWT đã được đơn giản hóa để chỉ chứa thông tin cần thiết và không phụ thuộc vào các API khác.

## 📋 JWT Payload Structure

JWT token sẽ chứa các thông tin sau:
```json
{
  "sub": "XCEL_BOT",
  "username": "XCEL_BOT", 
  "user_id": "65cd8c30-5300-4b73-a9fa-add929ad6fd8",
  "agent_id": "facebook_marketing_agent",
  "workspace_id": "963c2754-6388-4219-8989-39bb5d12ade",
  "role": "user",
  "user_info": "",
  "iat": 1758598555,
  "exp": 1758627355
}
```

## 🚀 API Endpoints

### 1. Tạo JWT Token
```http
POST /api/v1/auth/token
Content-Type: application/json

{
  "username": "XCEL_BOT",
  "agent_id": "facebook_marketing_agent",
  "workspace_id": "963c2754-6388-4219-8989-39bb5d12ade"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 28800,
  "claims": {
    "sub": "XCEL_BOT",
    "username": "XCEL_BOT",
    "user_id": "65cd8c30530...",
    "agent_id": "facebook_marketing_agent",
    "workspace_id": "963c2754-6388...",
    "role": "user"
  }
}
```

### 2. Decode JWT Token
```http
POST /api/v1/auth/decode?token=YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "valid": true,
  "payload": {
    "sub": "XCEL_BOT",
    "username": "XCEL_BOT",
    "user_id": "65cd8c30530...",
    "agent_id": "facebook_marketing_agent",
    "workspace_id": "963c2754-6388...",
    "role": "user",
    "iat": 1758598555,
    "exp": 1758627355
  },
  "expires_at": "2025-09-25T10:15:55"
}
```

## 🎯 Sử dụng với Create Epic API (Đã cải tiến)

API create epic đã được cải tiến để chỉ cần 3 thông tin từ JWT:

```http
POST /api/v1/epics/create
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "epic_name": "My Epic",
  "description": "Epic description",
  "category": "Development",
  "priority": "High"
}
```

### ✨ **Cải tiến mới:**
- JWT có thể chứa **bất kỳ thông tin nào**, API chỉ lấy 3 field cần thiết:
  - `workspace_id` 
  - `user_id`
  - `user_name` (hoặc `username` hoặc `sub`)
- **Bỏ qua tất cả thông tin thừa** trong JWT
- **Không cần agent_id** nữa
- Logic đơn giản hơn, ít debug code

### 🔄 **Luồng hoạt động:**
1. Decode JWT token từ Authorization header
2. Extract chỉ `workspace_id`, `user_id`, `user_name`
3. Kết hợp với thông tin từ request body
4. Tạo epic trong database

## ⚙️ Configuration

Thêm vào file `.env`:
```env
JWT_SECRET_KEY=ai-proma-secret-key-2024
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480
```

## 🧪 Testing

Chạy test script:
```bash
python test_jwt.py
```

## 🔧 Key Features

- ✅ **Đơn giản**: Chỉ chứa thông tin cần thiết
- ✅ **Độc lập**: Không phụ thuộc vào API khác
- ✅ **Tự động**: API tự decode và lấy thông tin
- ✅ **Bảo mật**: JWT signed với secret key
- ✅ **Expiration**: Token có thời hạn (8 giờ)
- ✅ **Validation**: Kiểm tra các field bắt buộc

## 📝 Notes

- Token có thời hạn 8 giờ (480 phút)
- `user_id` được generate từ username bằng SHA-256
- Tất cả API cần authentication sẽ tự động decode JWT
- Không cần database lookup - tất cả thông tin trong token
