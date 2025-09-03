// Updated config.js
const APP_CONFIG = {
    // Use the same origin as the frontend
    CONTEXT_PATH: '/dmcp/ui',
    
    // Use localhost if frontend is on localhost, or use relative URLs
    API_BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000/dmcp' 
        : 'http://127.0.0.1:8000/dmcp',
    
    // Alternative: use relative URLs if frontend and backend are on same server
    // API_BASE_URL: '/api/dmcp',
    
    getPath: function(path) {
        if (!path.startsWith('/')) {
            path = '/' + path;
        }
        return this.CONTEXT_PATH + path;
    },
    
    urls: {
        home: function() { return APP_CONFIG.getPath('/index.html'); },
        datasource: function() { return APP_CONFIG.getPath('/datasource/'); },
        datasourceEdit: function(id = null) { 
            return APP_CONFIG.getPath('/datasource/edit.html' + (id ? '?id=' + id : ''));
        },
        tools: function() { return APP_CONFIG.getPath('/tools/'); },
        toolsEdit: function(id = null) { 
            return APP_CONFIG.getPath('/tools/edit.html' + (id ? '?id=' + id : ''));
        },
        users: function() { return APP_CONFIG.getPath('/users/'); }
    }
};

window.APP_CONFIG = APP_CONFIG;