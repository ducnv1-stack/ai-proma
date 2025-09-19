// Dashboard Navigation and Chat Integration
class PromaDashboard {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
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
            }, 100);
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
            const response = await fetch(`${this.apiUrl}/api/v1/chat-stream`, {
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
        const messageElement = this.addMessage('agent', '');
        const contentDiv = messageElement.querySelector('.message-bubble');
        
        let currentText = '';
        const words = text.split(' ');
        
        for (let i = 0; i < words.length; i++) {
            currentText += (i > 0 ? ' ' : '') + words[i];
            contentDiv.innerHTML = this.formatMessage(currentText);
            this.scrollToBottom();
            
            // Random delay between 50-150ms per word
            await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 50));
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
                <p>Xin chào ${this.currentUser || 'bạn'}! Tôi là Proma Project Manager Agent. Tôi có thể giúp bạn quản lý dự án, tạo task, phân công công việc và theo dõi tiến độ. Hãy bắt đầu cuộc trò chuyện!</p>
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
        this.showAuthLoading();

        const formData = new FormData(e.target);
        const username = formData.get('username');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        const workspaceId = 'default';

        if (password !== confirmPassword) {
            this.hideAuthLoading();
            this.showRegisterForm();
            this.showAuthError('Mật khẩu xác nhận không khớp.');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/api/v1/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_name: username,
                    user_pass: password,
                    confirm_password: confirmPassword,
                    workspace_id: workspaceId
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
                this.showRegisterForm();
                this.showAuthError(data.detail || 'Đăng ký thất bại. Vui lòng thử lại.');
            }
        } catch (error) {
            console.error('Register error:', error);
            this.hideAuthLoading();
            this.showRegisterForm();
            this.showAuthError('Có lỗi xảy ra khi đăng ký. Vui lòng thử lại.');
        }
    }

    checkAuthentication() {
        const token = localStorage.getItem('proma_token');
        const user = localStorage.getItem('proma_user');

        if (token && user) {
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
        
        // Update online status to green color
        const onlineStatusEl = document.querySelector('#current-user').nextElementSibling;
        if (onlineStatusEl) {
            onlineStatusEl.textContent = 'Online';
            onlineStatusEl.style.color = '#10b981'; // Green color
            onlineStatusEl.classList.remove('text-gray-500');
            onlineStatusEl.classList.add('text-green-500');
        }
    }

    // Auth UI methods
    showAuthLoading() {
        if (this.authLoading) this.authLoading.classList.remove('hidden');
        if (this.loginFormContainer) this.loginFormContainer.classList.add('hidden');
        if (this.registerFormContainer) this.registerFormContainer.classList.add('hidden');
        this.hideAuthError();
    }

    hideAuthLoading() {
        if (this.authLoading) this.authLoading.classList.add('hidden');
    }

    showLoginForm() {
        this.hideAuthLoading();
        if (this.loginFormContainer) this.loginFormContainer.classList.remove('hidden');
        if (this.registerFormContainer) this.registerFormContainer.classList.add('hidden');
        this.hideAuthError();
    }

    showRegisterForm() {
        this.hideAuthLoading();
        if (this.loginFormContainer) this.loginFormContainer.classList.add('hidden');
        if (this.registerFormContainer) this.registerFormContainer.classList.remove('hidden');
        this.hideAuthError();
    }

    showAuthError(message) {
        if (this.authError) {
            this.authError.textContent = message;
            this.authError.classList.remove('hidden');
        }
    }

    hideAuthError() {
        if (this.authError) {
            this.authError.classList.add('hidden');
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
