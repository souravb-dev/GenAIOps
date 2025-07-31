import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      onClose();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const quickActions = [
    { name: 'View All Resources', path: '/cloud-resources', icon: 'fas fa-list' },
    { name: 'System Health', path: '/monitoring/health', icon: 'fas fa-heartbeat' },
    { name: 'Cost Overview', path: '/cost-analysis', icon: 'fas fa-chart-pie' },
    { name: 'Recent Alerts', path: '/monitoring/alerts', icon: 'fas fa-exclamation-triangle' },
  ];

  const supportLinks = [
    { name: 'Documentation', href: '#', icon: 'fas fa-book' },
    { name: 'API Reference', href: '#', icon: 'fas fa-code' },
    { name: 'Support', href: '#', icon: 'fas fa-life-ring' },
    { name: 'Feedback', href: '#', icon: 'fas fa-comment' },
  ];

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out md:hidden ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <i className="fas fa-cloud text-blue-500 text-xl mr-2"></i>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">
                GenAI CloudOps
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <i className="fas fa-times text-lg"></i>
            </button>
          </div>

          {/* User Info */}
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user?.full_name?.charAt(0)?.toUpperCase() || user?.username?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {user?.full_name || user?.username || 'User'}
                </p>
                                 <p className="text-xs text-gray-500 dark:text-gray-400">
                   {user?.email || 'No email'}
                 </p>
              </div>
            </div>
          </div>

          {/* Navigation Content */}
          <div className="flex-1 overflow-y-auto">
            
            {/* Quick Actions */}
            <div className="p-4">
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                Quick Actions
              </h3>
              <nav className="space-y-1">
                {quickActions.map((action) => (
                  <NavLink
                    key={action.name}
                    to={action.path}
                    onClick={onClose}
                    className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white"
                  >
                    <i className={`${action.icon} mr-3 text-sm text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300`}></i>
                    {action.name}
                  </NavLink>
                ))}
              </nav>
            </div>

            {/* Support Links */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                Support & Help
              </h3>
              <nav className="space-y-1">
                {supportLinks.map((link) => (
                  <a
                    key={link.name}
                    href={link.href}
                    className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white"
                  >
                    <i className={`${link.icon} mr-3 text-sm text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300`}></i>
                    {link.name}
                  </a>
                ))}
              </nav>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={handleLogout}
              className="w-full flex items-center px-2 py-2 text-sm font-medium rounded-md text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900 hover:text-red-900 dark:hover:text-red-300"
            >
              <i className="fas fa-sign-out-alt mr-3 text-sm"></i>
              Sign out
            </button>
          </div>
        </div>
      </div>
    </>
  );
} 