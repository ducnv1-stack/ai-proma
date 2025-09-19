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

        // Modal elements
        this.authModal = document.getElementById('auth-modal');
        this.loginForm = document.getElementById('login-form');
        this.registerForm = document.getElementById('register-form');
        this.loginFormContainer = document.getElementById('login-form-container');
        this.registerFormContainer = document.getElementById('register-form-container');
        this.authLoading = document.getElementById('auth-loading');
        this.authError = document.getElementById('auth-error');

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

        // Global functions for form switching
        window.showLoginForm = () => this.showLoginForm();
        window.showRegisterForm = () => this.showRegisterForm();

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
                this.handleLogout();
            });
        }

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
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.remove('hidden');
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
        this.hideAuthError(); // Hide any previous messages
        this.showAuthLoading();

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

                this.authModal.style.display = 'none';
                this.updateUserInfo();
                this.clearChat();
            } else {
                this.hideAuthLoading();
                this.showLoginForm();
                this.showAuthError(data.detail || 'Đăng nhập thất bại. Vui lòng thử lại.');
            }
        } catch (error) {
            console.error('Login error:', error);
            this.hideAuthLoading();
            this.showLoginForm();
            this.showAuthError('Có lỗi xảy ra khi đăng nhập. Vui lòng thử lại.');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        console.log('📝 Register form submitted');

        this.hideAuthError(); // Hide any previous error messages
        this.showAuthLoading();

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

                // Hide loading and show login form
                this.hideAuthLoading();
                this.showLoginForm();

                // Show success message
                this.showAuthSuccess(`🎉 Đăng ký thành công! Vui lòng đăng nhập với tài khoản "${username}".`);

                // Auto-fill username in login form
                const loginUsernameInput = document.getElementById('login-username');
                if (loginUsernameInput) {
                    loginUsernameInput.value = username;
                    loginUsernameInput.focus();
                }

            } else {
                console.log('❌ Registration failed:', data.detail);
                this.hideAuthLoading();
                this.showRegisterForm();
                this.showAuthError(data.detail || 'Đăng ký thất bại. Vui lòng thử lại.');
            }
        } catch (error) {
            console.error('❌ Register error:', error);
            this.hideAuthLoading();
            this.showRegisterForm();
            this.showAuthError('Có lỗi xảy ra khi đăng ký. Vui lòng kiểm tra kết nối mạng và thử lại.');
        }
    }

    checkAuthentication() {
        console.log('🔐 Checking authentication...');
        const token = localStorage.getItem('proma_token');
        const user = localStorage.getItem('proma_user');

        if (token && user) {
            console.log('✅ User authenticated:', user);
            this.token = token;
            this.currentUser = user;
            this.workspaceId = localStorage.getItem('proma_workspace') || 'default';
            this.agentId = localStorage.getItem('proma_agent') || 'project_manager_agent';
            this.authModal.style.display = 'none';
            this.updateUserInfo();

            // Add welcome message
            setTimeout(() => {
                this.addWelcomeMessage();
            }, 500);
        } else {
            console.log('❌ User not authenticated, showing login form');
            this.authModal.style.display = 'flex';
            this.showLoginForm();
        }
    }

    updateUserInfo() {
        if (this.currentUserEl) {
            this.currentUserEl.textContent = this.currentUser || 'User';
            // Set user name color to black
            this.currentUserEl.style.color = '#000000';
            this.currentUserEl.classList.remove('text-gray-900');
            this.currentUserEl.classList.add('text-black');
        }

        // Update header user info
        if (this.headerCurrentUser) {
            this.headerCurrentUser.textContent = this.currentUser || 'User';
        }

        // Update online status to green color
        const onlineStatusEl = document.querySelector('#current-user').nextElementSibling;
        if (onlineStatusEl) {
            onlineStatusEl.textContent = 'Online';
            onlineStatusEl.style.color = '#10b981'; // Green color
            onlineStatusEl.classList.remove('text-gray-500');
            onlineStatusEl.classList.add('text-green-500');
        }
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
            // Call logout API endpoint
            const response = await fetch(`${this.apiUrl}/api/v1/auth/logout`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();
            console.log('🚪 Logout response:', data);

            // Clear all stored data
            this.clearAuthData();

            // Hide dropdowns
            this.hideUserDropdown();
            this.hideHeaderDropdown();

            // Clear chat
            this.clearChat();

            // Show auth modal
            this.authModal.style.display = 'flex';
            this.showLoginForm();

            // Show success message
            this.showAuthSuccess('Đăng xuất thành công!');

            console.log('✅ Logout completed successfully');

        } catch (error) {
            console.error('❌ Logout error:', error);

            // Even if API call fails, clear local data
            this.clearAuthData();
            this.authModal.style.display = 'flex';
            this.showLoginForm();
            this.showAuthError('Đã đăng xuất (có lỗi kết nối server)');
        }
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
        this.hideAuthError();
    }

    hideAuthLoading() {
        console.log('⏹️ Hiding auth loading...');
        if (this.authLoading) {
            this.authLoading.classList.add('hidden');
            this.authLoading.style.display = 'none';
        }
    }

    showLoginForm() {
        console.log('📝 Showing login form...');
        this.hideAuthLoading();
        if (this.loginFormContainer) {
            this.loginFormContainer.classList.remove('hidden');
            this.loginFormContainer.style.display = 'block';
        }
        if (this.registerFormContainer) {
            this.registerFormContainer.classList.add('hidden');
            this.registerFormContainer.style.display = 'none';
        }
        // Don't hide success message when showing login form after successful registration
        // this.hideAuthError();
    }

    showRegisterForm() {
        console.log('📝 Showing register form...');
        this.hideAuthLoading();
        if (this.loginFormContainer) {
            this.loginFormContainer.classList.add('hidden');
            this.loginFormContainer.style.display = 'none';
        }
        if (this.registerFormContainer) {
            this.registerFormContainer.classList.remove('hidden');
            this.registerFormContainer.style.display = 'block';
        }
        this.hideAuthError();
    }

    showAuthError(message) {
        console.log('❌ Showing error:', message);
        if (this.authError) {
            this.authError.textContent = message;
            this.authError.classList.remove('hidden');
            this.authError.style.display = 'block';
            this.authError.className = 'mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded';
        }
    }

    showAuthSuccess(message) {
        console.log('✅ Showing success:', message);
        if (this.authError) {
            this.authError.textContent = message;
            this.authError.classList.remove('hidden');
            this.authError.style.display = 'block';
            this.authError.className = 'mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded';
        }
    }

    hideAuthError() {
        console.log('🙈 Hiding auth error/success message');
        if (this.authError) {
            this.authError.classList.add('hidden');
            this.authError.style.display = 'none';
        }
    }

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
