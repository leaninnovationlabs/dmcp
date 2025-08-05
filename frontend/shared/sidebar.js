// Sidebar Navigation Component
class Sidebar {
    constructor() {
        this.isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        this.isMobileOpen = false;
        this.init();
    }

    init() {
        this.createSidebar();
        this.bindEvents();
        this.setInitialState();
    }

    createSidebar() {
        const sidebarHTML = `
            <!-- Sidebar -->
            <div id="sidebar" class="fixed inset-y-0 left-0 z-50 w-64 bg-white text-black transform -translate-x-full lg:translate-x-0 transition-transform duration-300 ease-in-out flex flex-col border-r border-gray-200">
                <!-- Sidebar Header -->
                <div class="flex items-center justify-between h-16 px-4 border-b border-gray-200">
                    <div class="flex items-center min-w-0">
                        <div class="sidebar-logo">
                            <h1 class="text-xl font-bold text-black">DB-MCP</h1>
                            <p class="text-xs text-gray-600 sidebar-subtitle">Database Model Control Protocol</p>
                        </div>
                    </div>
                    <button id="sidebarToggle" class="lg:hidden text-gray-500 hover:text-black flex-shrink-0">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>

                <!-- Navigation Menu -->
                <nav class="flex-1 overflow-y-auto">
                    <div class="px-4 py-4 space-y-2">
                        <a href="${APP_CONFIG ? APP_CONFIG.urls.home() : '/index.html'}" 
                           class="sidebar-link flex items-center px-4 py-3 text-black rounded-lg hover:bg-gray-50 transition-colors" 
                           data-page="home">
                            <i class="fas fa-home w-5 h-5 mr-3 flex-shrink-0"></i>
                            <span class="sidebar-text">Home</span>
                        </a>
                        
                        <a href="${APP_CONFIG ? APP_CONFIG.urls.datasource() : '/datasource/'}" 
                           class="sidebar-link flex items-center px-4 py-3 text-black rounded-lg hover:bg-gray-50 transition-colors" 
                           data-page="datasource">
                            <i class="fas fa-database w-5 h-5 mr-3 flex-shrink-0"></i>
                            <span class="sidebar-text">Data Sources</span>
                        </a>
                        
                        <a href="${APP_CONFIG ? APP_CONFIG.urls.tools() : '/tools/'}" 
                           class="sidebar-link flex items-center px-4 py-3 text-black rounded-lg hover:bg-gray-50 transition-colors" 
                           data-page="tools">
                            <i class="fas fa-tools w-5 h-5 mr-3 flex-shrink-0"></i>
                            <span class="sidebar-text">Tools</span>
                        </a>
                    </div>
                    
                    <!-- Authentication Section -->
                    <div class="px-4 py-2 mt-4 border-t border-gray-200">
                        <button id="logoutBtn" class="w-full flex items-center px-4 py-3 text-black rounded-lg hover:bg-red-50 hover:text-red-600 transition-colors">
                            <i class="fas fa-sign-out-alt w-5 h-5 mr-3 flex-shrink-0"></i>
                            <span class="sidebar-text">Logout</span>
                        </button>
                    </div>
                </nav>
                
                <!-- Collapse Toggle (Desktop) -->
                <div class="border-t border-gray-200 p-4 hidden lg:block">
                    <button id="collapseToggle" class="w-full flex items-center justify-center px-4 py-3 text-gray-500 hover:text-black hover:bg-gray-50 rounded-lg transition-colors">
                        <i class="fas fa-chevron-left collapse-icon transition-transform duration-300 flex-shrink-0"></i>
                        <span class="sidebar-text ml-2">Collapse</span>
                    </button>
                </div>
            </div>

            <!-- Mobile Overlay -->
            <div id="sidebarOverlay" class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden hidden"></div>

            <!-- Mobile Menu Button -->
            <button id="mobileMenuBtn" class="fixed top-4 left-4 z-60 lg:hidden bg-white text-black p-3 rounded-lg shadow-lg hover:bg-gray-50 transition-colors border border-gray-200">
                <i class="fas fa-bars text-lg"></i>
            </button>
        `;

        // Insert sidebar at the beginning of body
        document.body.insertAdjacentHTML('afterbegin', sidebarHTML);
    }

    bindEvents() {
        // Mobile menu toggle
        document.getElementById('mobileMenuBtn').addEventListener('click', () => {
            this.toggleMobile();
        });

        // Sidebar close button (mobile)
        document.getElementById('sidebarToggle').addEventListener('click', () => {
            this.toggleMobile();
        });

        // Overlay click (mobile)
        document.getElementById('sidebarOverlay').addEventListener('click', () => {
            this.toggleMobile();
        });

        // Collapse toggle (desktop)
        document.getElementById('collapseToggle').addEventListener('click', () => {
            this.toggleCollapse();
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth >= 1024) {
                this.closeMobile();
            }
        });

        // Logout button
        document.getElementById('logoutBtn').addEventListener('click', () => {
            if (window.authManager) {
                window.authManager.logout();
            }
        });
    }

    toggleMobile() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        
        this.isMobileOpen = !this.isMobileOpen;
        
        if (this.isMobileOpen) {
            sidebar.classList.remove('-translate-x-full');
            overlay.classList.remove('hidden');
        } else {
            sidebar.classList.add('-translate-x-full');
            overlay.classList.add('hidden');
        }
    }

    closeMobile() {
        if (this.isMobileOpen) {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebarOverlay');
            
            sidebar.classList.add('-translate-x-full');
            overlay.classList.add('hidden');
            this.isMobileOpen = false;
        }
    }

    toggleCollapse() {
        this.isCollapsed = !this.isCollapsed;
        localStorage.setItem('sidebarCollapsed', this.isCollapsed.toString());
        this.updateSidebarState();
    }

    setInitialState() {
        // Apply initial state after a small delay to ensure DOM is ready
        setTimeout(() => {
            if (this.isCollapsed) {
                this.updateSidebarState();
            }
            
            // Ensure proper body spacing for sidebar
            document.body.classList.add('lg:pl-64');
            
            // Update main content if it exists
            const mainContent = document.getElementById('mainContent');
            if (mainContent) {
                mainContent.classList.remove('lg:ml-64');
                mainContent.classList.add('transition-all', 'duration-300');
            }
        }, 50);
    }

    updateSidebarState() {
        const sidebar = document.getElementById('sidebar');
        const collapseIcon = document.querySelector('.collapse-icon');
        
        if (this.isCollapsed) {
            sidebar.classList.add('lg:w-16');
            sidebar.classList.remove('lg:w-64');
            
            // Hide text elements
            document.querySelectorAll('.sidebar-text').forEach(el => {
                el.classList.add('lg:hidden');
            });
            
            const subtitle = document.querySelector('.sidebar-subtitle');
            if (subtitle) {
                subtitle.classList.add('lg:hidden');
            }
            
            // Rotate collapse icon
            if (collapseIcon) {
                collapseIcon.classList.add('rotate-180');
            }
            
            // Adjust body spacing
            document.body.classList.remove('lg:pl-64');
            document.body.classList.add('lg:pl-16');
            
        } else {
            sidebar.classList.remove('lg:w-16');
            sidebar.classList.add('lg:w-64');
            
            // Show text elements
            document.querySelectorAll('.sidebar-text').forEach(el => {
                el.classList.remove('lg:hidden');
            });
            
            const subtitle = document.querySelector('.sidebar-subtitle');
            if (subtitle) {
                subtitle.classList.remove('lg:hidden');
            }
            
            // Reset collapse icon
            if (collapseIcon) {
                collapseIcon.classList.remove('rotate-180');
            }
            
            // Adjust body spacing
            document.body.classList.remove('lg:pl-16');
            document.body.classList.add('lg:pl-64');
        }
    }

    setActivePage(page) {
        // Remove active class from all links
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.classList.remove('bg-blue-600', 'text-white');
            link.classList.add('text-black');
            link.classList.remove('bg-gray-100');
        });

        // Add active class to current page
        const activeLink = document.querySelector(`[data-page="${page}"]`);
        if (activeLink) {
            activeLink.classList.remove('text-black');
            activeLink.classList.add('bg-blue-600', 'text-white');
        }
    }
}

// Initialize sidebar when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.sidebar = new Sidebar();
});

// Global function to set active page
window.setSidebarActivePage = function(page) {
    if (window.sidebar) {
        window.sidebar.setActivePage(page);
    }
}; 