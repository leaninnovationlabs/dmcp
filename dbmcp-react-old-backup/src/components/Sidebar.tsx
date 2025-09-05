import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHome, 
  faDatabase, 
  faTools, 
  faSignOutAlt, 
  faChevronLeft, 
  faBars, 
  faTimes 
} from '@fortawesome/free-solid-svg-icons';

interface SidebarProps {
  activePage?: string;
  onNavigate?: (page: string) => void;
  onLogout?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  activePage = 'home', 
  onNavigate, 
  onLogout 
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Load collapsed state from localStorage on mount
  useEffect(() => {
    const savedCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    setIsCollapsed(savedCollapsed);
  }, []);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setIsMobileOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleMobile = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  const toggleCollapse = () => {
    const newCollapsed = !isCollapsed;
    setIsCollapsed(newCollapsed);
    localStorage.setItem('sidebarCollapsed', newCollapsed.toString());
  };

  const handleNavigation = (page: string) => {
    if (onNavigate) {
      onNavigate(page);
    }
    // Close mobile menu after navigation
    setIsMobileOpen(false);
  };

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
  };

  const sidebarClasses = `
    fixed inset-y-0 left-0 z-50 bg-white text-black transform transition-transform duration-300 ease-in-out flex flex-col border-r border-gray-200
    ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
    ${isCollapsed ? 'lg:w-16' : 'w-64 lg:w-64'}
  `;

  const overlayClasses = `
    fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden
    ${isMobileOpen ? 'block' : 'hidden'}
  `;

  const mobileMenuClasses = `
    fixed top-4 left-4 z-60 lg:hidden bg-white text-black p-3 rounded-lg shadow-lg hover:bg-gray-50 transition-colors border border-gray-200
  `;

  return (
    <>
      {/* Sidebar */}
      <div className={sidebarClasses}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <div className="flex items-center min-w-0">
            <div className="sidebar-logo">
              <h1 className="text-xl font-bold text-black">Opsloom Data MCP</h1>
              <p className={`text-xs text-gray-600 sidebar-subtitle ${isCollapsed ? 'lg:hidden' : ''}`}>
                Connect AI assistants to your data
              </p>
            </div>
          </div>
          <button 
            onClick={toggleMobile}
            className="lg:hidden text-gray-500 hover:text-black flex-shrink-0"
          >
            <FontAwesomeIcon icon={faTimes} className="text-xl" />
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 overflow-y-auto">
          <div className="px-4 py-4 space-y-2">
            <button
              onClick={() => handleNavigation('home')}
              className={`w-full flex items-center px-4 py-3 rounded-lg transition-colors ${
                activePage === 'home' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-black hover:bg-gray-50'
              }`}
            >
              <FontAwesomeIcon icon={faHome} className="w-5 h-5 mr-3 flex-shrink-0" />
              <span className={`sidebar-text ${isCollapsed ? 'lg:hidden' : ''}`}>Home</span>
            </button>
            
            <button
              onClick={() => handleNavigation('datasource')}
              className={`w-full flex items-center px-4 py-3 rounded-lg transition-colors ${
                activePage === 'datasource' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-black hover:bg-gray-50'
              }`}
            >
              <FontAwesomeIcon icon={faDatabase} className="w-5 h-5 mr-3 flex-shrink-0" />
              <span className={`sidebar-text ${isCollapsed ? 'lg:hidden' : ''}`}>Data Sources</span>
            </button>
            
            <button
              onClick={() => handleNavigation('tools')}
              className={`w-full flex items-center px-4 py-3 rounded-lg transition-colors ${
                activePage === 'tools' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-black hover:bg-gray-50'
              }`}
            >
              <FontAwesomeIcon icon={faTools} className="w-5 h-5 mr-3 flex-shrink-0" />
              <span className={`sidebar-text ${isCollapsed ? 'lg:hidden' : ''}`}>Tools</span>
            </button>
          </div>
          
          {/* Authentication Section */}
          <div className="px-4 py-2 mt-4 border-t border-gray-200">
            <button 
              onClick={handleLogout}
              className="w-full flex items-center px-4 py-3 text-black rounded-lg hover:bg-red-50 hover:text-red-600 transition-colors"
            >
              <FontAwesomeIcon icon={faSignOutAlt} className="w-5 h-5 mr-3 flex-shrink-0" />
              <span className={`sidebar-text ${isCollapsed ? 'lg:hidden' : ''}`}>Logout</span>
            </button>
          </div>
        </nav>
        
        {/* Collapse Toggle (Desktop) */}
        <div className="border-t border-gray-200 p-4 hidden lg:block">
          <button 
            onClick={toggleCollapse}
            className="w-full flex items-center justify-center px-4 py-3 text-gray-500 hover:text-black hover:bg-gray-50 rounded-lg transition-colors"
          >
            <FontAwesomeIcon 
              icon={faChevronLeft} 
              className={`collapse-icon transition-transform duration-300 flex-shrink-0 ${isCollapsed ? 'rotate-180' : ''}`} 
            />
            <span className={`sidebar-text ml-2 ${isCollapsed ? 'lg:hidden' : ''}`}>Collapse</span>
          </button>
        </div>
      </div>

      {/* Mobile Overlay */}
      <div 
        className={overlayClasses}
        onClick={toggleMobile}
      />

      {/* Mobile Menu Button */}
      <button 
        onClick={toggleMobile}
        className={mobileMenuClasses}
      >
        <FontAwesomeIcon icon={faBars} className="text-lg" />
      </button>
    </>
  );
};

export default Sidebar;