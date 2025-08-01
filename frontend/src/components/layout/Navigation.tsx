import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface NavigationItem {
  id: string;
  name: string;
  path: string;
  icon: string;
  requiredPermissions?: string[];
  description: string;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    path: '/dashboard',
    icon: 'fas fa-tachometer-alt',
    description: 'Overview and key metrics'
  },
  {
    id: 'cloud-resources',
    name: 'Cloud Resources',
    path: '/cloud-resources',
    icon: 'fas fa-cloud',
    requiredPermissions: ['can_view_resources'],
    description: 'OCI resources and services'
  },
  {
    id: 'monitoring',
    name: 'Monitoring',
    path: '/monitoring',
    icon: 'fas fa-chart-line',
    requiredPermissions: ['can_view_monitoring'],
    description: 'Real-time metrics and alerts'
  },
  {
    id: 'alerts',
    name: 'Alerts & Insights',
    path: '/alerts',
    icon: 'fas fa-exclamation-triangle',
    requiredPermissions: ['can_view_alerts'],
    description: 'Alert management with AI insights'
  },
  {
    id: 'kubernetes',
    name: 'Kubernetes',
    path: '/kubernetes',
    icon: 'fas fa-dharmachakra',
    requiredPermissions: ['can_view_kubernetes'],
    description: 'K8s clusters and workloads'
  },
  {
    id: 'cost-analysis',
    name: 'Cost Analysis',
    path: '/cost-analysis',
    icon: 'fas fa-dollar-sign',
    requiredPermissions: ['can_view_costs'],
    description: 'Resource costs and optimization'
  },
  {
    id: 'automation',
    name: 'Automation',
    path: '/automation',
    icon: 'fas fa-cogs',
    requiredPermissions: ['can_manage_automation'],
    description: 'Automated workflows and remediation'
  },
  {
    id: 'settings',
    name: 'Settings',
    path: '/settings',
    icon: 'fas fa-cog',
    requiredPermissions: ['can_view_settings'],
    description: 'Application configuration'
  }
];

export function Navigation() {
  const { permissions } = useAuth();

  const hasPermission = (requiredPermissions?: string[]): boolean => {
    if (!requiredPermissions || requiredPermissions.length === 0) {
      return true;
    }
    
    if (!permissions) {
      return false;
    }

    const permissionMap: Record<string, boolean> = {
      'can_view_dashboard': permissions.can_view_dashboard,
      'can_view_resources': permissions.can_view_dashboard, // For now, map to dashboard
      'can_view_monitoring': permissions.can_view_alerts,
      'can_view_alerts': permissions.can_view_alerts, // Add mapping for alerts & insights
      'can_view_kubernetes': permissions.can_view_pod_analyzer,
      'can_view_costs': permissions.can_view_cost_analyzer,
      'can_manage_automation': permissions.can_execute_remediation,
      'can_view_settings': permissions.can_manage_users || permissions.can_manage_roles,
    };

    return requiredPermissions.some(permission => 
      permissionMap[permission] === true
    );
  };

  const visibleItems = navigationItems.filter(item => hasPermission(item.requiredPermissions));

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="px-4 sm:px-6 lg:px-8">
        
        {/* Desktop Navigation */}
        <div className="hidden md:block">
          <div className="flex space-x-8">
            {visibleItems.map((item) => (
              <NavLink
                key={item.id}
                to={item.path}
                className={({ isActive }) =>
                  `group flex items-center px-1 py-4 text-sm font-medium border-b-2 transition-colors duration-200 ${
                    isActive
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:border-gray-300'
                  }`
                }
              >
                <i className={`${item.icon} mr-2 text-sm`}></i>
                <span>{item.name}</span>
                
                {/* Tooltip */}
                <div className="absolute invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-gray-900 text-white text-xs rounded py-1 px-2 mt-12 ml-4 whitespace-nowrap z-50">
                  {item.description}
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-b-gray-900"></div>
                </div>
              </NavLink>
            ))}
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden">
          <div className="flex overflow-x-auto py-2 space-x-4">
            {visibleItems.map((item) => (
              <NavLink
                key={item.id}
                to={item.path}
                className={({ isActive }) =>
                  `flex-shrink-0 flex flex-col items-center px-3 py-2 text-xs font-medium rounded-md transition-colors duration-200 ${
                    isActive
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`
                }
              >
                <i className={`${item.icon} text-lg mb-1`}></i>
                <span className="whitespace-nowrap">{item.name}</span>
              </NavLink>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
} 