# DevOps Concepts & Implementation Guide

## Overview

This document explains the DevOps principles, methodologies, and architectural patterns demonstrated in the RiskGuard AI project.

---

## 1. CI/CD Pipeline (Continuous Integration / Continuous Deployment)

### What is CI/CD?

**Continuous Integration (CI):** Developers integrate code into a shared repository multiple times per day. Each integration is automatically tested.

**Continuous Deployment (CD):** Every change that passes automated tests is automatically deployed to production.

### Implementation in RiskGuard

**GitHub Actions Workflow** (`.github/workflows/deploy.yml`):

```
Push to Repository
        ↓
├─ Lint & Format Check (ESLint, Flake8)
├─ Unit Tests (pytest, Jest)
├─ Build Docker Images
├─ Push to Docker Registry
└─ Deploy to Staging/Production
```

### Benefits

- ✅ **Faster Feedback**: Issues detected immediately
- ✅ **Reduced Risk**: Smaller, more frequent deployments
- ✅ **Automated Process**: Remove manual errors
- ✅ **Rapid Iteration**: Deploy multiple times per day

### Stages Explained

#### 1. **Source Control**
```bash
# Developers push code
git commit -m "Add new feature"
git push origin feature-branch
```

#### 2. **Automated Testing**
```bash
# Backend tests
pytest backend/tests -v --cov=app

# Frontend tests
npm test
```

#### 3. **Build Artifacts**
```bash
# Create Docker images
docker build -f docker/Dockerfile.backend -t riskguard-backend:latest .
docker build -f docker/Dockerfile.frontend -t riskguard-frontend:latest .
```

#### 4. **Repository Push**
```bash
# Push to Docker Hub/ECR
docker push your-registry/riskguard-backend:latest
docker push your-registry/riskguard-frontend:latest
```

#### 5. **Automated Deployment**
```bash
# Staging (develop branch)
curl -X POST deploy-staging-webhook

# Production (main branch)
curl -X POST deploy-production-webhook
```

### GitHub Secrets for Security
```
DOCKER_USERNAME    # Docker registry credentials
DOCKER_PASSWORD
RENDER_API_KEY     # Deployment provider token
```

---

## 2. Containerization

### What is Containerization?

Packaging applications with all dependencies (code, runtime, libraries) into isolated, lightweight containers that run consistently anywhere.

### Container vs Virtual Machine

```
Traditional VM Approach:
┌─────────────┐
│ App 1       │
├─────────────┤
│ OS (Linux)  │  } 2-4 GB per VM
├─────────────┤
│ Hypervisor  │
└─────────────┘
Startup: 1-2 minutes

Container Approach:
┌─────────────┐
│ App 1       │
├─────────────┤
│ Minimal OS  │  } 50-100 MB per container
├─────────────┤
│ Container   │
│ Runtime     │
└─────────────┘
Startup: 100-500 ms
```

### Docker Images in RiskGuard

#### Multi-Stage Build (Efficiency)

**Backend Dockerfile:**
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim
WORKDIR /app
RUN pip install -r requirements.txt
# ... rest of build

# Stage 2: Runtime
FROM python:3.11-slim  # Fresh, smaller base
COPY --from=builder /app /app
CMD ["python", "-m", "uvicorn", "app.main:app"]
```

Benefits:
- Smaller final image (~200 MB vs 800 MB)
- Faster builds
- Reduced attack surface

#### Docker Compose for Local Development

```yaml
services:
  postgres:     # Database service
  backend:      # API service
  frontend:     # Web UI
  prometheus:   # Metrics
  grafana:      # Dashboards
```

### Image Layers

```
Layer 1: FROM python:3.11-slim
Layer 2: RUN pip install requirements.txt
Layer 3: COPY backend /app
Layer 4: EXPOSE 8000
Layer 5: CMD ["python", "-m", "uvicorn", "..."]
```

Docker caches each layer → faster rebuilds.

### Container Networking

```
┌──────────────────────────────────────┐
│      Docker Network (bridge)         │
├──────────────┬───────────┬───────────┤
│              │           │           │
│ frontend     │ backend   │ postgres  │
│ :80          │ :8000     │ :5432     │
│              │           │           │
└──────────────┴───────────┴───────────┘

Service Discovery via DNS:
- backend.riskguard-network:8000
- postgres.riskguard-network:5432
```

---

## 3. Infrastructure as Code (IaC) with Terraform

### What is IaC?

Managing infrastructure (servers, networks, databases) as code files instead of manual clicking in web consoles.

### Benefits

- 📝 **Version Control**: Track infrastructure changes
- 🔄 **Reproducibility**: Deploy identical environments
- 🤖 **Automation**: Deploy with one command
- 👥 **Collaboration**: Review infrastructure changes in PRs

### Terraform Architecture

**Terraform Workflow:**

```
1. Write Code (main.tf, variables.tf)
   ↓
2. terraform init
   ↓
3. terraform plan  (Preview changes)
   ↓
4. terraform apply (Apply changes)
   ↓
5. terraform state (Track current state)
```

### RiskGuard Infrastructure

**VPC (Virtual Private Cloud):**
```
┌─────────────────────────────────────┐
│     AWS VPC (10.0.0.0/16)           │
├─────────────────┬───────────────────┤
│  Public Subnet  │  Private Subnet   │
│  (10.0.0.0/24)  │  (10.0.2.0/24)    │
│                 │                   │
│  ┌─────────┐    │  ┌──────────┐     │
│  │   ALB   │────┤  │PostgreSQL│     │
│  └─────────┘    │  └──────────┘     │
│                 │                   │
│  ┌─────────┐    │                   │
│  │   ECS   │    │                   │
│  │  Tasks  │    │                   │
│  └─────────┘    │                   │
│                 │                   │
└─────────────────┴───────────────────┘
        ↑
    Internet Gateway
        ↑
   Route 53 (DNS)
        ↑
    Users
```

### Key Infrastructure Resources

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

# Subnets
resource "aws_subnet" "public" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.0.0/24"
}

# Security Groups (Firewalls)
resource "aws_security_group" "alb" {
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Open to internet
  }
}

# Database
resource "aws_db_instance" "postgres" {
  engine = "postgres"
  instance_class = "db.t3.small"
  allocated_storage = 50
}

# Load Balancer
resource "aws_lb" "main" {
  name = "riskguard-alb"
  subnets = [aws_subnet.public[0].id, aws_subnet.public[1].id]
}
```

### Terraform State Management

**Local State:**
```
terraform.tfstate  # Current infrastructure state
terraform.tfstate.backup
```

**Remote State (Best Practice):**
```
S3 Bucket: riskguard-terraform-state
  - Shared across team
  - Versioning enabled
  - DynamoDB locks (prevent conflicts)
```

### Deployment vs Destroy

```bash
# Create/Update
terraform apply -var-file="prod.tfvars"

# Preview
terraform plan

# Remove all
terraform destroy
```

---

## 4. Microservices Architecture

### Monolith vs Microservices

**Monolith:**
```
Single Codebase
    ↓
Single Application
    ↓
Single Database
    ↓
Tight Coupling
```

**Microservices:**
```
Service 1     Service 2     Service 3
(Frontend)    (Backend)    (Database)
    ↓             ↓             ↓
Independent   Independent   Independent
Deployments   Scaling       Databases
```

### RiskGuard Microservices

```
┌─────────────────────────────────────────────┐
│         Frontend Service                    │
│  React + Vite (Port 3000)                   │
│  - Can scale independently                  │
│  - Updated without backend restarts         │
└──────────────────┬──────────────────────────┘
                   │ API Calls
                   ↓
┌─────────────────────────────────────────────┐
│  Backend API Service                        │
│  FastAPI (Port 8000)                        │
│  - Controllers (HTTP endpoints)             │
│  - Services (Business logic)                │
│  - Models (Data structures)                 │
│  - Async for scalability                    │
└──────────────────┬──────────────────────────┘
                   │ SQL Queries
                   ↓
┌─────────────────────────────────────────────┐
│  Database Service                           │
│  PostgreSQL (Port 5432)                     │
│  - Persists user data                       │
│  - ACID compliance                          │
│  - Read replicas for scaling                │
└─────────────────────────────────────────────┘
```

### Benefits

- **Independent Scaling**: Scale backend without frontend
- **Technology Diversity**: Use best language for each service
- **Resilience**: Failure in one service doesn't crash all
- **Deployment Speed**: Update one service without full deployment

---

## 5. Containerization Orchestration

### From Docker to Docker Compose to Kubernetes

**Development:**
```
Docker Compose (Single host)
  - Perfect for local development
  - All services in one file
  - Automatic networking
```

**Production:**
```
Kubernetes (Multi-host)
  - 1000s of containers
  - Auto-healing
  - Rolling updates
  - Self-healing
```

### Docker Compose Networking

```yaml
services:
  backend:
    networks:
      - riskguard-network

  postgres:
    networks:
      - riskguard-network

networks:
  riskguard-network:
    driver: bridge
```

Result:
- `backend` can reach `postgres:5432`
- Automatic DNS resolution
- Network isolation (containers can't reach outside)

---

## 6. Monitoring & Observability

### Three Pillars of Observability

#### 1. **Metrics** (Numbers)
```
http_requests_total: 10,500
http_request_duration: [0.1s, 0.05s, 0.15s]
database_connections: 48/50
```

#### 2. **Logs** (Events)
```
2024-03-15 10:30:45 INFO Backend started
2024-03-15 10:31:02 ERROR Database connection timeout
2024-03-15 10:32:15 INFO Risk assessment created
```

#### 3. **Traces** (Request flow)
```
Request from Browser
  → Frontend (10ms)
  → Nginx (2ms)
  → Backend API (150ms)
    → Database Query (30ms)
    → Risk Calculation (120ms)
Total: 162ms
```

### Prometheus Scraping

```
Every 15 seconds:
┌──────────────┐
│ Prometheus   │
└──────┬───────┘
       │
       ↓ Scrapes
┌──────────────┐
│ Backend API  │
│ /metrics     │
└──────────────┘

# Sample Output
http_requests_total{method="GET",status="200"} 1234
http_request_duration_seconds_bucket{le="0.5"} 45
```

### Grafana Alerting

```
Metric Threshold → Alert Triggered → Notification
┌──────────────────┐
│ Error Rate > 5%  │
└────────┬─────────┘
         ↓
    Alert Triggered
         ↓
    Slack Message
    PagerDuty Incident
    Email Notification
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "checks": {
            "database": await check_db(),
            "cache": await check_cache(),
            "disk_space": check_disk()
        }
    }
```

Load balancer uses this to route traffic only to healthy instances.

---

## 7. Scalability Patterns

### Horizontal Scaling (Scale Out)

```
Single Instance:
┌──────────────┐
│   Backend    │
│   (CPU=80%)  │
└──────────────┘

Scale Horizontally:
┌──────────────┐
│   Backend 1  │
│   (CPU=40%)  │
├──────────────┤
│   Backend 2  │
│   (CPU=40%)  │
├──────────────┤
│   Backend 3  │
│   (CPU=40%)  │
└──────────────┘
     ↑ ALB distributes traffic
```

### Vertical Scaling (Scale Up)

```
Upgrade instance type:
t3.micro (1 CPU, 512 MB) → t3.large (2 CPU, 8 GB)
```

### Auto-Scaling (AWS)

```hcl
resource "aws_autoscaling_group" "backend" {
  min_size         = 2
  max_size         = 10
  desired_capacity = 3
  
  health_check_type = "ELB"
  health_check_grace_period = 300
}

resource "aws_autoscaling_policy" "scale_up" {
  adjustment_type       = "ChangeInCapacity"
  adjustment_magnitude  = 1
  metric_aggregation_type = "Average"
}
```

Scales based on:
- CPU utilization > 70% → Add instance
- CPU utilization < 30% → Remove instance

### Caching Strategy

```
Request Flow:
User Request
    ↓
Check Cache
    ├─ HIT  → Return cached data (10ms)
    └─ MISS → Query DB (100ms) → Cache → Return
```

---

## 8. Blue-Green Deployment

### Zero-Downtime Updates

```
CURRENT STATE:
┌─────────────────────────────┐
│     Production (Blue)       │
│                             │
│  ┌──────────────────────┐   │
│  │ Version 1.2          │   │
│  │ 100% Traffic         │   │
│  └──────────────────────┘   │
└─────────────────────────────┘


DEPLOYMENT STATE:
┌──────────────────────────────────────┐
│  Blue (1.2)          Green (1.3)     │
│  ┌─────────────────┐  ┌─────────────┐│
│  │Version 1.2      │  │ Version 1.3 ││
│  │50% Traffic      │  │ 50% Traffic ││
│  └─────────────────┘  └─────────────┘│
│  Testing...          Testing...      │
└──────────────────────────────────────┘


FINAL STATE:
┌─────────────────────────────┐
│     Production (Green)      │
│                             │
│  ┌──────────────────────┐   │
│  │ Version 1.3          │   │
│  │ 100% Traffic         │   │
│  │ Blue ready to rollback   │
│  └──────────────────────┘   │
└─────────────────────────────┘
```

### Advantages

- ✅ **Zero Downtime**: Instant switch
- ✅ **Easy Rollback**: Keep old version running
- ✅ **Testing**: Full QA on green before switch
- ✅ **A/B Testing**: Can keep both versions active

### Implementation

```bash
# Deploy to green environment
terraform apply -var="environment=green"

# Run smoke tests
pytest tests/smoke/ --target green.riskguard.com

# Switch ALB to green
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:aws:...:targetgroup/green

# Keep blue as instant rollback
# If issues detected, switch back to blue
```

---

## 9. Security Best Practices

### Authentication Flow

```
User Credentials
    ↓
POST /auth/login
    ↓
Bcrypt Password Verification
    ↓
Generate JWT Token (expires in 30 min)
    ↓
Return access_token
    ↓
client stores token
    ↓
Authorization: Bearer {token}
```

### Secret Management

```
NEVER commit secrets:
❌ password = "admin123"
❌ api_key = "sk_live_abc123"

USE environment variables:
✅ password = os.getenv("DB_PASSWORD")
✅ api_key = os.getenv("API_KEY")

AWS Secrets Manager:
✅ Encrypted secrets
✅ Rotation policies
✅ Audit logs
```

### Network Security

```
┌─────────────────────────────────────┐
│      AWS VPC (Private)              │
├─────────────────────────────────────┤
│                                     │
│  Public Subnet (ALB, NAT)           │
│  ├─ Port 80: HTTP                   │
│  ├─ Port 443: HTTPS                 │
│  └─ Only inbound: internet traffic  │
│                                     │
│  Private Subnet (Backend, RDS)      │
│  ├─ NO inbound from internet        │
│  ├─ Only accepts from public subnet │
│  └─ All requests through ALB        │
│                                     │
└─────────────────────────────────────┘
```

### HTTPS/TLS Encryption

```
Certificate Chain:
User's Browser
    ↓
Validates cert issued by trusted CA
    ↓
Establishes TLS handshake
    ↓
Encrypted connection (https://)
    ↓
Backend (Nginx terminates TLS)
    ↓
Internal traffic (HTTP) over private network
```

---

## 10. Disaster Recovery & Business Continuity

### RTO & RPO

```
RTO = Recovery Time Objective
How fast can we restore service?
Target: < 30 minutes

RPO = Recovery Point Objective
How much data can we lose?
Target: < 5 minutes
```

### Backup Strategy

```
Daily Automated Backups:
┌─ 7 day retention
├─ Cross-region replication
├─ Point-in-time recovery
└─ Regular restore tests

Backup Locations:
├─ Primary Region (us-east-1)
├─ Secondary Region (us-west-2)
└─ Archive (Glacier for 90+ days)
```

### Failover Process

```
Primary Region Failure
    ↓
(Automatic) Route 53 health checks fail
    ↓
(Automatic) Switch DNS to secondary region
    ↓
RDS Read Replica promotes to Primary
    ↓
ECS tasks start in secondary region
    ↓
Service restored (< 2 minutes)
    ↓
(Manual) Investigate primary region
    ↓
(Manual) Fix and restore
```

---

## 11. Cost Optimization

### Resource Optimization

```
DEVELOPMENT:
- t3.micro instances (burstable)
- Small RDS: db.t3.micro
- 7-day backup retention
- No redundancy
Cost: ~$50/month

PRODUCTION:
- t3.large instances (guaranteed capacity)
- Multi-AZ RDS: db.t3.large
- 30-day backup retention + cross-region
- Auto-scaling (min 2, max 10)
Cost: ~$500/month
```

### Reserved Instances

```bash
# On-Demand (pay per hour)
t3.large: $0.10/hour

# Reserved (commit 1-3 years)
1-year: $0.07/hour (30% discount)
3-year: $0.06/hour (40% discount)
```

---

## Summary Table

| Concept | Purpose | Tool/Tech | Benefit |
|---------|---------|-----------|---------|
| CI/CD | Auto test & deploy | GitHub Actions | Fast feedback,<br>reduced risk |
| Containerization | Isolation & consistency | Docker | Works everywhere,<br>lightweight |
| IaC | Manage infrastructure | Terraform | Version control,<br>reproducibility |
| Monitoring| Observe system health | Prometheus,<br>Grafana | Alerts,<br>visibility |
| Scaling | Handle load | Kubernetes,<br>ASG | Reliability,<br>cost-effective |
| Microservices | Separation of concerns | Docker +<br>API | Independent<br>deployment |
| Blue-Green | Zero-downtime updates | ALB | Instant<br>rollback |
| Security | Protect data | TLS, Secrets,<br>VPC | Compliance,<br>safety |

---

## Learning Path

1. **Start**: Docker & Docker Compose
2. **Then**: CI/CD basics (GitHub Actions)
3. **Next**: Infrastructure basics (Terraform)
4. **Advanced**: Kubernetes, advanced monitoring
5. **Expert**: Distributed systems, multi-region, FinOps

---

## References

- [Docker Documentation](https://docs.docker.com)
- [Terraform Registry](https://registry.terraform.io)
- [Kubernetes Basics](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes)
- [Prometheus Docs](https://prometheus.io/docs)
- [AWS Architecture Center](https://aws.amazon.com/architecture)

