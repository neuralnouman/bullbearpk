import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

import { 
  Menu, 
  X, 
  TrendingUp, 
  User, 
  LogOut,
  Sun,
  Moon,
  Home,
  Brain,
  FileText
} from 'lucide-react';
import toast from 'react-hot-toast';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { user, logout } = useAuthStore();

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const navigationItems = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: Home,
      description: 'Overview and insights'
    },
    {
      path: '/investment-form',
      label: 'AI Analysis',
      icon: Brain,
      description: 'Get investment recommendations'
    },
    {
      path: '/portfolio',
      label: 'Portfolio',
      icon: TrendingUp,
      description: 'Track your investments'
    },
    {
      path: '/market-data',
      label: 'Market Data',
      icon: TrendingUp,
      description: 'Live market information'
    },
    {
      path: '/news',
      label: 'News',
      icon: FileText,
      description: 'Market news and updates'
    }
  ];

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden`}>
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold gradient-text">BullBearPK</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`w-full flex items-center p-3 rounded-lg transition-colors ${
                    isActive(item.path)
                      ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon size={20} className="mr-3" />
                  <div className="flex-1">
                    <div className="font-medium">{item.label}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{item.description}</div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* User Menu */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="space-y-2">

            <button 
              onClick={handleLogout}
              className="w-full flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg text-red-600"
            >
              <LogOut size={20} className="mr-3" />
              <span className="text-sm">Logout</span>
            </button>
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <User size={16} className="text-white" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium">{user?.name}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => setSidebarOpen(true)}
                className={`${sidebarOpen ? 'lg:hidden' : ''} p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg mr-3`}
              >
                <Menu size={20} />
              </button>
              <h1 className="text-xl font-semibold">
                {isActive('/dashboard') && 'Dashboard'}
                {isActive('/investment-form') && 'AI Investment Analysis'}
                {isActive('/portfolio') && 'Portfolio'}
                {isActive('/market-data') && 'Market Data'}
                {isActive('/news') && 'Market News'}

              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                PSX: <span className="text-green-600">+1.2%</span>
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                KMI 30: <span className="text-blue-600">45,234</span>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900">
          {children}
        </div>
      </div>
    </div>
  );
};

export default MainLayout;