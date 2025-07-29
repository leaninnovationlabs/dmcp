// Authentication Management Module
class AuthManager {
    constructor() {
        this.tokenKey = 'dbmcp_bearer_token';
        this.init();
    }

    init() {
        // Initialize but don't immediately check authentication
        // Authentication will be checked when first API call is made
    }

    // Get token from localStorage
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    // Set token in localStorage
    setToken(token) {
        localStorage.setItem(this.tokenKey, token);
    }

    // Remove token from localStorage
    clearToken() {
        localStorage.removeItem(this.tokenKey);
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    }

    // Check authentication and prompt for login if needed
    checkAuthentication() {
        if (!this.isAuthenticated()) {
            this.showLoginDialog();
            return false;
        }
        return true;
    }

    // Show login dialog
    showLoginDialog() {
        // Create modal if it doesn't exist
        if (!document.getElementById('authModal')) {
            this.createLoginModal();
        }
        
        $('#authModal').removeClass('hidden').addClass('flex');
        $('#tokenInput').focus();
    }

    // Hide login dialog
    hideLoginDialog() {
        $('#authModal').addClass('hidden').removeClass('flex');
        $('#tokenInput').val('');
        $('#authError').hide();
    }

    // Create login modal HTML
    createLoginModal() {
        const modalHTML = `
            <!-- Authentication Modal -->
            <div id="authModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 hidden items-center justify-center">
                <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
                    <!-- Modal Header -->
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-semibold text-gray-900">Authentication Required</h3>
                        <p class="text-sm text-gray-600 mt-1">Please enter your bearer token to access the application</p>
                    </div>
                    
                    <!-- Modal Body -->
                    <div class="px-6 py-4">
                        <form id="authForm">
                            <div class="mb-4">
                                <label for="tokenInput" class="block text-sm font-medium text-gray-700 mb-2">Bearer Token</label>
                                <input type="password" id="tokenInput" 
                                       class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                       placeholder="Enter your bearer token"
                                       required>
                            </div>
                            
                            <div id="authError" class="mb-4 p-3 bg-red-100 border border-red-300 text-red-700 rounded-md hidden">
                                <i class="fas fa-exclamation-circle mr-2"></i>
                                <span id="authErrorMessage">Invalid token. Please try again.</span>
                            </div>
                            
                            <div class="flex justify-end space-x-3">
                                <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    <i class="fas fa-sign-in-alt mr-2"></i>Login
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Bind events
        $('#authForm').on('submit', (e) => {
            e.preventDefault();
            const token = $('#tokenInput').val().trim();
            if (token) {
                this.validateAndSetToken(token);
            }
        });
    }

    // Validate token and set if valid
    validateAndSetToken(token) {
        // Set token temporarily for validation
        this.setToken(token);
        
        // Test the token with a simple API call
        this.makeAuthenticatedRequest({
            url: `${APP_CONFIG.API_BASE_URL}/health`,
            method: 'GET',
            success: () => {
                // Token is valid
                $('#authError').hide();
                this.hideLoginDialog();
                this.showNotification('Authentication successful!', 'success');
                // Refresh the current page to load data
                window.location.reload();
            },
            error: (xhr) => {
                // Token is invalid
                this.clearToken();
                if (xhr.status === 401) {
                    $('#authErrorMessage').text('Invalid or expired token. Please check your bearer token.');
                } else {
                    $('#authErrorMessage').text('Unable to validate token. Please try again.');
                }
                $('#authError').show();
                $('#tokenInput').focus().select();
            }
        });
    }

    // Logout user
    logout() {
        this.clearToken();
        this.showNotification('Logged out successfully', 'info');
        // Show login dialog again
        setTimeout(() => {
            this.showLoginDialog();
        }, 500);
    }

    // Make authenticated API request
    makeAuthenticatedRequest(options) {
        const token = this.getToken();
        
        if (!token) {
            this.showLoginDialog();
            return $.Deferred().reject().promise();
        }

        // Add authorization header
        const headers = options.headers || {};
        headers['Authorization'] = `Bearer ${token}`;
        
        const requestOptions = {
            ...options,
            headers: headers,
            error: (xhr, status, error) => {
                // Handle 401 authentication errors
                if (xhr.status === 401) {
                    this.clearToken();
                    this.showLoginDialog();
                    return;
                }
                
                // Call original error handler if provided
                if (options.error) {
                    options.error(xhr, status, error);
                }
            }
        };

        return $.ajax(requestOptions);
    }

    // Helper method to show notifications
    showNotification(message, type = 'info') {
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500',
            warning: 'bg-yellow-500'
        };

        // Create status messages container if it doesn't exist
        if (!document.getElementById('statusMessages')) {
            document.body.insertAdjacentHTML('beforeend', 
                '<div id="statusMessages" class="fixed top-4 right-4 z-50 space-y-2"></div>'
            );
        }

        const notification = $(`
            <div class="notification ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300 max-w-sm">
                <p class="font-medium">${this.escapeHtml(message)}</p>
            </div>
        `);

        $('#statusMessages').append(notification);
        
        // Slide in
        setTimeout(() => {
            notification.removeClass('translate-x-full');
        }, 100);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.addClass('translate-x-full');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }

    // Helper method to escape HTML
    escapeHtml(text) {
        if (!text) return '';
        return $('<div>').text(text).html();
    }
}

// Initialize auth manager globally
window.authManager = new AuthManager();

// Global helper function for making authenticated requests
window.makeApiRequest = function(options) {
    return window.authManager.makeAuthenticatedRequest(options);
}; 