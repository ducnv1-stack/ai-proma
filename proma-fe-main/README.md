# Famarex - AI Agent for Facebook Marketing

Famarex is an advanced AI-powered platform designed to revolutionize Facebook marketing through intelligent automation, campaign optimization, and data-driven insights.

## 🚀 Features

- **AI-Powered Chat Interface**: Interactive AI assistant for Facebook marketing guidance
- **Modern UI/UX**: Clean white and blue design with responsive layout
- **User Authentication**: Secure login/registration with social media integration
- **Workspace Management**: Multi-workspace support for different marketing campaigns
- **Real-time Analytics**: Campaign performance tracking and optimization suggestions
- **Audience Targeting**: AI-driven audience analysis and recommendations

## 🛠️ Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript
- **Styling**: Tailwind CSS 4
- **Icons**: Heroicons
- **Animations**: Framer Motion
- **Forms**: React Hook Form with Zod validation

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn package manager

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd famarex-fe
```

### 2. Install dependencies
```bash
npm install
# or
yarn install
```

### 3. Environment Setup
```bash
# Copy the environment example file
cp env.example .env.local

# Edit .env.local with your API configurations
```

### 4. Run the development server
```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🏗️ Project Structure

```
src/
├── app/
│   ├── components/          # Reusable UI components
│   │   └── LoginModal.tsx   # Authentication modal
│   ├── chat/               # Chat interface pages
│   │   └── page.tsx        # Main chat interface
│   ├── lib/                # Utilities and services
│   │   └── api/            # API service layers
│   │       ├── aiService.ts      # AI chat and analysis API
│   │       └── userService.ts    # User management API
│   ├── globals.css         # Global styles and theme
│   ├── layout.tsx          # Root layout component
│   └── page.tsx           # Landing page
```

## 🎨 Design System

### Color Palette
- **Primary Blue**: `#3b82f6`
- **Secondary Blue**: `#1e40af`
- **Background**: `#ffffff`
- **Text**: `#1f2937`

### Key Components
- **Landing Page**: Hero section, features, about, and footer
- **Login Modal**: Authentication with social login options
- **Chat Interface**: AI assistant with sidebar navigation
- **User Profile**: Workspace and user management

## 🔧 API Integration

### AI Service API
Handles AI chat functionality, campaign analysis, and marketing insights.

**Endpoints:**
- `POST /chat` - Send messages to AI assistant
- `GET /campaigns/{id}/analyze` - Analyze campaign performance
- `GET /insights/{userId}` - Get marketing insights
- `POST /audience/suggestions` - Generate audience recommendations

### User Management API
Manages authentication, user data, and workspace functionality.

**Endpoints:**
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `GET /users/me` - Get current user data
- `GET /workspaces` - Get user workspaces
- `POST /workspaces` - Create new workspace

## 🚀 Deployment

### Build for production
```bash
npm run build
# or
yarn build
```

### Start production server
```bash
npm start
# or
yarn start
```

## 📱 Features Overview

### Landing Page
- Hero section with Famarex branding
- Interactive chat input (triggers login)
- Feature showcase
- About section
- Professional footer

### Authentication
- Email/password login and registration
- Social login (Google, Facebook)
- Form validation with error handling
- Responsive modal design

### Chat Interface
- Real-time AI conversation
- Message history
- Typing indicators
- User profile sidebar
- Chat session management
- Settings and logout options

### API Services
- Robust error handling
- Fallback responses for offline mode
- Token-based authentication
- Workspace management
- Campaign analytics integration

## 🔐 Environment Variables

Required environment variables (see `env.example`):

```bash
# AI Service
NEXT_PUBLIC_AI_SERVICE_URL=https://api.famarex-ai.com
NEXT_PUBLIC_AI_API_KEY=your_ai_api_key

# User Management  
NEXT_PUBLIC_USER_API_URL=https://api.famarex.com
NEXT_PUBLIC_USER_API_KEY=your_user_api_key

# Facebook Integration
NEXT_PUBLIC_FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: support@famarex.com
- Documentation: [docs.famarex.com](https://docs.famarex.com)
- Issues: [GitHub Issues](https://github.com/famarex/famarex-fe/issues)

---

**Famarex** - Revolutionizing Facebook Marketing with AI
