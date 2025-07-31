import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  actionable?: boolean;
  resourceId?: string;
  resourceType?: string;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback((notificationData: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notificationData,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      read: false,
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Auto-remove success notifications after 5 seconds
    if (notificationData.type === 'success') {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== newNotification.id));
      }, 5000);
    }
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  // Real-time OCI monitoring integration
  useEffect(() => {
    const fetchRealTimeNotifications = async () => {
      try {
        // Get selected compartment from local storage or context
        const selectedCompartmentId = localStorage.getItem('selectedCompartmentId');
        if (!selectedCompartmentId) return;

        const response = await fetch(`/api/notifications/real-time?compartment_id=${selectedCompartmentId}&hours_back=24`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const realTimeNotifications = await response.json();
          
          // Add new notifications that we don't already have
          const existingIds = new Set(notifications.map(n => n.id));
          const newNotifications = realTimeNotifications.filter((n: any) => !existingIds.has(n.id));
          
          if (newNotifications.length > 0) {
            setNotifications(prev => [...newNotifications, ...prev]);
            console.log(`Added ${newNotifications.length} real-time notifications from OCI monitoring`);
          }
        }
      } catch (error) {
        console.warn('Failed to fetch real-time notifications:', error);
        // Fail silently - don't disrupt user experience
      }
    };

    // Fetch immediately
    fetchRealTimeNotifications();

    // Set up polling every 2 minutes for real-time updates
    const interval = setInterval(fetchRealTimeNotifications, 120000);

    return () => clearInterval(interval);
  }, [notifications]); // Re-run when notifications change to avoid duplicates

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        addNotification,
        markAsRead,
        markAllAsRead,
        removeNotification,
        clearAll,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
} 