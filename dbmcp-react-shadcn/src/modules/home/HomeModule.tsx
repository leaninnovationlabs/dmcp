'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import {
  Home,
  Database,
  Wrench,
  Shield,
  Zap,
  Link,
  Server,
  ChevronRight,
  LogOut,
  ChevronLeft
} from 'lucide-react';

type NavigationItem = 'home' | 'data-sources' | 'tools';

interface FileItem {
  id: string;
  name: string;
  type: 'folder' | 'file';
  size?: string;
  modified?: string;
}

interface HomeModuleProps {
  onModuleChange: (module: NavigationItem) => void;
  sidebarCollapsed?: boolean;
  onToggleSidebar?: () => void;
}

const HomeModule = ({ onModuleChange, sidebarCollapsed = false, onToggleSidebar }: HomeModuleProps) => {
  const [activeFileCategory, setActiveFileCategory] = useState<string>('Home Files');

  const navigationItems = [
    { id: 'home', label: 'Home', icon: Home, color: 'blue' },
    { id: 'data-sources', label: 'Data Sources', icon: Database, color: 'green' },
    { id: 'tools', label: 'Tools', icon: Wrench, color: 'purple' },
  ];

  const getActiveColor = (itemColor: string) => {
    switch (itemColor) {
      case 'blue':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'green':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'purple':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      default:
        return 'bg-blue-50 text-blue-700 border-blue-200';
    }
  };

  const getIconColor = (itemColor: string, isActive: boolean) => {
    if (isActive) {
      switch (itemColor) {
        case 'blue':
          return 'text-blue-600';
        case 'green':
          return 'text-green-600';
        case 'purple':
          return 'text-purple-600';
        default:
          return 'text-blue-600';
      }
    }
    return 'text-gray-500';
  };

  const handleTryNow = () => {
    onModuleChange('data-sources');
  };

  const handleDatasourceClick = () => {
    onModuleChange('data-sources');
  };

  const handleToolsClick = () => {
    onModuleChange('tools');
  };

  return (
    <>
      {/* Left Sidebar Navigation */}
      <aside className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-white border-r border-gray-200 flex flex-col transition-all duration-300`}>
        {/* Header */}
        <div className={`${sidebarCollapsed ? 'p-2' : 'p-6'} border-b border-gray-200`}>
          {sidebarCollapsed ? (
            <div className="flex justify-center">
              <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
                <Home className="w-5 h-5 text-white" />
              </div>
            </div>
          ) : (
            <>
              <h1 className="text-xl font-bold text-black">Opsloom Data MCP</h1>
              <p className="text-sm text-gray-600 mt-1">Connect AI assistants to your data</p>
            </>
          )}
        </div>

        {/* Main Navigation */}
        <div className={`${sidebarCollapsed ? 'p-2' : 'p-4'}`}>
          <nav className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = item.id === 'home';
              return (
                <Button
                  key={item.id}
                  variant="ghost"
                  onClick={() => onModuleChange(item.id as NavigationItem)}
                  className={`w-full justify-start h-auto ${sidebarCollapsed ? 'p-2' : 'p-3'} ${
                    isActive
                      ? `${getActiveColor(item.color)} border`
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className={`${sidebarCollapsed ? 'w-5 h-5' : 'w-5 h-5 mr-3'} ${getIconColor(item.color, isActive)}`} />
                  {!sidebarCollapsed && <span className="font-medium">{item.label}</span>}
                </Button>
              );
            })}
          </nav>
        </div>

        <div className="flex-1"></div>

        {/* Footer */}
        {!sidebarCollapsed && (
          <div className="p-4 border-t border-gray-200">
            <Button variant="ghost" className="w-full justify-start h-auto p-3 text-gray-700 hover:bg-gray-50">
              <LogOut className="w-5 h-5 mr-3 text-gray-500" />
              <span className="font-medium">Logout</span>
            </Button>
          </div>
        )}

        {/* Collapse Button */}
        <div className="p-2 border-t border-gray-200">
          <Button
            variant="ghost"
            onClick={onToggleSidebar}
            className="w-full justify-center h-auto p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50"
          >
            <ChevronLeft className={`w-4 h-4 transition-transform duration-300 ${sidebarCollapsed ? 'rotate-180' : ''}`} />
            {!sidebarCollapsed && <span className="ml-2 text-sm">Collapse</span>}
          </Button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto bg-white">
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
                    <Button 
                      onClick={handleTryNow}
                      className="bg-[#FEBF23] hover:bg-[#FEBF23]/90 text-black border border-[#FEBF23] transition-all duration-200 hover:-translate-y-0.5 inline-flex items-center gap-2"
                    >
                      Try now
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </main>
            </div>
          </div>
          <div className="lg:absolute lg:inset-y-10 lg:right-0 lg:w-1/3">
            <div className="h-56 w-full bg-gradient-to-br from-indigo-500 to-purple-600 sm:h-72 md:h-96 lg:w-full lg:h-full flex items-center justify-center">
              <div className="text-white text-center">
                <div className="text-6xl mb-4">
                  <Database className="w-16 h-16 mx-auto" />
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
              <Badge variant="secondary" className="text-base font-medium tracking-wide uppercase mb-2">
                Features
              </Badge>
              <h2 className="mt-2 text-3xl leading-8 font-bold tracking-tight text-black sm:text-4xl">
                Everything you need to manage databases
              </h2>
              <p className="mt-4 max-w-2xl text-lg text-gray-600 lg:mx-auto">
                DMCP provides a comprehensive suite of tools for database management and query execution.
              </p>
            </div>

            <div className="mt-12">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Database Connections Card */}
                <Card className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center">
                        <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white mr-4">
                          <Link className="w-6 h-6" />
                        </div>
                        <div>
                          <CardTitle>Database Connections</CardTitle>
                          <CardDescription>Connect to multiple database types</CardDescription>
                        </div>
                      </div>
                      <Button 
                        variant="link"
                        onClick={handleDatasourceClick}
                        className="text-[#FEBF23] underline font-medium hover:text-[#FEBF23]/80 p-0 h-auto"
                      >
                        Try now
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
                          <Database className="text-white text-sm" />
                        </div>
                        <div className="w-8 h-8 bg-green-600 rounded flex items-center justify-center">
                          <Server className="text-white text-sm" />
                        </div>
                        <div className="w-8 h-8 bg-purple-600 rounded flex items-center justify-center">
                          <Database className="text-white text-sm" />
                        </div>
                      </div>
                    </div>
                    <p className="text-gray-600">
                      Connect to PostgreSQL, MySQL, and SQLite databases with secure encrypted password storage.
                    </p>
                  </CardContent>
                </Card>

                {/* Query Tools Card */}
                <Card className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center">
                        <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white mr-4">
                          <Wrench className="w-6 h-6" />
                        </div>
                        <div>
                          <CardTitle>Query Tools</CardTitle>
                          <CardDescription>Create powerful database tools</CardDescription>
                        </div>
                      </div>
                      <Button 
                        variant="link"
                        onClick={handleToolsClick}
                        className="text-black underline font-medium hover:text-gray-700 p-0 h-auto"
                      >
                        Learn more
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent>
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
                  </CardContent>
                </Card>

                {/* Security Card */}
                <Card className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                  <CardHeader>
                    <div className="flex items-center">
                      <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white mr-4">
                        <Shield className="w-6 h-6" />
                      </div>
                      <div>
                        <CardTitle>Secure & Encrypted</CardTitle>
                        <CardDescription>Enterprise-grade security</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
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
                  </CardContent>
                </Card>

                {/* Performance Card */}
                <Card className="transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                  <CardHeader>
                    <div className="flex items-center">
                      <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 text-white mr-4">
                        <Zap className="w-6 h-6" />
                      </div>
                      <div>
                        <CardTitle>Fast & Responsive</CardTitle>
                        <CardDescription>Modern async architecture</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
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
                  </CardContent>
                </Card>
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
      </main>
    </>
  );
};

export default HomeModule;
