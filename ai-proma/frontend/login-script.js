/**
 * Login Page Script for Proma AI
 */

class LoginManager {
    constructor() {
        this.apiUrl = 'http://localhost:8002';
        this.init();
    }

    init() {
        console.log('🔐 Login Manager initialized');
        
        // Get form elements
        this.loginForm = document.getElementById('loginForm');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.rememberCheckbox = document.getElementById('remember');
        this.submitButton = document.querySelector('button[type="submit"]');
        
        // Bind events
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }
        
        // Check for error messages in URL
        this.checkUrlParams();
        
        // Check if already logged in
        this.checkExistingAuth();
    }

    checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const error = urlParams.get('error');
        
        if (error) {
            let message = '';
            switch (error) {
                case 'login_failed':
                    message = 'Đăng nhập thất bại. Vui lòng kiểm tra email và mật khẩu.';
                    break;
                case 'network_error':
                    message = 'Lỗi kết nối. Vui lòng thử lại.';
                    break;
                case 'unauthorized':
                    message = 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.';
                    break;
                default:
                    message = 'Có lỗi xảy ra. Vui lòng thử lại.';
            }
            this.showError(message);
        }
    }

    checkExistingAuth() {
        const token = localStorage.getItem('proma_token');
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        
        if (token && isLoggedIn === 'true') {
            console.log('🔐 User already logged in, redirecting to dashboard...');
            window.location.href = 'dashboard.html';
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        console.log('🔐 Login form submitted');
        
        // Get form data
        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;
        const remember = this.rememberCheckbox.checked;
        
        // Validate inputs
        if (!email || !password) {
            this.showError('Vui lòng nhập đầy đủ email và mật khẩu');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showError('Email không hợp lệ');
            return;
        }
        
        // Show loading state
        this.setLoadingState(true);
        
        try {
            console.log('🚀 Calling login API...');
            const response = await fetch(`${this.apiUrl}/api/v1/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    gmail: email,
                    user_pass: password
                })
            });

            console.log('📡 Login response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Login successful:', data);
                
                // Validate response data
                if (data.access_token && data.user) {
                    // Store authentication data
                    this.storeAuthData(data, remember);
                    
                    // Show success message
                    this.showSuccess('Đăng nhập thành công! Đang chuyển hướng...');
                    
                    // Redirect to dashboard after short delay
                    setTimeout(() => {
                        console.log('🔄 Redirecting to dashboard...');
                        window.location.href = 'dashboard.html';
                    }, 1000);
                } else {
                    console.error('❌ Invalid response data:', data);
                    this.showError('Phản hồi từ server không hợp lệ');
                }
                
            } else {
                let errorMessage = 'Đăng nhập thất bại';
                
                try {
                    const errorData = await response.json();
                    console.error('❌ Login failed:', errorData);
                    
                    if (response.status === 422) {
                        errorMessage = 'Dữ liệu đầu vào không hợp lệ';
                    } else if (response.status === 401) {
                        errorMessage = 'Email hoặc mật khẩu không đúng';
                    } else {
                        errorMessage = errorData.detail || 'Đăng nhập thất bại';
                    }
                } catch (e) {
                    console.error('❌ Error parsing error response:', e);
                    errorMessage = `Lỗi ${response.status}: Không thể đăng nhập`;
                }
                
                this.showError(errorMessage);
            }
            
        } catch (error) {
            console.error('❌ Login error:', error);
            this.showError('Lỗi kết nối. Vui lòng kiểm tra mạng và thử lại.');
        } finally {
            this.setLoadingState(false);
        }
    }

    storeAuthData(data, remember) {
        console.log('💾 Storing authentication data...');
        console.log('📊 User data received:', data.user);
        
        // Clear any existing auth data first
        this.clearAuthData();
        
        // Store token and user data
        localStorage.setItem('proma_token', data.access_token);
        localStorage.setItem('proma_user', data.user.user_name);
        localStorage.setItem('proma_user_data', JSON.stringify(data.user));
        localStorage.setItem('proma_workspace', data.user.workspace_id || 'default');
        
        // New authentication system - store individual fields for easy access
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('user_id', data.user.user_id);
        localStorage.setItem('user_name', data.user.user_name);
        localStorage.setItem('user_email', data.user.gmail);
        localStorage.setItem('rememberMe', remember ? 'true' : 'false');
        
        // Store login timestamp
        localStorage.setItem('login_timestamp', new Date().toISOString());
        
        console.log('✅ Authentication data stored successfully');
        console.log('📋 Stored data:', {
            user_id: data.user.user_id,
            user_name: data.user.user_name,
            user_email: data.user.gmail,
            isLoggedIn: 'true'
        });
    }

    clearAuthData() {
        // Clear all authentication related data
        const authKeys = [
            'proma_token', 'proma_user', 'proma_user_data', 'proma_workspace',
            'isLoggedIn', 'user_id', 'user_name', 'user_email', 'rememberMe',
            'login_timestamp'
        ];
        
        authKeys.forEach(key => {
            localStorage.removeItem(key);
        });
    }

    setLoadingState(isLoading) {
        if (this.submitButton) {
            this.submitButton.disabled = isLoading;
            if (isLoading) {
                this.submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang đăng nhập...';
            } else {
                this.submitButton.innerHTML = '<i class="fas fa-sign-in-alt mr-2"></i>Sign In';
            }
        }
        
        // Disable form inputs
        if (this.emailInput) this.emailInput.disabled = isLoading;
        if (this.passwordInput) this.passwordInput.disabled = isLoading;
        if (this.rememberCheckbox) this.rememberCheckbox.disabled = isLoading;
    }

    showError(message) {
        this.showMessage(message, 'error');
    }

    showSuccess(message) {
        this.showMessage(message, 'success');
    }

    showMessage(message, type) {
        // Remove existing messages
        const existingMessage = document.querySelector('.error-message, .success-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Create message element
        const messageDiv = document.createElement('div');
        if (type === 'success') {
            messageDiv.className = 'success-message bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4';
            messageDiv.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-check-circle mr-2"></i>
                    <span>${message}</span>
                </div>
            `;
        } else {
            messageDiv.className = 'error-message bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4';
            messageDiv.innerHTML = `
                <div class="flex items-center">
                    <i class="fas fa-exclamation-circle mr-2"></i>
                    <span>${message}</span>
                </div>
            `;
        }
        
        // Insert before the form
        if (this.loginForm) {
            this.loginForm.parentNode.insertBefore(messageDiv, this.loginForm);
        }
        
        // Auto-remove after 5 seconds (3 seconds for success)
        const timeout = type === 'success' ? 3000 : 5000;
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, timeout);
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LoginManager();
});
