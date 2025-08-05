// Application Configuration
const APP_CONFIG = {
    // Base context path for the application
    CONTEXT_PATH: '/dbmcp/ui',
    
    // API configuration - SIMPLE RELATIVE PATH (browser uses same protocol automatically)
    API_BASE_URL: '/dbmcp',
    
    // Debug information
    getDebugInfo: function() {
        return {
            currentUrl: window.location.href,
            apiBaseUrl: this.API_BASE_URL,
            contextPath: this.CONTEXT_PATH,
            detectedPort: window.location.port,
            detectedProtocol: window.location.protocol,
            detectedHostname: window.location.hostname
        };
    },
    
    // Helper functions for path generation
    getPath: function(path) {
        // Ensure path starts with /
        if (!path.startsWith('/')) {
            path = '/' + path;
        }
        return this.CONTEXT_PATH + path;
    },
    
    // Generate full URLs for navigation
    urls: {
        home: function() { return APP_CONFIG.getPath('/index.html'); },
        datasource: function() { return APP_CONFIG.getPath('/datasource/'); },
        datasourceEdit: function(id = null) { 
            return APP_CONFIG.getPath('/datasource/edit.html' + (id ? '?id=' + id : ''));
        },
        tools: function() { return APP_CONFIG.getPath('/tools/'); },
        toolsEdit: function(id = null) { 
            return APP_CONFIG.getPath('/tools/edit.html' + (id ? '?id=' + id : ''));
        }
    }
};

// Make it globally available
window.APP_CONFIG = APP_CONFIG;

// Debug helper - accessible via browser console
window.dbmcpDebug = function() {

};

// Test API connection - accessible via browser console
window.dbmcpTestConnection = function() {

    
    fetch(`${APP_CONFIG.API_BASE_URL}/health`)
        .then(response => {
            return response.json();
        })
        .then(data => {
        })
        .catch(error => {

        });
}; 