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
  Key,
  LogOut,
  ChevronDown,
  Shield,
  User
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

type NavigationItem = 'home' | 'data-sources' | 'tools' | 'auth' | 'token' | 'change-password' | 'profile';

interface NavigationProps {
  activeModule: NavigationItem;
  notificationCount?: number;
}

const Navigation = ({ activeModule: _activeModule }: NavigationProps) => {
  const { user, logout } = useAuth();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const navigate = useNavigate();

  const getAvatarColor = () => {
    return 'bg-[#FEBF23]/20 text-[#FEBF23]';
  };

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
          className="flex items-center p-0 h-auto hover:bg-transparent cursor-pointer"
        >
          <div className="w-20 h-16 flex items-center justify-center">
            <img 
              src="/logo.webp" 
              alt="DBMCP Logo" 
              className="w-18 h-14 object-contain rounded-lg"
              onLoad={() => console.log('Logo loaded successfully')}
              onError={(e) => {
                console.error('Logo failed to load:', e);
                console.log('Trying fallback to PNG...');
                e.currentTarget.src = '/logo.png';
              }}
            />
          </div>
          <span className="text-lg font-semibold text-gray-900">DBMCP</span>
        </Button>
      </div>
      
      <div className="flex items-center space-x-4">
        <Separator orientation="vertical" className="h-6" />
        
        {/* User Menu */}
        <DropdownMenu open={isUserMenuOpen} onOpenChange={setIsUserMenuOpen}>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center space-x-2 h-auto p-2">
              <Avatar className="h-8 w-8">
                <AvatarFallback className={`text-sm font-medium ${getAvatarColor()}`}>
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