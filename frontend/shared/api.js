// Centralized API Request Handler
// Ensures all API calls use proper authentication and HTTPS

// Global API request function with authentication
function makeApiRequest(options) {
    // Ensure we have the auth manager
    if (typeof window.authManager === 'undefined') {
        window.authManager = new AuthManager();
    }
    
    // Force HTTPS for production domains
    if (options.url && options.url.startsWith('http://') && 
        (window.location.hostname.includes('opsloom.io') || 
         window.location.hostname.includes('yourdomain.com') ||
         (!window.location.hostname.includes('localhost') && 
          !window.location.hostname.includes('127.0.0.1')))) {
        options.url = options.url.replace('http://', 'https://');
        console.warn('🔒 Forced HTTPS for production domain:', options.url);
    }
    

    
    // Use authenticated request if token exists
    const token = window.authManager.getToken();
    if (token) {
        return window.authManager.makeAuthenticatedRequest(options);
    }
    
    // For non-authenticated requests (like login), use regular jQuery AJAX
    return $.ajax(options);
}

// Global variable to make it available everywhere
window.makeApiRequest = makeApiRequest;

// Debug function to check current API configuration
window.debugApiConfig = function() {

    
    // Test the health endpoint
    fetch(`${APP_CONFIG.API_BASE_URL}/health`)
        .then(response => {
            return response.json();
        })
        .then(data => data)
        .catch(error => {});
};

// Auto-fix mixed content issues on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on HTTPS but API base URL is HTTP
    if (window.location.protocol === 'https:' && APP_CONFIG.API_BASE_URL.startsWith('http://')) {
        console.error('🚨 MIXED CONTENT DETECTED!');
        console.error('Page is HTTPS but API URL is HTTP:', APP_CONFIG.API_BASE_URL);
        console.error('This will cause browser security errors!');
        
        // Try to auto-fix by updating the config
        const httpsUrl = APP_CONFIG.API_BASE_URL.replace('http://', 'https://');
        console.warn('🔧 Auto-fixing API URL to:', httpsUrl);
        
        // Update the config
        APP_CONFIG.API_BASE_URL = httpsUrl;
    }
    
    
});