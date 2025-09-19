/**
 * Register Page Script for Proma AI
 */

class RegisterManager {
    constructor() {
        this.apiUrl = 'http://localhost:8002';
        this.init();
    }

    init() {
        console.log('📝 Register Manager initialized');
        
        // Get form elements
        this.registerForm = document.getElementById('registerForm');
        this.usernameInput = document.getElementById('username');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.confirmPasswordInput = document.getElementById('confirmPassword');
        this.submitButton = document.querySelector('button[type="submit"]');
        
        // Bind events
        if (this.registerForm) {
            this.registerForm.addEventListener('submit', (e) => this.handleRegister(e));
        }
        
        // Real-time password validation
        if (this.confirmPasswordInput) {
            this.confirmPasswordInput.addEventListener('input', () => this.validatePasswordMatch());
        }
        
        // Check if already logged in
        this.checkExistingAuth();
    }

    checkExistingAuth() {
        const token = localStorage.getItem('proma_token');
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        
        if (token && isLoggedIn === 'true') {
            console.log('🔐 User already logged in, redirecting to dashboard...');
            window.location.href = 'dashboard.html';
        }
    }

    validatePasswordMatch() {
        const password = this.passwordInput.value;
        const confirmPassword = this.confirmPasswordInput.value;
        
        if (confirmPassword && password !== confirmPassword) {
            this.confirmPasswordInput.setCustomValidity('Mật khẩu xác nhận không khớp');
            this.confirmPasswordInput.classList.add('border-red-500');
        } else {
            this.confirmPasswordInput.setCustomValidity('');
            this.confirmPasswordInput.classList.remove('border-red-500');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        console.log('📝 Register form submitted');
        
        // Get form data
        const username = this.usernameInput.value.trim();
        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;
        const confirmPassword = this.confirmPasswordInput.value;
        
        // Validate inputs
        if (!username || !email || !password || !confirmPassword) {
            this.showError('Vui lòng điền đầy đủ thông tin');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            this.showError('Email không hợp lệ');
            return;
        }
        
        if (password.length < 6) {
            this.showError('Mật khẩu phải có ít nhất 6 ký tự');
            return;
        }
        
        if (password !== confirmPassword) {
            this.showError('Mật khẩu xác nhận không khớp');
            return;
        }
        
        // Show loading state
        this.setLoadingState(true);
        
        try {
            console.log('🚀 Calling register API...');
            const response = await fetch(`${this.apiUrl}/api/v1/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_name: username,
                    gmail: email,
                    user_pass: password,
                    confirm_password: confirmPassword
                })
            });

            console.log('📡 Register response status:', response.status);
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Registration successful:', data);
                
                // Store authentication data
                this.storeAuthData(data);
                
                // Redirect to dashboard
                console.log('🔄 Redirecting to dashboard...');
                window.location.href = 'dashboard.html';
                
            } else {
                const errorData = await response.json();
                console.error('❌ Registration failed:', errorData);
                this.showError(errorData.detail || 'Đăng ký thất bại');
            }
            
        } catch (error) {
            console.error('❌ Registration error:', error);
            this.showError('Lỗi kết nối. Vui lòng kiểm tra mạng và thử lại.');
        } finally {
            this.setLoadingState(false);
        }
    }

    storeAuthData(data) {
        console.log('💾 Storing authentication data...');
        
        // Store token and user data
        localStorage.setItem('proma_token', data.access_token);
        localStorage.setItem('proma_user', data.user.user_name);
        localStorage.setItem('proma_user_data', JSON.stringify(data.user));
        localStorage.setItem('proma_workspace', data.user.workspace_id);
        
        // New authentication system
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('user_id', data.user.user_id);
        localStorage.setItem('user_name', data.user.user_name);
        localStorage.setItem('user_email', data.user.gmail);
        localStorage.setItem('rememberMe', 'false');
        
        console.log('✅ Authentication data stored');
    }

    setLoadingState(isLoading) {
        if (this.submitButton) {
            this.submitButton.disabled = isLoading;
            if (isLoading) {
                this.submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang đăng ký...';
            } else {
                this.submitButton.innerHTML = '<i class="fas fa-user-plus mr-2"></i>Sign Up';
            }
        }
        
        // Disable form inputs
        if (this.usernameInput) this.usernameInput.disabled = isLoading;
        if (this.emailInput) this.emailInput.disabled = isLoading;
        if (this.passwordInput) this.passwordInput.disabled = isLoading;
        if (this.confirmPasswordInput) this.confirmPasswordInput.disabled = isLoading;
    }

    showError(message) {
        // Remove existing error messages
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Create error message element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4';
        errorDiv.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-circle mr-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Insert before the form
        if (this.registerForm) {
            this.registerForm.parentNode.insertBefore(errorDiv, this.registerForm);
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RegisterManager();
});
