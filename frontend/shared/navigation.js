// Shared Navigation Component
function createNavigation(currentPage = '') {
    return `
    <nav class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <h1 class="text-2xl font-bold text-gray-900">DB-MCP</h1>
                        <p class="text-xs text-gray-500">Data Model Control Protocol</p>
                    </div>
                </div>
                <div class="flex items-center space-x-8">
                    <a href="${APP_CONFIG ? APP_CONFIG.urls.home() : '../index.html'}" class="${currentPage === 'home' ? 'text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:border-b-2 hover:border-gray-300 transition-all'}">
                        Home
                    </a>
                    <a href="${APP_CONFIG ? APP_CONFIG.urls.datasource() : '../datasource/'}" class="${currentPage === 'datasource' ? 'text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:border-b-2 hover:border-gray-300 transition-all'}">
                        Data Sources
                    </a>
                    <a href="${APP_CONFIG ? APP_CONFIG.urls.tools() : '../tools/'}" class="${currentPage === 'tools' ? 'text-gray-900 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:border-b-2 hover:border-gray-300 transition-all'}">
                        Tools
                    </a>
                </div>
                <div class="flex items-center" id="navActions">
                    <!-- Actions will be injected here based on page -->
                </div>
            </div>
        </div>
    </nav>`;
}

// Common page header for module pages
function createPageHeader(title, backUrl, backText) {
    return `
    <div class="bg-gray-50 border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div class="flex items-center space-x-4">
                <button onclick="window.location.href='${backUrl}'" class="text-gray-500 hover:text-gray-700 transition-colors flex items-center">
                    <i class="fas fa-chevron-left mr-2"></i>
                    ${backText}
                </button>
                <h2 class="text-2xl font-bold text-gray-900">${title}</h2>
            </div>
        </div>
    </div>`;
}

// Initialize navigation for a specific page
function initNavigation(currentPage, actionButtons = '') {
    document.addEventListener('DOMContentLoaded', function() {
        // Insert navigation
        const navContainer = document.getElementById('navigation');
        if (navContainer) {
            navContainer.innerHTML = createNavigation(currentPage);
            
            // Add action buttons if provided
            const actionsContainer = document.getElementById('navActions');
            if (actionsContainer && actionButtons) {
                actionsContainer.innerHTML = actionButtons;
            }
        }
    });
} 