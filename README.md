# 🧠 GenAI CloudOps Dashboard

<div align="center">

![Project Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**An AI-powered cloud operations monitoring and management platform for Oracle Cloud Infrastructure (OCI)**

[View Dashboard](./index.html) • [Documentation](#documentation) • [Contributing](#contributing) • [Support](#support)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## 🌟 Overview

The **GenAI CloudOps Dashboard** is a comprehensive web application that revolutionizes cloud operations management by combining real-time monitoring, AI-powered insights, and automated remediation capabilities. It monitors Oracle Cloud Infrastructure (OCI) resources, provides intelligent alerts, and uses GenAI to recommend and apply fixes with user approval.

### 🎯 Key Objectives

- **Monitor** OCI resources (VMs, Databases, Kubernetes, Load Balancers) with real-time metrics
- **Analyze** system health and performance using AI-powered insights
- **Remediate** issues automatically with GenAI-recommended solutions
- **Optimize** costs and resource utilization through intelligent recommendations
- **Secure** infrastructure with unified access control analysis

---

## ✨ Features

### 🖥️ Core Dashboard
- **Resource Monitoring**: Real-time visibility into VMs, Databases, OKE clusters, API Gateway, and Load Balancers
- **Live Metrics**: CPU, Memory, Network usage, and Health status monitoring
- **Compartment Filtering**: Toggle between different OCI compartments and projects
- **Interactive Charts**: Dynamic visualizations for resource utilization and trends

### 🚨 Alerts & Insights
- **Smart Alerting**: Summary of alerts from OCI Monitoring with natural language explanations
- **AI-Powered Analysis**: GenAI model provides context-aware issue interpretation
- **Predictive Insights**: Proactive identification of potential problems
- **Custom Notifications**: Configurable alert thresholds and notification channels

### 🔧 Remediation Engine
- **AI Recommendations**: GenAI-generated remediation suggestions for identified issues
- **Approval Workflow**: "Approve & Apply" mechanism for safe automation
- **Infrastructure as Code**: Automated execution via OCI CLI and Terraform
- **Audit Trail**: Complete logging of all remediation actions and outcomes

### 💬 Conversational Agent
- **Natural Language Interface**: Chat with your infrastructure using plain English
- **Contextual Responses**: AI understands your cloud environment and provides relevant answers
- **Query Examples**:
  - "What's wrong with my web server?"
  - "How can I reduce my monthly costs?"
  - "Show me pods with high memory usage"

### 🔐 Access Analyzer
- **RBAC Visualization**: Graph-based view of Kubernetes role bindings and permissions
- **IAM Policy Analysis**: Comprehensive Oracle Cloud IAM policy evaluation
- **Security Scoring**: Risk assessment with color-coded severity levels
- **Hardening Recommendations**: AI-suggested security improvements

### 📊 Pod Health & Log Analyzer
- **Container Monitoring**: Real-time OKE cluster pod status tracking
- **Error Detection**: Automatic identification of CrashLoopBackOff and failing pods
- **Log Analysis**: AI-powered log summarization and root cause analysis
- **Performance Insights**: Resource usage patterns and optimization suggestions

### 💰 Cost Analyzer
- **Cost Tracking**: Monthly spending analysis and trend visualization
- **Resource Optimization**: Identification of top costly resources with optimization recommendations
- **Anomaly Detection**: Unusual spending pattern alerts
- **Savings Recommendations**: AI-suggested cost reduction strategies

---

## 🏗️ Architecture

### System Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React + Tailwind CSS]
        WS[WebSocket Client]
        RQ[React Query]
    end
    
    subgraph "API Gateway"
        GW[Unified API Gateway]
        AUTH[Authentication]
        RATE[Rate Limiting]
    end
    
    subgraph "Backend Microservices"
        DASH[Dashboard Service]
        ALERT[Alerts Service]
        REM[Remediation Service]
        ACCESS[Access Analyzer]
        POD[Pod Analyzer]
        COST[Cost Analyzer]
        CHAT[Chat Service]
    end
    
    subgraph "AI & Integration Layer"
        GENAI[GenAI Service]
        OCI[OCI SDK]
        K8S[Kubernetes Client]
        TERRA[Terraform Runner]
    end
    
    subgraph "Data Layer"
        CACHE[Redis Cache]
        LOGS[Audit Logs]
        VAULT[OCI Vault]
    end
    
    UI --> GW
    WS --> GW
    GW --> DASH
    GW --> ALERT
    GW --> REM
    GW --> ACCESS
    GW --> POD
    GW --> COST
    GW --> CHAT
    
    DASH --> OCI
    ALERT --> OCI
    REM --> TERRA
    ACCESS --> K8S
    ACCESS --> OCI
    POD --> K8S
    COST --> OCI
    CHAT --> GENAI
    
    GENAI --> CACHE
    OCI --> VAULT
    REM --> LOGS
```

### 🧩 Component Architecture

#### Frontend Components
- **Unified Dashboard**: Single React application with tabbed navigation
- **Real-time Updates**: WebSocket connections for live data streaming
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **State Management**: React Query for server state and caching

#### Backend Services
- **Modular Microservices**: Domain-specific FastAPI services
- **API Gateway**: Centralized routing and middleware
- **Authentication**: RBAC with optional OCI IAM integration
- **WebSocket Support**: Real-time bidirectional communication

#### AI Integration
- **GenAI Service**: Centralized AI processing with prompt engineering
- **Response Caching**: Redis-based caching for performance optimization
- **Context Management**: Maintains conversation state and infrastructure context

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Query for server state
- **Charts**: Chart.js or D3.js for data visualization
- **Icons**: Font Awesome or Heroicons
- **Build Tool**: Vite or Create React App

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **API Documentation**: OpenAPI/Swagger auto-generation
- **WebSockets**: FastAPI WebSocket support
- **Authentication**: JWT with optional OAuth integration
- **Validation**: Pydantic models

### Infrastructure & DevOps
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes (OCI OKE)
- **Service Mesh**: Istio (optional)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or OCI Logging

### Cloud & AI Services
- **Cloud Provider**: Oracle Cloud Infrastructure (OCI)
- **AI Services**: OpenAI API or OCI GenAI
- **Secret Management**: OCI Vault
- **Container Registry**: OCI Container Registry
- **Load Balancing**: OCI Load Balancer

### Development Tools
- **Version Control**: Git with GitHub/GitLab
- **CI/CD**: GitHub Actions or GitLab CI
- **Testing**: pytest (backend), Jest/React Testing Library (frontend)
- **Code Quality**: ESLint, Prettier, Black, mypy
- **Documentation**: Swagger/OpenAPI, Storybook

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18+ recommended)
- **Python** (v3.9+ required)
- **Docker** (v20+ recommended)
- **Git** (latest version)
- **OCI CLI** (configured with valid credentials)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/genai-cloudops-dashboard.git
   cd genai-cloudops-dashboard
   ```

2. **View the current project status**
   ```bash
   # Open the dashboard to see current progress
   open dashboard.html
   ```

3. **Set up development environment** (when Task-001 is completed)
   ```bash
   # Install frontend dependencies
   cd frontend
   npm install

   # Install backend dependencies
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OCI credentials and API keys
   ```

5. **Start development servers**
   ```bash
   # Start backend (when available)
   cd backend
   uvicorn main:app --reload --port 8000

   # Start frontend (when available)
   cd frontend
   npm run dev
   ```

---

## ⚙️ Installation

### Development Setup

#### Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest
```

#### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

### Production Deployment

#### Using Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Using Helm (Kubernetes)
```bash
# Add Helm repository
helm repo add genai-cloudops ./deployment/helm

# Install the application
helm install genai-cloudops genai-cloudops/genai-cloudops-dashboard \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=dashboard.yourdomain.com
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# OCI Configuration
OCI_CONFIG_FILE=/path/to/oci/config
OCI_PROFILE=DEFAULT
OCI_COMPARTMENT_ID=ocid1.compartment.oc1..xxxxx

# GenAI Configuration
OPENAI_API_KEY=your_openai_api_key
GENAI_MODEL=gpt-4
GENAI_MAX_TOKENS=2048

# Database Configuration
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:password@localhost/genai_cloudops

# Application Configuration
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here

# Security Configuration
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Monitoring Configuration
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
```

### OCI Configuration

1. **Install OCI CLI**
   ```bash
   pip install oci-cli
   oci setup config
   ```

2. **Configure authentication**
   ```bash
   # Follow prompts to set up API keys
   oci iam user list
   ```

3. **Verify access**
   ```bash
   oci compute instance list --compartment-id <your-compartment-id>
   ```

---

## 📖 Usage

### Dashboard Navigation

#### 1. Main Dashboard
- View overall infrastructure health
- Monitor resource utilization
- Access quick actions and insights

#### 2. Alerts & Insights
- Review active alerts and recommendations
- Analyze system performance trends
- Configure notification preferences

#### 3. Remediation Panel
- Review AI-generated recommendations
- Approve and execute fixes
- Track remediation history

#### 4. Access Analyzer
- Visualize RBAC and IAM policies
- Identify security risks
- Apply recommended hardening

#### 5. Pod Analyzer
- Monitor Kubernetes pod health
- Analyze container logs
- Troubleshoot deployment issues

#### 6. Cost Analyzer
- Track spending and trends
- Identify optimization opportunities
- Generate cost reports

### Conversational Interface

```bash
# Example queries you can ask the AI assistant:
"Show me all unhealthy pods in production"
"What's causing high CPU usage on web-server-01?"
"How can I reduce storage costs this month?"
"List all security vulnerabilities in my cluster"
"Recommend optimizations for my database performance"
```

### API Usage

#### Authentication
```bash
# Get access token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

#### Resource Monitoring
```bash
# Get resource status
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/resources/status"

# Get specific resource metrics
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/resources/vm/ocid1.instance.oc1..xxxxx/metrics"
```

---

## 📚 API Documentation

### Core Endpoints

#### Dashboard Service
- `GET /api/v1/dashboard/overview` - Overall system status
- `GET /api/v1/dashboard/metrics` - Real-time metrics
- `GET /api/v1/dashboard/resources` - Resource inventory

#### Alerts Service
- `GET /api/v1/alerts` - List active alerts
- `POST /api/v1/alerts/acknowledge` - Acknowledge alert
- `GET /api/v1/alerts/insights` - AI-generated insights

#### Remediation Service
- `GET /api/v1/remediation/recommendations` - Get recommendations
- `POST /api/v1/remediation/execute` - Execute approved remediation
- `GET /api/v1/remediation/history` - Remediation audit log

#### Chat Service
- `POST /api/v1/chat/message` - Send message to AI assistant
- `GET /api/v1/chat/history` - Get conversation history
- `WebSocket /ws/chat` - Real-time chat interface

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Current user info
- `POST /auth/refresh` - Refresh token

### Interactive API Documentation

Once the application is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🚀 Deployment

### Local Development
```bash
# Start all services with Docker Compose
docker-compose -f docker-compose.dev.yml up -d
```

### Staging Environment
```bash
# Deploy to staging with Helm
helm upgrade --install genai-cloudops-staging ./deployment/helm \
  --namespace staging \
  --set environment=staging \
  --set image.tag=staging-latest
```

### Production Deployment

#### Prerequisites
- OCI OKE cluster configured
- OCI Vault with secrets configured
- Domain name and SSL certificates
- Monitoring and logging infrastructure

#### Deployment Steps
```bash
# 1. Build and push container images
docker build -t genai-cloudops/frontend:latest ./frontend
docker build -t genai-cloudops/backend:latest ./backend

# 2. Push to OCI Container Registry
docker tag genai-cloudops/frontend:latest <region>.ocir.io/<tenancy>/genai-cloudops/frontend:latest
docker push <region>.ocir.io/<tenancy>/genai-cloudops/frontend:latest

# 3. Deploy with Helm
helm upgrade --install genai-cloudops ./deployment/helm \
  --namespace production \
  --set environment=production \
  --set image.repository=<region>.ocir.io/<tenancy>/genai-cloudops \
  --set image.tag=latest \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=dashboard.yourdomain.com \
  --set vault.enabled=true
```

### Monitoring and Observability
```bash
# Install monitoring stack
helm install prometheus prometheus-community/kube-prometheus-stack
helm install grafana grafana/grafana

# Configure alerts
kubectl apply -f deployment/monitoring/alerts.yaml
```

---

## 🔒 Security

### Security Features
- **Authentication**: JWT-based authentication with role-based access control
- **Authorization**: Fine-grained permissions for different user roles
- **Encryption**: All data encrypted in transit (TLS) and at rest
- **Secret Management**: OCI Vault integration for secure credential storage
- **Input Validation**: Comprehensive input sanitization and validation
- **Rate Limiting**: API rate limiting to prevent abuse
- **Audit Logging**: Complete audit trail of all actions

### Security Best Practices

#### Authentication & Authorization
```python
# Example RBAC configuration
ROLES = {
    "admin": ["read", "write", "execute", "manage"],
    "operator": ["read", "write", "execute"],
    "viewer": ["read"]
}
```

#### Secret Management
```bash
# Store secrets in OCI Vault
oci vault secret create-base64 \
  --secret-name "genai-api-key" \
  --secret-content-content "your-secret-key" \
  --vault-id <vault-ocid>
```

#### Network Security
- Use private subnets for backend services
- Implement network segmentation
- Configure security groups and NACLs
- Enable VPN or bastion host access

---

## 🧪 Testing

### Running Tests

#### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m "unit"
pytest -m "integration"
pytest -m "e2e"
```

#### Frontend Tests
```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e
```

### Test Categories

#### Unit Tests
- Component functionality
- Service logic
- Utility functions
- API endpoints

#### Integration Tests
- Database interactions
- External service integrations
- API workflows
- Authentication flows

#### End-to-End Tests
- Complete user workflows
- Cross-service communication
- UI interactions
- Performance benchmarks

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite**
   ```bash
   npm test && pytest
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add amazing new feature"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/amazing-new-feature
   ```
8. **Create a Pull Request**

### Code Standards
- Follow TypeScript/ESLint rules for frontend
- Follow PEP 8 and use Black for Python backend
- Write comprehensive tests for new features
- Update documentation for API changes
- Use conventional commit messages

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Getting Help

- **Documentation**: [Project Wiki](https://github.com/your-org/genai-cloudops-dashboard/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-org/genai-cloudops-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/genai-cloudops-dashboard/discussions)
- **Email**: support@yourcompany.com

### Troubleshooting

#### Common Issues

**Issue**: OCI authentication failed
```bash
# Solution: Verify OCI CLI configuration
oci iam user list
```

**Issue**: GenAI service unavailable
```bash
# Solution: Check API key and service status
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**Issue**: Kubernetes connection failed
```bash
# Solution: Verify kubeconfig
kubectl cluster-info
```

### Performance Optimization

#### Frontend Performance
- Use React.memo for expensive components
- Implement virtual scrolling for large tables
- Optimize bundle size with code splitting
- Use service workers for caching

#### Backend Performance
- Implement Redis caching for frequently accessed data
- Use connection pooling for database connections
- Optimize database queries with indexes
- Use async/await for I/O operations

---

## 🗓️ Roadmap

### Phase 1: Foundation (Q1 2025)
- [x] Project planning and architecture design
- [ ] Basic infrastructure setup
- [ ] Core dashboard implementation
- [ ] Authentication and authorization

### Phase 2: Core Features (Q2 2025)
- [ ] Real-time monitoring integration
- [ ] AI-powered insights engine
- [ ] Basic remediation capabilities
- [ ] Cost analysis features

### Phase 3: Advanced Features (Q3 2025)
- [ ] Conversational AI interface
- [ ] Advanced security analysis
- [ ] Pod health monitoring
- [ ] Performance optimization

### Phase 4: Production Ready (Q4 2025)
- [ ] Comprehensive testing
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Documentation completion

---

## 📊 Project Status

| Component | Status | Progress |
|-----------|--------|----------|
| Project Planning | ✅ Complete | 100% |
| Architecture Design | ✅ Complete | 100% |
| Development Setup | ⏳ Pending | 0% |
| Frontend Development | ⏳ Pending | 0% |
| Backend Development | ⏳ Pending | 0% |
| AI Integration | ⏳ Pending | 0% |
| Testing | ⏳ Pending | 0% |
| Deployment | ⏳ Pending | 0% |

**Overall Progress: 3.3%** | **Next Milestone: Development Environment Setup**

---

<div align="center">

**Built with ❤️ for the cloud operations community**

[⬆ Back to top](#-genai-cloudops-dashboard)

</div> 
