import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faDatabase, 
  faLink, 
  faTools, 
  faShieldAlt, 
  faBolt,
  faServer
} from '@fortawesome/free-solid-svg-icons';

const Dashboard = () => {
  // Placeholder functions for navigation and actions
  const handleTryNow = () => {
    // TODO: Implement navigation to datasource page
    console.log('Navigate to datasource page');
  };

  const handleDatasourceClick = () => {
    // TODO: Implement navigation to datasource page
    console.log('Navigate to datasource page');
  };

  const handleToolsClick = () => {
    // TODO: Implement navigation to tools page
    console.log('Navigate to tools page');
  };

  const handleLogout = () => {
    // TODO: Implement logout functionality
    console.log('Logout user');
  };

  return (
    <div className="bg-white min-h-screen">
      {/* Hero Section */}
      <div className="relative bg-white overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="relative z-10 pb-8 bg-white sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="sm:text-center lg:text-left">
                              <h1 className="text-4xl tracking-tight font-bold text-black sm:text-5xl md:text-6xl">
                  <span className="block xl:inline">Data</span>
                  <span className="block xl:inline xl:ml-2">MCP</span>
                </h1>
                <p className="mt-6 text-lg text-gray-600 sm:mt-8 sm:text-xl sm:max-w-xl sm:mx-auto md:mt-8 md:text-xl lg:mx-0">
                  Securely connect to your data sources, create powerful tools, and execute queries across multiple database types with our intuitive interface.
                </p>
                <div className="mt-8 sm:mt-10 sm:flex sm:justify-center lg:justify-start gap-4">
                  <button 
                    onClick={handleTryNow}
                    className="bg-black text-white rounded-lg px-6 py-3 font-medium transition-all duration-200 hover:bg-gray-800 hover:-translate-y-0.5 inline-flex items-center gap-2"
                  >
                    Try now
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                  </button>
                </div>
              </div>
            </main>
          </div>
        </div>
        <div className="lg:absolute lg:inset-y-10 lg:right-0 lg:w-1/3">
          <div className="h-56 w-full bg-gradient-to-br from-indigo-500 to-purple-600 sm:h-72 md:h-96 lg:w-full lg:h-full flex items-center justify-center">
            <div className="text-white text-center">
              <div className="text-6xl mb-4">
                <FontAwesomeIcon icon={faDatabase} />
              </div>
              <h3 className="text-2xl font-semibold mb-2">Multiple Database Support</h3>
              <p className="text-lg opacity-90">PostgreSQL • MySQL • SQLite</p>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:text-center">
            <h2 className="text-base text-gray-600 font-medium tracking-wide uppercase">Features</h2>
            <p className="mt-2 text-3xl leading-8 font-bold tracking-tight text-black sm:text-4xl">
              Everything you need to manage databases
            </p>
            <p className="mt-4 max-w-2xl text-lg text-gray-600 lg:mx-auto">
              DMCP provides a comprehensive suite of tools for database management and query execution.
            </p>
          </div>

          <div className="mt-12">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Database Connections Card */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white mr-4">
                      <FontAwesomeIcon icon={faLink} className="text-lg" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-black">Database Connections</h3>
                      <p className="text-gray-600 mt-1">Connect to multiple database types</p>
                    </div>
                  </div>
                  <button 
                    onClick={handleDatasourceClick}
                    className="text-black underline font-medium hover:text-gray-700"
                  >
                    Try now
                  </button>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
                      <FontAwesomeIcon icon={faDatabase} className="text-white text-sm" />
                    </div>
                    <div className="w-8 h-8 bg-green-600 rounded flex items-center justify-center">
                      <FontAwesomeIcon icon={faServer} className="text-white text-sm" />
                    </div>
                    <div className="w-8 h-8 bg-purple-600 rounded flex items-center justify-center">
                      <FontAwesomeIcon icon={faDatabase} className="text-white text-sm" />
                    </div>
                  </div>
                </div>
                <p className="text-gray-600">
                  Connect to PostgreSQL, MySQL, and SQLite databases with secure encrypted password storage.
                </p>
              </div>

              {/* Query Tools Card */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white mr-4">
                      <FontAwesomeIcon icon={faTools} className="text-lg" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-black">Query Tools</h3>
                      <p className="text-gray-600 mt-1">Create powerful database tools</p>
                    </div>
                  </div>
                  <button 
                    onClick={handleToolsClick}
                    className="text-black underline font-medium hover:text-gray-700"
                  >
                    Learn more
                  </button>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                      <span className="text-sm text-gray-700">Parameterized queries</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-600 rounded-full"></div>
                      <span className="text-sm text-gray-700">Template support</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-purple-600 rounded-full"></div>
                      <span className="text-sm text-gray-700">Reusable components</span>
                    </div>
                  </div>
                </div>
                <p className="text-gray-600">
                  Create reusable query tools with parameters and templates for efficient database operations.
                </p>
              </div>

              {/* Security Card */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white mr-4">
                      <FontAwesomeIcon icon={faShieldAlt} className="text-lg" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-black">Secure & Encrypted</h3>
                      <p className="text-gray-600 mt-1">Enterprise-grade security</p>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Encryption</span>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    </div>
                  </div>
                </div>
                <p className="text-gray-600">
                  All sensitive data including passwords are encrypted at rest using industry-standard encryption.
                </p>
              </div>

              {/* Performance Card */}
              <div className="bg-white border border-gray-200 rounded-xl p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white mr-4">
                      <FontAwesomeIcon icon={faBolt} className="text-lg" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-black">Fast & Responsive</h3>
                      <p className="text-gray-600 mt-1">Modern async architecture</p>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div className="w-12 h-2 bg-green-500 rounded-full"></div>
                    </div>
                    <span className="text-sm text-gray-700">Performance</span>
                  </div>
                </div>
                <p className="text-gray-600">
                  Modern async architecture ensures fast query execution and responsive user interface.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-gray-50">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:py-20 lg:px-8 text-center">
          <h2 className="text-3xl font-bold tracking-tight text-black sm:text-4xl mb-4">
            <span className="block">Ready to get started?</span>
            <span className="block text-gray-600">Use the buttons above to begin managing your databases today.</span>
          </h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Start by adding a data source to connect to your database, then create powerful tools to execute queries and manage your data efficiently.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;