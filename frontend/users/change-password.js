// Password Change Management
class PasswordChangeManager {
    constructor() {
        this.currentUserId = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.getCurrentUser();
        this.setSidebarActivePage('profile');
    }

    bindEvents() {
        // Form submission
        $('#changePasswordForm').on('submit', (e) => {
            e.preventDefault();
            this.handlePasswordChange();
        });

        // Password strength checking
        $('#newPassword').on('input', () => {
            this.checkPasswordStrength();
            this.checkPasswordMatch();
        });

        // Password confirmation checking
        $('#confirmPassword').on('input', () => {
            this.checkPasswordMatch();
        });

        // Real-time validation
        $('#currentPassword, #newPassword, #confirmPassword').on('input', () => {
            this.hideMessages();
        });
    }

    // Get current user information
    async getCurrentUser() {
        try {
            const response = await makeApiRequest({
                url: `${APP_CONFIG.API_BASE_URL}/users/me`,
                method: 'GET'
            });

            if (response && response.data) {
                this.currentUserId = response.data.id;
                this.updateUserInfo(response.data);
            }
        } catch (error) {
            console.error('Failed to get current user:', error);
            this.showError('Failed to load user information. Please refresh the page.');
        }
    }

    // Update user information display
    updateUserInfo(user) {
        // You can add user info display here if needed
        console.log('Current user:', user);
    }

    // Handle password change submission
    async handlePasswordChange() {
        if (!this.validateForm()) {
            return;
        }

        const currentPassword = $('#currentPassword').val();
        const newPassword = $('#newPassword').val();

        // Show loading state
        const submitBtn = $('#submitBtn');
        const originalText = submitBtn.html();
        submitBtn.html('<i class="fas fa-spinner fa-spin mr-2"></i>Changing Password...').prop('disabled', true);

        try {
            const response = await makeApiRequest({
                url: `${APP_CONFIG.API_BASE_URL}/users/${this.currentUserId}/change-password`,
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            if (response && response.success) {
                this.showSuccess('Password changed successfully!');
                this.resetForm();
            } else {
                this.showError('Failed to change password. Please try again.');
            }
        } catch (error) {
            console.error('Password change error:', error);
            
            if (error.status === 400) {
                this.showError('Invalid current password. Please check your current password and try again.');
            } else if (error.status === 401) {
                this.showError('Authentication failed. Please log in again.');
                // Redirect to login
                setTimeout(() => {
                    window.location.href = '../index.html';
                }, 2000);
            } else {
                this.showError('An error occurred while changing your password. Please try again.');
            }
        } finally {
            // Restore button state
            submitBtn.html(originalText).prop('disabled', false);
        }
    }

    // Validate form inputs
    validateForm() {
        const currentPassword = $('#currentPassword').val().trim();
        const newPassword = $('#newPassword').val().trim();
        const confirmPassword = $('#confirmPassword').val().trim();

        // Check if all fields are filled
        if (!currentPassword || !newPassword || !confirmPassword) {
            this.showError('Please fill in all password fields.');
            return false;
        }

        // Check if new password is different from current password
        if (currentPassword === newPassword) {
            this.showError('New password must be different from your current password.');
            return false;
        }

        // Check password strength
        const strength = this.getPasswordStrength(newPassword);
        if (strength === 'weak') {
            this.showError('Password is too weak. Please choose a stronger password.');
            return false;
        }

        // Check password match
        if (newPassword !== confirmPassword) {
            this.showError('New password and confirmation password do not match.');
            return false;
        }

        return true;
    }

    // Check password strength
    checkPasswordStrength() {
        const password = $('#newPassword').val();
        const strength = this.getPasswordStrength(password);
        const strengthBar = $('#passwordStrength');
        const strengthText = $('#passwordStrengthText');

        // Remove all strength classes
        strengthBar.removeClass('weak fair good strong');

        if (password.length === 0) {
            strengthText.text('Password strength will appear here');
            return;
        }

        // Add appropriate strength class
        strengthBar.addClass(strength);

        // Update strength text
        const strengthMessages = {
            weak: 'Weak password - Add more characters and complexity',
            fair: 'Fair password - Add more complexity',
            good: 'Good password - Consider adding special characters',
            strong: 'Strong password - Excellent!'
        };

        strengthText.text(strengthMessages[strength]);
    }

    // Get password strength level
    getPasswordStrength(password) {
        if (password.length < 6) return 'weak';
        
        let score = 0;
        
        // Length contribution
        if (password.length >= 8) score += 1;
        if (password.length >= 12) score += 1;
        
        // Character variety contribution
        if (/[a-z]/.test(password)) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[^A-Za-z0-9]/.test(password)) score += 1;
        
        // Determine strength level
        if (score <= 2) return 'weak';
        if (score <= 3) return 'fair';
        if (score <= 4) return 'good';
        return 'strong';
    }

    // Check if passwords match
    checkPasswordMatch() {
        const newPassword = $('#newPassword').val();
        const confirmPassword = $('#confirmPassword').val();
        const matchError = $('#passwordMatchError');

        if (confirmPassword.length > 0 && newPassword !== confirmPassword) {
            matchError.removeClass('hidden');
        } else {
            matchError.addClass('hidden');
        }
    }

    // Toggle password visibility
    togglePasswordVisibility(fieldId) {
        const field = $(`#${fieldId}`);
        const toggle = $(`#${fieldId}Toggle`);
        
        if (field.attr('type') === 'password') {
            field.attr('type', 'text');
            toggle.removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            field.attr('type', 'password');
            toggle.removeClass('fa-eye-slash').addClass('fa-eye');
        }
    }

    // Show error message
    showError(message) {
        this.hideMessages();
        $('#errorText').text(message);
        $('#errorMessage').removeClass('hidden');
        $('#errorMessage')[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Show success message
    showSuccess(message) {
        this.hideMessages();
        $('#successText').text(message);
        $('#successMessage').removeClass('hidden');
        $('#successMessage')[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Hide all messages
    hideMessages() {
        $('#errorMessage').addClass('hidden');
        $('#successMessage').addClass('hidden');
    }

    // Reset form
    resetForm() {
        $('#changePasswordForm')[0].reset();
        $('#passwordStrength').removeClass('weak fair good strong');
        $('#passwordStrengthText').text('Password strength will appear here');
        $('#passwordMatchError').addClass('hidden');
        this.hideMessages();
        
        // Reset password fields to password type
        $('#currentPassword, #newPassword, #confirmPassword').attr('type', 'password');
        $('#currentPasswordToggle, #newPasswordToggle, #confirmPasswordToggle')
            .removeClass('fa-eye-slash')
            .addClass('fa-eye');
    }

    // Set sidebar active page
    setSidebarActivePage(page) {
        if (window.setSidebarActivePage) {
            window.setSidebarActivePage(page);
        }
    }
}

// Global functions for HTML onclick handlers
window.togglePasswordVisibility = function(fieldId) {
    if (window.passwordChangeManager) {
        window.passwordChangeManager.togglePasswordVisibility(fieldId);
    }
};

window.resetForm = function() {
    if (window.passwordChangeManager) {
        window.passwordChangeManager.resetForm();
    }
};

// Initialize when DOM is loaded
$(document).ready(function() {
    window.passwordChangeManager = new PasswordChangeManager();
});
