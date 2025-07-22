// Application Configuration
const APP_CONFIG = {
    // Base context path for the application
    CONTEXT_PATH: '/dbmcp/ui',
    
    // API configuration
    API_BASE_URL: 'http://localhost:8000/dbmcp',
    
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