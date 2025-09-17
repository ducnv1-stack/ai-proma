// Global function for back navigation
function goBack() {
    window.location.href = 'demo.html';
}

class FaramexChat {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.token = null;
        this.sessionId = null;
        this.workspaceId = null;
        this.agentId = 'facebook_marketing_agent';
        this.currentUser = null;
        this.attachedImages = [];
        this.settings = {
            autoScroll: true,
            soundNotifications: false
        };

        this.initializeElements();
        this.bindEvents();
        this.loadSettings();
        this.checkAuthentication();
    }

    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.attachBtn = document.getElementById('attach-btn');
        this.fileInput = document.getElementById('file-input');
        this.attachedImagesContainer = document.getElementById('attached-images');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.charCount = document.getElementById('char-count');

        // Modal elements
        this.loginModal = document.getElementById('login-modal');
        this.settingsModal = document.getElementById('settings-modal');
        this.loginForm = document.getElementById('login-form');

        // Header elements
        this.agentName = document.getElementById('agent-name');
        this.agentStatus = document.getElementById('agent-status');
        this.settingsBtn = document.getElementById('settings-btn');
        this.logoutBtn = document.getElementById('logout-btn');

        // Settings elements
        this.apiUrlInput = document.getElementById('api-url');
        this.autoScrollCheckbox = document.getElementById('auto-scroll');
        this.soundNotificationsCheckbox = document.getElementById('sound-notifications');
    }

    bindEvents() {
        // Message input events
        this.messageInput.addEventListener('input', () => this.handleInputChange());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // File attachment
        this.attachBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelection(e));
        
        // Modal events
        this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        this.settingsBtn.addEventListener('click', () => this.showSettings());
        this.logoutBtn.addEventListener('click', () => this.logout());
        
        // Settings modal
        document.getElementById('close-settings').addEventListener('click', () => this.hideSettings());
        document.getElementById('save-settings').addEventListener('click', () => this.saveSettings());
        
        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === this.loginModal) this.hideLogin();
            if (e.target === this.settingsModal) this.hideSettings();
        });
    }

    handleInputChange() {
        const length = this.messageInput.value.length;
        this.charCount.textContent = `${length}/4000`;
        
        // Auto-resize textarea
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        
        // Enable/disable send button
        this.sendBtn.disabled = length === 0 && this.attachedImages.length === 0;
    }

    handleKeyDown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!this.sendBtn.disabled) {
                this.sendMessage();
            }
        }
    }

    handleFileSelection(e) {
        const files = Array.from(e.target.files);
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                this.addAttachedImage(file);
            }
        });
        e.target.value = ''; // Reset input
    }

    addAttachedImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const imageData = {
                file: file,
                url: e.target.result,
                id: Date.now() + Math.random()
            };
            
            this.attachedImages.push(imageData);
            this.renderAttachedImages();
            this.handleInputChange(); // Update send button state
        };
        reader.readAsDataURL(file);
    }

    removeAttachedImage(imageId) {
        this.attachedImages = this.attachedImages.filter(img => img.id !== imageId);
        this.renderAttachedImages();
        this.handleInputChange();
    }

    renderAttachedImages() {
        this.attachedImagesContainer.innerHTML = '';
        this.attachedImages.forEach(image => {
            const imageContainer = document.createElement('div');
            imageContainer.className = 'attached-image';
            imageContainer.innerHTML = `
                <img src="${image.url}" alt="Attached image">
                <button class="remove-image" onclick="chat.removeAttachedImage(${image.id})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            this.attachedImagesContainer.appendChild(imageContainer);
        });
    }

    async uploadImages() {
        // For demo purposes, we'll use placeholder URLs
        // In production, you would upload to your image service
        const imageUrls = [];
        
        for (const image of this.attachedImages) {
            // Simulate image upload - replace with actual upload logic
            const formData = new FormData();
            formData.append('image', image.file);
            
            try {
                // This would be your actual image upload endpoint
                // const response = await fetch(`${this.apiUrl}/upload-image`, {
                //     method: 'POST',
                //     body: formData
                // });
                // const result = await response.json();
                // imageUrls.push(result.url);
                
                // For demo, use data URL
                imageUrls.push(image.url);
            } catch (error) {
                console.error('Error uploading image:', error);
            }
        }
        
        return imageUrls;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message && this.attachedImages.length === 0) return;

        // Upload images if any
        const imageUrls = await this.uploadImages();

        // Add user message to chat
        this.addMessage('user', message, imageUrls);

        // Clear input
        this.messageInput.value = '';
        this.attachedImages = [];
        this.renderAttachedImages();
        this.handleInputChange();

        // Show typing indicator
        this.showTypingIndicator();

        try {
            await this.sendToAPI(message, imageUrls);
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('agent', 'Xin lỗi, đã có lỗi xảy ra khi xử lý tin nhắn của bạn. Vui lòng thử lại.');
            console.error('Error sending message:', error);
        }
    }

    async sendToAPI(message, images = []) {
        const payload = {
            message: message,
            images: images,
            files: [],
            metadata: {}
        };

        const response = await fetch(`${this.apiUrl}/api/v1/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Handle streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let agentMessage = '';
        let messageElement = null;

        this.hideTypingIndicator();

        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;
                    
                    try {
                        // Try to parse as JSON first
                        const jsonData = JSON.parse(data);
                        if (jsonData.content) {
                            agentMessage += jsonData.content;
                        }
                        
                        // Create or update message element
                        if (!messageElement) {
                            messageElement = this.addMessage('agent', agentMessage);
                        } else {
                            this.updateMessage(messageElement, agentMessage);
                        }
                        
                        if (this.settings.autoScroll) {
                            this.scrollToBottom();
                        }
                    } catch (e) {
                        // Handle non-JSON data - treat as plain text
                        agentMessage += data;
                        if (!messageElement) {
                            messageElement = this.addMessage('agent', agentMessage);
                        } else {
                            this.updateMessage(messageElement, agentMessage);
                        }
                    }
                }
            }
        }

        if (this.settings.soundNotifications) {
            this.playNotificationSound();
        }
    }

    addMessage(sender, content, images = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const time = new Date().toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        let imagesHtml = '';
        if (images && images.length > 0) {
            imagesHtml = `
                <div class="message-images">
                    ${images.map(url => `<img src="${url}" alt="Image" onclick="chat.openImageModal('${url}')">`).join('')}
                </div>
            `;
        }

        messageDiv.innerHTML = `
            ${sender === 'agent' ? '<div class="agent-avatar"><i class="fas fa-robot"></i></div>' : ''}
            <div class="message-content">
                <p>${this.formatMessage(content)}</p>
                ${imagesHtml}
                <div class="message-time">${time}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        
        if (this.settings.autoScroll) {
            this.scrollToBottom();
        }

        return messageDiv;
    }

    updateMessage(messageElement, content) {
        const contentElement = messageElement.querySelector('.message-content p');
        if (contentElement) {
            contentElement.innerHTML = this.formatMessage(content);
        }
    }

    formatMessage(text) {
        // Basic text formatting
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    playNotificationSound() {
        // Create a simple notification sound
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    }

    // Authentication methods
    async handleLogin(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        this.workspaceId = document.getElementById('workspace-id').value;
        this.agentId = document.getElementById('agent-select').value;

        try {
            // For demo purposes, we'll simulate authentication
            // In production, you would call your authentication endpoint
            this.token = 'demo-token-' + Date.now();
            this.currentUser = { username, workspaceId: this.workspaceId };
            
            // Create session
            await this.createSession();
            
            this.hideLogin();
            this.updateUI();
            
        } catch (error) {
            alert('Đăng nhập thất bại: ' + error.message);
        }
    }

    async createSession() {
        try {
            const response = await fetch(`${this.apiUrl}/api/v1/session/create`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({
                    metadata: {
                        client: 'web-chat',
                        version: '1.0.0'
                    }
                })
            });

            if (!response.ok) {
                throw new Error('Failed to create session');
            }

            const result = await response.json();
            this.sessionId = result.session_id;
            
        } catch (error) {
            console.error('Error creating session:', error);
            // For demo, create a mock session
            this.sessionId = 'demo-session-' + Date.now();
        }
    }

    checkAuthentication() {
        const savedToken = localStorage.getItem('faramex_token');
        const savedUser = localStorage.getItem('faramex_user');
        
        if (savedToken && savedUser) {
            this.token = savedToken;
            this.currentUser = JSON.parse(savedUser);
            this.workspaceId = this.currentUser.workspaceId;
            this.updateUI();
            this.createSession();
        } else {
            this.showLogin();
        }
    }

    showLogin() {
        this.loginModal.classList.add('show');
    }

    hideLogin() {
        this.loginModal.classList.remove('show');
        // Save authentication
        localStorage.setItem('faramex_token', this.token);
        localStorage.setItem('faramex_user', JSON.stringify(this.currentUser));
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        this.sessionId = null;
        localStorage.removeItem('faramex_token');
        localStorage.removeItem('faramex_user');
        this.showLogin();
        this.clearChat();
    }

    clearChat() {
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="agent-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <p>Xin chào! Tôi là FARAMEX Marketing Agent. Tôi có thể giúp bạn tạo nội dung marketing, thiết kế hình ảnh và tư vấn chiến lược Facebook Marketing. Hãy bắt đầu cuộc trò chuyện!</p>
                </div>
            </div>
        `;
    }

    updateUI() {
        if (this.currentUser) {
            this.agentStatus.textContent = 'Online';
            this.agentStatus.className = 'status-online';
        }
    }

    // Settings methods
    showSettings() {
        this.settingsModal.classList.add('show');
        this.apiUrlInput.value = this.apiUrl;
        this.autoScrollCheckbox.checked = this.settings.autoScroll;
        this.soundNotificationsCheckbox.checked = this.settings.soundNotifications;
    }

    hideSettings() {
        this.settingsModal.classList.remove('show');
    }

    saveSettings() {
        this.apiUrl = this.apiUrlInput.value;
        this.settings.autoScroll = this.autoScrollCheckbox.checked;
        this.settings.soundNotifications = this.soundNotificationsCheckbox.checked;
        
        localStorage.setItem('faramex_settings', JSON.stringify({
            apiUrl: this.apiUrl,
            ...this.settings
        }));
        
        this.hideSettings();
    }

    loadSettings() {
        const savedSettings = localStorage.getItem('faramex_settings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            this.apiUrl = settings.apiUrl || this.apiUrl;
            this.settings = { ...this.settings, ...settings };
        }
    }

    openImageModal(imageUrl) {
        // Simple image modal - you can enhance this
        const modal = document.createElement('div');
        modal.className = 'modal show';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 80%; max-height: 80%;">
                <div class="modal-header">
                    <h2>Hình ảnh</h2>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body" style="text-align: center;">
                    <img src="${imageUrl}" style="max-width: 100%; max-height: 70vh; border-radius: 10px;">
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chat = new FaramexChat();
});
