// Dashboard Navigation and Chat Integration
class PromaDashboard {
    constructor() {
        this.apiUrl = 'http://localhost:8002';
        this.token = null;
        this.sessionId = null;
        this.workspaceId = null;
        this.agentId = 'project_manager_agent';
        this.currentUser = null;
        this.attachedImages = [];
        this.settings = {
            autoScroll: true,
            soundNotifications: false
        };

        // Typing indicator state
        this.typingTimeout = null;
        this.isTypingVisible = false;

        this.initializeElements();
        this.bindEvents();
        this.loadSettings();
        this.checkAuthentication();
    }

    initializeElements() {
        // Dashboard elements
        this.pageTitle = document.getElementById('page-title');
        this.currentUserEl = document.getElementById('current-user');
        this.userStatusEl = document.getElementById('user-status');

        // Chat elements
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('send-button');
        this.fileInput = document.getElementById('file-input');
        this.attachedImagesContainer = document.getElementById('attached-images');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.charCount = document.getElementById('char-count');

        // Modal elements (removed - using separate login/register pages)
        // All auth modal elements removed since we use separate pages now

        // Header elements
        this.agentName = document.getElementById('agent-name');
        this.agentStatus = document.getElementById('agent-status');
        this.aiStatus = document.getElementById('ai-status');
        this.aiThinking = document.getElementById('ai-thinking');

        // User menu elements
        this.userMenuButton = document.getElementById('user-menu-button');
        this.userDropdown = document.getElementById('user-dropdown');
        this.userMenuIcon = document.getElementById('user-menu-icon');
        this.logoutButton = document.getElementById('logout-button');
        this.sidebarLogoutButton = document.getElementById('sidebar-logout-button');

        // Header user menu elements
        this.headerUserMenu = document.getElementById('header-user-menu');
        this.headerDropdown = document.getElementById('header-dropdown');
        this.headerCurrentUser = document.getElementById('header-current-user');
        this.headerLogoutButton = document.getElementById('header-logout-button');
    }

    bindEvents() {
        // Navigation events
        window.showSection = (section) => this.showSection(section);

        console.log('Binding events...');
        console.log('Send button:', this.sendBtn);
        console.log('Message input:', this.messageInput);

        // Chat events
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => {
                console.log('Send button clicked');
                this.sendMessage();
            });
        } else {
            console.error('Send button not found!');
        }

        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    console.log('Enter key pressed');
                    this.sendMessage();
                }
            });

            this.messageInput.addEventListener('input', () => this.handleInputChange());
        } else {
            console.error('Message input not found!');
        }

        // Auth forms
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        if (this.registerForm) {
            this.registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }

        // Global functions removed - using separate login/register pages

        // Global logout function for emergency use
        window.performLogout = () => {
            console.log('🚪 Global logout called');
            this.performLogout();
        };

        // File input
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        // User menu events
        if (this.userMenuButton) {
            this.userMenuButton.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleUserDropdown();
            });
        }

        if (this.headerUserMenu) {
            this.headerUserMenu.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleHeaderDropdown();
            });
        }

        // Logout button events
        if (this.logoutButton) {
            this.logoutButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('🚪 User dropdown logout button clicked');
                this.handleLogout();
            });
        }

        if (this.sidebarLogoutButton) {
            this.sidebarLogoutButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('🚪 Sidebar logout button clicked');
                this.handleLogout();
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (this.userDropdown && !this.userDropdown.contains(e.target) && !this.userMenuButton.contains(e.target)) {
                this.hideUserDropdown();
            }
        });

        if (this.headerLogoutButton) {
            this.headerLogoutButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLogout();
            });
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (this.userDropdown && !this.userDropdown.classList.contains('hidden')) {
                this.hideUserDropdown();
            }
            if (this.headerDropdown && !this.headerDropdown.classList.contains('hidden')) {
                this.hideHeaderDropdown();
            }
        });
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.section-content').forEach(section => {
            section.classList.add('hidden');
        });

        // Remove active class from all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('bg-purple-600', 'text-white');
        });

        // Show selected section
        let targetSection;
        if (sectionName === 'dashboard') {
            targetSection = document.getElementById('dashboard-section');
        } else if (sectionName === 'chat') {
            targetSection = document.getElementById('chat-section');
        } else {
            targetSection = document.getElementById(`${sectionName}-section`);
        }
        
        if (targetSection) {
            targetSection.classList.remove('hidden');
            console.log(`✅ Showing section: ${sectionName}`, targetSection);
        } else {
            console.error(`❌ Section not found: ${sectionName}`);
        }

        // Add active class to clicked nav item
        const activeNavItem = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
        if (activeNavItem) {
            activeNavItem.classList.add('bg-purple-600', 'text-white');
        }

        // Update page title
        if (this.pageTitle) {
            this.pageTitle.textContent = sectionName.charAt(0).toUpperCase() + sectionName.slice(1);
        }

        // Add welcome message if switching to chat
        if (sectionName === 'chat') {
            setTimeout(() => {
                this.addWelcomeMessage();
            }, 300);
        }
    }

    scrollToBottom() {
        if (this.chatMessages && this.settings.autoScroll) {
            setTimeout(() => {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }, 100);
        }
    }

    handleInputChange() {
        if (!this.messageInput) return;

        const message = this.messageInput.value.trim();
        const length = this.messageInput.value.length;

        if (this.charCount) {
            this.charCount.textContent = `${length}/4000`;
        }

        if (this.sendBtn) {
            this.sendBtn.disabled = !message && this.attachedImages.length === 0;
        }

        // Auto-resize textarea
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        console.log('sendMessage called');
        const message = this.messageInput.value.trim();
        console.log('Message:', message);
        if (!message && this.attachedImages.length === 0) {
            console.log('No message or images, returning');
            return;
        }

        // Show user message
        this.addMessage('user', message);

        // Clear input
        this.messageInput.value = '';
        this.handleInputChange();

        // Show AI thinking status
        this.showAIThinking();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Call AI API
            const response = await this.callAI(message);

            // Hide thinking status and typing indicator
            this.hideAIThinking();
            this.hideTypingIndicator();

            // Show AI response with typing effect
            await this.typeAIResponse(response);

        } catch (error) {
            console.error('AI call failed:', error);
            this.hideAIThinking();
            this.hideTypingIndicator();
            this.addMessage('agent', 'Xin lỗi, tôi gặp sự cố khi xử lý tin nhắn của bạn. Vui lòng thử lại.');
        }
    }

    async callAI(message) {
        const response = await fetch(`${this.apiUrl}/api/v1/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId || 'default',
                workspace_id: this.workspaceId || 'default',
                agent_id: this.agentId
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.response || data.message || 'Tôi không thể trả lời câu hỏi này.';
    }

    async typeAIResponse(text) {
        // Wait a bit before hiding typing indicator
        await new Promise(resolve => setTimeout(resolve, 100));

        const messageElement = this.addMessage('agent', '');
        const contentDiv = messageElement.querySelector('.message-bubble');

        let currentText = '';
        const words = text.split(' ');

        for (let i = 0; i < words.length; i++) {
            currentText += (i > 0 ? ' ' : '') + words[i];
            contentDiv.innerHTML = this.formatMessage(currentText);
            this.scrollToBottom();

            // Faster typing: 30-80ms per word
            await new Promise(resolve => setTimeout(resolve, Math.random() * 50 + 30));
        }
    }

    addMessage(sender, content, attachments = []) {
        if (!this.chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `flex items-start space-x-3 mb-4 ${sender === 'user' ? 'justify-end' : ''}`;

        const avatarDiv = document.createElement('div');
        if (sender === 'user') {
            avatarDiv.className = 'w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center order-2 flex-shrink-0';
            avatarDiv.innerHTML = '<i class="fas fa-user text-blue-600 text-sm"></i>';
        } else {
            avatarDiv.className = 'w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0';
            avatarDiv.innerHTML = '<i class="fas fa-robot text-purple-600 text-sm"></i>';
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = `message-bubble p-3 ${sender === 'user' ? 'user order-1' : 'agent'}`;
        contentDiv.innerHTML = this.formatMessage(content);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    showTypingIndicator() {
        // Remove existing typing indicator
        this.hideTypingIndicator();

        // Create typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'flex items-start space-x-3 mb-4';
        typingDiv.id = 'typing-indicator';

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0';
        avatarDiv.innerHTML = '<i class="fas fa-robot text-purple-600 text-sm"></i>';

        const typingBubble = document.createElement('div');
        typingBubble.className = 'typing-indicator';
        typingBubble.innerHTML = `
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        typingDiv.appendChild(avatarDiv);
        typingDiv.appendChild(typingBubble);

        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    showAIThinking() {
        if (this.aiStatus) this.aiStatus.classList.add('hidden');
        if (this.aiThinking) this.aiThinking.classList.remove('hidden');
    }

    hideAIThinking() {
        if (this.aiStatus) this.aiStatus.classList.remove('hidden');
        if (this.aiThinking) this.aiThinking.classList.add('hidden');
    }

    formatMessage(text) {
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code class="bg-gray-200 px-1 rounded">$1</code>');
    }

    addWelcomeMessage() {
        if (!this.chatMessages) return;

        // Check if welcome message already exists
        if (this.chatMessages.querySelector('.welcome-message')) return;

        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message flex items-start space-x-3 mb-4';

        welcomeDiv.innerHTML = `
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-purple-600 text-sm"></i>
            </div>
            <div class="message-bubble agent p-3">
                <p>👋 Xin chào <strong>${this.currentUser || 'bạn'}</strong>!</p>
                <p>Tôi là <strong>Proma Project Manager Agent</strong>. Tôi có thể giúp bạn:</p>
                <ul class="mt-2 ml-4 list-disc">
                    <li>📋 Quản lý dự án và lập kế hoạch</li>
                    <li>✅ Tạo và phân công tasks</li>
                    <li>📊 Theo dõi tiến độ công việc</li>
                    <li>🚀 Tối ưu hóa quy trình làm việc</li>
                </ul>
                <p class="mt-2">Hãy bắt đầu cuộc trò chuyện bằng cách hỏi tôi về dự án của bạn! 💬</p>
            </div>
        `;

        this.chatMessages.appendChild(welcomeDiv);
        this.scrollToBottom();
    }

    clearChat() {
        if (this.chatMessages) {
            this.chatMessages.innerHTML = '';
            setTimeout(() => {
                this.addWelcomeMessage();
            }, 100);
        }
    }

    // Authentication methods
    async handleLogin(e) {
        e.preventDefault();
        // Auth functions removed - using separate pages

        const formData = new FormData(e.target);
        const username = formData.get('username');
        const password = formData.get('password');

        try {
            const response = await fetch(`${this.apiUrl}/api/v1/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_name: username,
                    user_pass: password
                })
            });

            const data = await response.json();

            if (data.access_token) {
                this.token = data.access_token;
                this.currentUser = data.user.user_name;
                this.workspaceId = data.user.workspace_id;
                this.agentId = 'project_manager_agent';

                // Store in localStorage
                localStorage.setItem('proma_token', this.token);
                localStorage.setItem('proma_user', this.currentUser);
                localStorage.setItem('proma_workspace', this.workspaceId);
                localStorage.setItem('proma_agent', this.agentId);
                localStorage.setItem('proma_user_data', JSON.stringify(data.user));

                // Modal removed - user already authenticated
                this.updateUserInfo();
                this.clearChat();
            } else {
                // Redirect to login page on failure
                window.location.href = 'login.html?error=login_failed';
            }
        } catch (error) {
            console.error('Login error:', error);
            // Redirect to login page on error
            window.location.href = 'login.html?error=network_error';
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        console.log('📝 Register form submitted');

        // Auth functions removed - using separate pages

        const formData = new FormData(e.target);
        const username = formData.get('username');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');

        console.log(`📝 Register attempt for user: ${username}`);

        // Validate password confirmation
        if (password !== confirmPassword) {
            console.log('❌ Password confirmation mismatch');
            this.hideAuthLoading();
            this.showRegisterForm();
            this.showAuthError('Mật khẩu xác nhận không khớp.');
            return;
        }

        // Validate password length
        if (password.length < 6) {
            console.log('❌ Password too short');
            this.hideAuthLoading();
            this.showRegisterForm();
            this.showAuthError('Mật khẩu phải có ít nhất 6 ký tự.');
            return;
        }

        try {
            console.log(`🚀 Calling register API: ${this.apiUrl}/api/v1/auth/register`);

            const response = await fetch(`${this.apiUrl}/api/v1/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_name: username,
                    user_pass: password,
                    confirm_password: confirmPassword
                })
            });

            console.log(`📡 Register response status: ${response.status}`);
            const data = await response.json();
            console.log('📡 Register response data:', data);

            if (response.ok && data.access_token) {
                console.log('✅ Registration successful!');

                // Clear register form first
                if (this.registerForm) {
                    this.registerForm.reset();
                }

                // Redirect to login page with success message
                window.location.href = `login.html?success=registered&username=${encodeURIComponent(username)}`;

                // Auto-fill username in login form
                const loginUsernameInput = document.getElementById('login-username');
                if (loginUsernameInput) {
                    loginUsernameInput.value = username;
                    loginUsernameInput.focus();
                }

            } else {
                console.log('❌ Registration failed:', data.detail);
                // Redirect to register page on failure
                window.location.href = 'register.html?error=register_failed';
            }
        } catch (error) {
            console.error('❌ Register error:', error);
            // Redirect to register page on error
            window.location.href = 'register.html?error=network_error';
        }
    }

    async checkAuth() {
        console.log('🔐 Checking authentication...');

        // Check local authentication data first
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        const userId = localStorage.getItem('user_id');
        const userName = localStorage.getItem('user_name');
        const userEmail = localStorage.getItem('user_email');
        const token = localStorage.getItem('proma_token');
        
        console.log('🔍 Local auth check results:', {
            isLoggedIn,
            userId,
            userName,
            userEmail,
            hasToken: !!token
        });
        
        // If no local auth data, redirect to login
        if (!token || !userId || isLoggedIn !== 'true') {
            console.log('❌ No local authentication data, redirecting to login');
            this.clearIncompleteAuthData();
            window.location.href = 'login.html?error=unauthorized';
            return;
        }
        
        // Verify authentication with backend
        try {
            console.log('🚀 Verifying authentication with backend...');
            const response = await fetch(`${this.apiUrl}/api/v1/auth/verify`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                }
            });

            console.log('📡 Auth verification response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Backend authentication verified:', data);
                
                // Set instance variables from verified data
                this.token = token;
                this.currentUser = data.user_name || userName;
                this.userId = data.user_id || userId;
                this.userEmail = userEmail;
                this.workspaceId = localStorage.getItem('proma_workspace') || 'default';
                this.agentId = localStorage.getItem('proma_agent') || 'project_manager_agent';
                
                console.log('👤 User info verified and loaded:', {
                    user_id: this.userId,
                    user_name: this.currentUser,
                    user_email: this.userEmail
                });
                
                // Update UI with user info
                this.updateUserInfo();
                
                // Add welcome message after a short delay
                setTimeout(() => {
                    this.addWelcomeMessage();
                }, 500);
                
            } else {
                console.log('❌ Backend authentication failed');
                const errorData = await response.json().catch(() => ({}));
                console.error('Auth verification error:', errorData);
                
                // Clear invalid auth data and redirect
                this.clearIncompleteAuthData();
                window.location.href = 'login.html?error=session_expired';
            }
            
        } catch (error) {
            console.error('❌ Auth verification network error:', error);
            
            // On network error, allow access but show warning
            console.log('⚠️ Network error during auth verification, allowing local access');
            
            // Set instance variables from local data
            this.token = token;
            this.currentUser = userName;
            this.userId = userId;
            this.userEmail = userEmail;
            this.workspaceId = localStorage.getItem('proma_workspace') || 'default';
            this.agentId = localStorage.getItem('proma_agent') || 'project_manager_agent';
            
            // Update UI with user info
            this.updateUserInfo();
            
            // Add welcome message with warning
            setTimeout(() => {
                this.addWelcomeMessage();
                this.showNetworkWarning();
            }, 500);
        }
    }

    showNetworkWarning() {
        // Show a subtle warning about network connectivity
        const warningDiv = document.createElement('div');
        warningDiv.className = 'fixed top-4 right-4 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-2 rounded-lg shadow-md z-50';
        warningDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                <span class="text-sm">Không thể xác thực với server. Một số tính năng có thể bị hạn chế.</span>
            </div>
        `;
        
        document.body.appendChild(warningDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (warningDiv.parentNode) {
                warningDiv.remove();
            }
        }, 5000);
    }

    clearIncompleteAuthData() {
        const authKeys = [
            'proma_token', 'proma_user', 'proma_user_data', 'proma_workspace',
            'isLoggedIn', 'user_id', 'user_name', 'user_email', 'rememberMe',
            'login_timestamp'
        ];
        
        authKeys.forEach(key => {
            localStorage.removeItem(key);
        });
    }

    updateUserInfo() {
        console.log('👤 Updating user info...');

        // Get user data from localStorage
        const userData = localStorage.getItem('proma_user_data');
        let user = null;

        if (userData) {
            try {
                user = JSON.parse(userData);
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        }

        // Fallback to individual localStorage items
        if (!user) {
            user = {
                user_name: localStorage.getItem('user_name') || localStorage.getItem('proma_user') || 'Demo User',
                gmail: localStorage.getItem('user_email') || 'demo@example.com',
                user_id: localStorage.getItem('user_id') || 'demo-id'
            };
        }

        // Update current user reference
        this.currentUser = user.user_name;

        // Update sidebar user info
        const currentUserElement = document.getElementById('current-user');
        if (currentUserElement) {
            currentUserElement.textContent = user.user_name;
        }

        // Update header user info
        const headerCurrentUserElement = document.getElementById('header-current-user');
        if (headerCurrentUserElement) {
            headerCurrentUserElement.textContent = user.user_name;
        }

        // Update user email display if exists
        const userEmailElements = document.querySelectorAll('.user-email');
        userEmailElements.forEach(element => {
            element.textContent = user.gmail;
        });

        console.log('✅ User info updated:', user);
    }

    // User dropdown methods
    toggleUserDropdown() {
        if (this.userDropdown) {
            const isHidden = this.userDropdown.classList.contains('hidden');
            if (isHidden) {
                this.showUserDropdown();
            } else {
                this.hideUserDropdown();
            }
        }
    }

    showUserDropdown() {
        if (this.userDropdown) {
            this.userDropdown.classList.remove('hidden');
            if (this.userMenuIcon) {
                this.userMenuIcon.classList.remove('fa-chevron-up');
                this.userMenuIcon.classList.add('fa-chevron-down');
            }
        }
    }

    hideUserDropdown() {
        if (this.userDropdown) {
            this.userDropdown.classList.add('hidden');
            if (this.userMenuIcon) {
                this.userMenuIcon.classList.remove('fa-chevron-down');
                this.userMenuIcon.classList.add('fa-chevron-up');
            }
        }
    }

// Header dropdown methods
toggleHeaderDropdown() {
if (this.headerDropdown) {
    const isHidden = this.headerDropdown.classList.contains('hidden');
    if (isHidden) {
        this.showHeaderDropdown();
    } else {
        this.hideHeaderDropdown();
    }
}
}

showHeaderDropdown() {
if (this.headerDropdown) {
    this.headerDropdown.classList.remove('hidden');
}
}

hideHeaderDropdown() {
if (this.headerDropdown) {
    this.headerDropdown.classList.add('hidden');
}
}

// Logout functionality
async handleLogout() {
console.log('🚪 Logout initiated');

try {
    // Call logout API first
    console.log('🚪 Calling logout API...');
    const token = localStorage.getItem('proma_token');

    if (token) {
        const response = await fetch(`${this.apiUrl}/api/v1/auth/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        console.log('📡 Logout API response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('✅ API logout successful:', data);
            setTimeout(() => {
                this.addWelcomeMessage();
            }, 500);
        } else {
            console.log('❌ User not authenticated, redirecting to login');
            window.location.href = 'login.html';
        }
    }

    updateUserInfo() {
        console.log('👤 Updating user info...');
        
        // Get user data from localStorage
        const userData = localStorage.getItem('proma_user_data');
        let user = null;
        
        if (userData) {
            try {
                user = JSON.parse(userData);
            } catch (e) {
                console.error('Error parsing user data:', e);
            }
        }
        
        // Fallback to individual localStorage items
        if (!user) {
            user = {
                user_name: localStorage.getItem('user_name') || localStorage.getItem('proma_user') || 'Demo User',
                gmail: localStorage.getItem('user_email') || 'demo@example.com',
                user_id: localStorage.getItem('user_id') || 'demo-id'
            };
        }
        
        // Update current user reference
        this.currentUser = user.user_name;
        
        // Update sidebar user info
        const currentUserElement = document.getElementById('current-user');
        if (currentUserElement) {
            currentUserElement.textContent = user.user_name;
        }
        
        // Update header user info
        const headerCurrentUserElement = document.getElementById('header-current-user');
        if (headerCurrentUserElement) {
            headerCurrentUserElement.textContent = user.user_name;
        }
        
        // Update user email display if exists
        const userEmailElements = document.querySelectorAll('.user-email');
        userEmailElements.forEach(element => {
            element.textContent = user.gmail;
        });
        
        console.log('✅ User info updated:', user);
    }

    // User dropdown methods
    toggleUserDropdown() {
        if (this.userDropdown) {
            const isHidden = this.userDropdown.classList.contains('hidden');
            if (isHidden) {
                this.showUserDropdown();
            } else {
                this.hideUserDropdown();
            }
        }
    }

    showUserDropdown() {
        if (this.userDropdown) {
            this.userDropdown.classList.remove('hidden');
            if (this.userMenuIcon) {
                this.userMenuIcon.classList.remove('fa-chevron-up');
                this.userMenuIcon.classList.add('fa-chevron-down');
            }
        }
    }

    hideUserDropdown() {
        if (this.userDropdown) {
            this.userDropdown.classList.add('hidden');
            if (this.userMenuIcon) {
                this.userMenuIcon.classList.remove('fa-chevron-down');
                this.userMenuIcon.classList.add('fa-chevron-up');
            }
        }
    }

    // Header dropdown methods
    toggleHeaderDropdown() {
        if (this.headerDropdown) {
            const isHidden = this.headerDropdown.classList.contains('hidden');
            if (isHidden) {
                this.showHeaderDropdown();
            } else {
                this.hideHeaderDropdown();
            }
        }
    }

    showHeaderDropdown() {
        if (this.headerDropdown) {
            this.headerDropdown.classList.remove('hidden');
        }
    }

    hideHeaderDropdown() {
        if (this.headerDropdown) {
            this.headerDropdown.classList.add('hidden');
        }
    }

    // Logout functionality
    async handleLogout() {
        console.log('🚪 Logout initiated');

        try {
            // Call logout API first
            console.log('🚪 Calling logout API...');
            const token = localStorage.getItem('proma_token');
            
            if (token) {
                const response = await fetch(`${this.apiUrl}/api/v1/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                });

                console.log('📡 Logout API response status:', response.status);

                if (response.ok) {
                    const data = await response.json();
                    console.log('✅ API logout successful:', data);
                } else {
                    console.log('⚠️ API logout failed, but continuing with local logout');
                }
            } else {
                console.log('⚠️ No token found, skipping API call');
            }
        } catch (error) {
            console.error('❌ Logout API error:', error);
            console.log('⚠️ API call failed, but continuing with local logout');
        }

        // Always perform local logout
        this.performLogout();
    }

    performLogout() {
        console.log('🚪 Performing logout...');

        // Clear all localStorage data immediately (no API calls)
        const keysToRemove = [
            'user_id', 'user_email', 'user_name', 'user_company',
            'isLoggedIn', 'rememberMe',
            'proma_token', 'proma_user', 'proma_workspace',
            'proma_agent', 'proma_user_data', 'proma_settings'
        ];

        keysToRemove.forEach(key => {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.log(`Error removing ${key}:`, e);
            }
        });

        // Clear session storage as well
        try {
            sessionStorage.clear();
        } catch (e) {
            console.log('Error clearing session storage:', e);
        }

        // Reset instance variables
        this.token = null;
        this.currentUser = null;
        this.sessionId = null;
        this.workspaceId = null;

        console.log('✅ All data cleared, redirecting to login...');

        // Force redirect to login page
        setTimeout(() => {
            window.location.replace('login.html');
        }, 100);
    }

    clearAuthData() {
        // Clear instance variables
        this.token = null;
        this.currentUser = null;
        this.sessionId = null;
        this.workspaceId = null;

        // Clear localStorage
        localStorage.removeItem('proma_token');
        localStorage.removeItem('proma_user');
        localStorage.removeItem('proma_workspace');
        localStorage.removeItem('proma_agent');
        localStorage.removeItem('proma_user_data');

        console.log('🧹 Auth data cleared');
    }

    // Auth UI methods
    showAuthLoading() {
        console.log('🔄 Showing auth loading...');
        if (this.authLoading) {
            this.authLoading.classList.remove('hidden');
            this.authLoading.style.display = 'block';
        }
        if (this.loginFormContainer) {
            this.loginFormContainer.classList.add('hidden');
            this.loginFormContainer.style.display = 'none';
        }
        if (this.registerFormContainer) {
            this.registerFormContainer.classList.add('hidden');
            this.registerFormContainer.style.display = 'none';
        }
        // Auth functions removed
    }

    // Auth modal functions removed - using separate login/register pages

    loadSettings() {
        const settings = localStorage.getItem('proma_settings');
        if (settings) {
            this.settings = { ...this.settings, ...JSON.parse(settings) };
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new PromaDashboard();

    // Show dashboard by default
    setTimeout(() => {
        if (window.dashboard) {
            window.dashboard.showSection('dashboard');
        }
    }, 100);
});
