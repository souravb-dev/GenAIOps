/**
 * MSW API handlers for mocking backend endpoints
 * Provides realistic mock responses for all API calls
 */

import { http, HttpResponse } from 'msw';

// Mock data
const mockUser = {
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  full_name: 'Admin User',
  is_active: true,
  roles: ['admin']
};

const mockToken = {
  access_token: 'mock-jwt-token',
  token_type: 'bearer',
  expires_in: 3600
};

const mockInstances = [
  {
    id: 'ocid1.instance.oc1.us-ashburn-1.test1',
    display_name: 'web-server-1',
    lifecycle_state: 'RUNNING',
    availability_domain: 'US-ASHBURN-AD-1',
    shape: 'VM.Standard2.1',
    time_created: '2024-01-01T00:00:00Z',
    cpu_utilization: 45.2,
    memory_utilization: 67.8
  },
  {
    id: 'ocid1.instance.oc1.us-ashburn-1.test2',
    display_name: 'database-server',
    lifecycle_state: 'STOPPED',
    availability_domain: 'US-ASHBURN-AD-2',
    shape: 'VM.Standard2.2',
    time_created: '2024-01-02T00:00:00Z',
    cpu_utilization: 0,
    memory_utilization: 0
  }
];

const mockPods = [
  {
    metadata: {
      name: 'frontend-pod-1',
      namespace: 'default',
      labels: { app: 'frontend' }
    },
    status: {
      phase: 'Running',
      pod_ip: '10.0.1.1'
    },
    spec: {
      containers: [
        { name: 'frontend', image: 'nginx:latest' }
      ]
    }
  },
  {
    metadata: {
      name: 'backend-pod-1',
      namespace: 'default',
      labels: { app: 'backend' }
    },
    status: {
      phase: 'Running',
      pod_ip: '10.0.1.2'
    },
    spec: {
      containers: [
        { name: 'backend', image: 'python:3.9' }
      ]
    }
  }
];

const mockAlerts = [
  {
    id: 'alert-1',
    severity: 'warning',
    title: 'High CPU Usage',
    description: 'Instance web-server-1 CPU usage is above 80%',
    timestamp: '2024-01-01T12:00:00Z',
    status: 'active',
    resource_id: 'ocid1.instance.oc1.us-ashburn-1.test1'
  },
  {
    id: 'alert-2',
    severity: 'error',
    title: 'Service Down',
    description: 'Database service is not responding',
    timestamp: '2024-01-01T11:30:00Z',
    status: 'resolved',
    resource_id: 'ocid1.instance.oc1.us-ashburn-1.test2'
  }
];

const mockRemediationActions = [
  {
    id: 'action-1',
    name: 'Restart Service',
    description: 'Restart the application service',
    status: 'completed',
    created_at: '2024-01-01T10:00:00Z',
    executed_at: '2024-01-01T10:05:00Z',
    resource_id: 'ocid1.instance.oc1.us-ashburn-1.test1'
  }
];

const mockChatHistory = [
  {
    id: 'msg-1',
    role: 'user',
    content: 'What is the status of my instances?',
    timestamp: '2024-01-01T09:00:00Z'
  },
  {
    id: 'msg-2',
    role: 'assistant',
    content: 'You have 2 instances: web-server-1 is running, and database-server is stopped.',
    timestamp: '2024-01-01T09:00:05Z'
  }
];

export const handlers = [
  // Authentication endpoints
  http.post('*/api/v1/auth/login', async ({ request }) => {
    const body = await request.json() as any;
    
    if (body.username === 'admin' && body.password === 'admin123') {
      return HttpResponse.json(mockToken);
    }
    
    return HttpResponse.json(
      { detail: 'Invalid credentials' },
      { status: 401 }
    );
  }),

  http.post('*/api/v1/auth/logout', () => {
    return HttpResponse.json({ message: 'Logged out successfully' });
  }),

  http.get('*/api/v1/auth/me', ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    
    if (authHeader?.includes('mock-jwt-token')) {
      return HttpResponse.json(mockUser);
    }
    
    return HttpResponse.json(
      { detail: 'Unauthorized' },
      { status: 401 }
    );
  }),

  // Cloud/OCI endpoints
  http.get('*/api/v1/cloud/instances', () => {
    return HttpResponse.json(mockInstances);
  }),

  http.get('*/api/v1/cloud/instances/:instanceId', ({ params }) => {
    const instance = mockInstances.find(i => i.id === params.instanceId);
    
    if (instance) {
      return HttpResponse.json(instance);
    }
    
    return HttpResponse.json(
      { detail: 'Instance not found' },
      { status: 404 }
    );
  }),

  http.post('*/api/v1/cloud/instances/:instanceId/start', ({ params }) => {
    return HttpResponse.json({
      message: `Instance ${params.instanceId} start initiated`
    });
  }),

  http.post('*/api/v1/cloud/instances/:instanceId/stop', ({ params }) => {
    return HttpResponse.json({
      message: `Instance ${params.instanceId} stop initiated`
    });
  }),

  // Kubernetes endpoints
  http.get('*/api/v1/kubernetes/pods', () => {
    return HttpResponse.json(mockPods);
  }),

  http.get('*/api/v1/kubernetes/pods/:podName/logs', ({ params }) => {
    return HttpResponse.json({
      logs: [
        '2024-01-01T12:00:00Z INFO: Application started',
        '2024-01-01T12:01:00Z INFO: Processing request',
        '2024-01-01T12:02:00Z WARN: High memory usage detected',
        '2024-01-01T12:03:00Z INFO: Request completed'
      ]
    });
  }),

  // Monitoring endpoints
  http.get('*/api/v1/monitoring/alerts', () => {
    return HttpResponse.json(mockAlerts);
  }),

  http.get('*/api/v1/monitoring/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      services: {
        database: 'healthy',
        oci: 'healthy',
        kubernetes: 'healthy'
      },
      timestamp: new Date().toISOString()
    });
  }),

  http.get('*/api/v1/monitoring/metrics', () => {
    return HttpResponse.json({
      cpu_usage: 45.2,
      memory_usage: 67.8,
      disk_usage: 23.1,
      network_io: 12.5,
      timestamp: new Date().toISOString()
    });
  }),

  // Remediation endpoints
  http.get('*/api/v1/remediation/actions', () => {
    return HttpResponse.json(mockRemediationActions);
  }),

  http.post('*/api/v1/remediation/actions', async ({ request }) => {
    const body = await request.json() as any;
    
    const newAction = {
      id: `action-${Date.now()}`,
      name: body.name,
      description: body.description,
      status: 'pending',
      created_at: new Date().toISOString(),
      resource_id: body.resource_id
    };
    
    return HttpResponse.json(newAction, { status: 201 });
  }),

  http.post('*/api/v1/remediation/actions/:actionId/execute', ({ params }) => {
    return HttpResponse.json({
      message: `Action ${params.actionId} execution started`
    });
  }),

  // GenAI/Chatbot endpoints
  http.get('*/api/v1/chatbot/history', () => {
    return HttpResponse.json(mockChatHistory);
  }),

  http.post('*/api/v1/chatbot/chat', async ({ request }) => {
    const body = await request.json() as any;
    
    // Simulate AI response based on input
    let response = 'I can help you with cloud operations and monitoring.';
    
    if (body.message.toLowerCase().includes('instance')) {
      response = 'You have 2 instances: web-server-1 is running and database-server is stopped.';
    } else if (body.message.toLowerCase().includes('alert')) {
      response = 'You have 1 active alert: High CPU usage on web-server-1.';
    } else if (body.message.toLowerCase().includes('pod')) {
      response = 'You have 2 pods running in the default namespace.';
    }
    
    return HttpResponse.json({
      response,
      timestamp: new Date().toISOString()
    });
  }),

  // GenAI endpoints
  http.post('*/api/v1/genai/analyze', async ({ request }) => {
    const body = await request.json() as any;
    
    return HttpResponse.json({
      analysis: `Analysis of ${body.context}: This appears to be a ${body.type} issue that can be resolved by following these steps...`,
      recommendations: [
        'Check system resources',
        'Review logs for errors',
        'Consider scaling if needed'
      ],
      confidence: 0.85
    });
  }),

  http.post('*/api/v1/genai/suggest-remediation', async ({ request }) => {
    const body = await request.json() as any;
    
    return HttpResponse.json({
      suggestions: [
        {
          action: 'restart_service',
          description: 'Restart the affected service',
          priority: 'high',
          estimated_time: '2 minutes'
        },
        {
          action: 'scale_up',
          description: 'Scale up the instance',
          priority: 'medium',
          estimated_time: '5 minutes'
        }
      ]
    });
  }),

  // Access Analyzer endpoints
  http.get('*/api/v1/access/analysis', () => {
    return HttpResponse.json({
      findings: [
        {
          id: 'finding-1',
          type: 'excessive_permissions',
          severity: 'medium',
          resource: 'IAM User: test-user',
          description: 'User has more permissions than required',
          recommendation: 'Remove unused permissions'
        }
      ],
      summary: {
        total_findings: 1,
        high_severity: 0,
        medium_severity: 1,
        low_severity: 0
      }
    });
  }),

  // Cost Analyzer endpoints
  http.get('*/api/v1/cost/analysis', () => {
    return HttpResponse.json({
      total_cost: 245.67,
      cost_by_service: {
        'Compute': 150.00,
        'Storage': 45.67,
        'Network': 50.00
      },
      recommendations: [
        {
          service: 'Compute',
          potential_savings: 25.00,
          recommendation: 'Right-size underutilized instances'
        }
      ]
    });
  }),

  // Vault endpoints
  http.get('*/api/v1/vault/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      vault_enabled: true,
      vault_accessible: true,
      secret_count: 5,
      timestamp: new Date().toISOString()
    });
  }),

  http.get('*/api/v1/vault/stats', () => {
    return HttpResponse.json({
      total_secrets: 5,
      secrets_by_type: {
        'api_key': 2,
        'database_password': 1,
        'jwt_secret': 1,
        'generic': 1
      },
      cache_stats: {
        total_cached: 3,
        active_cached: 3,
        cache_ttl_minutes: 15
      },
      vault_enabled: true
    });
  }),

  // Notifications endpoints
  http.get('*/api/v1/notifications', () => {
    return HttpResponse.json([
      {
        id: 'notif-1',
        type: 'alert',
        title: 'High CPU Usage Alert',
        message: 'Instance web-server-1 CPU usage is above 80%',
        severity: 'warning',
        timestamp: '2024-01-01T12:00:00Z',
        read: false
      }
    ]);
  }),

  http.put('*/api/v1/notifications/:notificationId/read', ({ params }) => {
    return HttpResponse.json({
      message: `Notification ${params.notificationId} marked as read`
    });
  }),

  // Health check
  http.get('*/api/v1/health', () => {
    return HttpResponse.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    });
  }),

  // WebSocket simulation (for testing)
  http.get('*/api/v1/ws/*', () => {
    return HttpResponse.json({
      message: 'WebSocket connection established',
      status: 'connected'
    });
  }),

  // Fallback for unhandled requests
  http.get('*/api/*', ({ request }) => {
    console.warn(`Unhandled request: ${request.method} ${request.url}`);
    return HttpResponse.json(
      { detail: 'Endpoint not implemented in mock' },
      { status: 501 }
    );
  })
]; 