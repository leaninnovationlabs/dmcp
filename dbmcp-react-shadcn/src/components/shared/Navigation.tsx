import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Folder,
  Key,
  LogOut,
  ChevronDown,
  Shield,
  User
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

type NavigationItem = 'home' | 'data-sources' | 'tools' | 'auth' | 'token' | 'change-password';

interface NavigationProps {
  activeModule: NavigationItem;
  notificationCount?: number;
}

const Navigation = ({ activeModule }: NavigationProps) => {
  const { user, logout } = useAuth();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const navigate = useNavigate();

  const getHeaderColor = (module: NavigationItem) => {
    switch (module) {
      case 'home':
        return 'bg-blue-600';
      case 'data-sources':
        return 'bg-green-600';
      case 'tools':
        return 'bg-purple-600';
      default:
        return 'bg-blue-600';
    }
  };

  const getAvatarColor = (module: NavigationItem) => {
    switch (module) {
      case 'home':
        return 'bg-blue-100 text-blue-600';
      case 'data-sources':
        return 'bg-green-100 text-green-600';
      case 'tools':
        return 'bg-purple-100 text-purple-600';
      default:
        return 'bg-blue-100 text-blue-600';
    }
  };

  const activeItem = { label: activeModule.charAt(0).toUpperCase() + activeModule.slice(1) };

  const handleLogout = () => {
    logout();
    setIsUserMenuOpen(false);
    navigate('/login');
  };

  const handleGenerateToken = () => {
    navigate('/generate-token');
    setIsUserMenuOpen(false);
  };

  const handleChangePassword = () => {
    navigate('/change-password');
    setIsUserMenuOpen(false);
  };

  const handleProfile = () => {
    navigate('/profile');
    setIsUserMenuOpen(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <Button
          variant="ghost"
          onClick={() => navigate('/app')}
          className="flex items-center space-x-3 p-0 h-auto hover:bg-transparent cursor-pointer"
        >
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${getHeaderColor(activeModule)}`}>
            <Folder className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-semibold text-gray-900">{activeItem?.label}</span>
        </Button>
      </div>
      
      <div className="flex items-center space-x-4">
        <Separator orientation="vertical" className="h-6" />
        
        {/* User Menu */}
        <DropdownMenu open={isUserMenuOpen} onOpenChange={setIsUserMenuOpen}>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center space-x-2 h-auto p-2">
              <Avatar className="h-8 w-8">
                <AvatarFallback className={`text-sm font-medium ${getAvatarColor(activeModule)}`}>
                  {user?.username?.charAt(0).toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm font-medium text-gray-700">{user?.username || 'User'}</span>
              <ChevronDown className="w-4 h-4 text-gray-500" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleProfile}>
              <User className="mr-2 h-4 w-4" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleGenerateToken}>
              <Key className="mr-2 h-4 w-4" />
              Generate API Token
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleChangePassword}>
              <Shield className="mr-2 h-4 w-4" />
              Change Password
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default Navigation;