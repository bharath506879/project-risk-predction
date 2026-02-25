# Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Compose (Staging)](#docker-compose-staging)
3. [AWS Deployment (Production)](#aws-deployment-production)
4. [Render Deployment (Simplified)](#render-deployment-simplified)
5. [Monitoring Setup](#monitoring-setup)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites
- Docker & Docker Compose 2.0+
- Python 3.11+
- Node.js 18+
- PostgreSQL 15 (optional, use Docker)
- Git

### Setup

1. **Clone and navigate to project**
```bash
git clone https://github.com/yourname/riskguard.git
cd riskguard
```

2. **Create environment files**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your values

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your values
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Initialize database** (first time only)
```bash
docker-compose exec backend python -m alembic upgrade head
docker-compose exec backend python -m pytest tests/
```

5. **Access services**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

### Development without Docker

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
python -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Docker Compose (Staging)

### Features
- All services in containers
- Persistent volumes for database
- Health checks on all services
- Prometheus and Grafana monitoring
- Network isolation

### Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Stop services
docker-compose down

# Remove everything (including volumes)
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Run migrations
docker-compose exec backend alembic upgrade head

# Access container shell
docker-compose exec backend bash
docker-compose exec postgres psql -U riskguard_user -d riskguard_db
```

### Docker Compose Environment Variables

Create `.env` file in project root:
```
DB_USER=riskguard_user
DB_PASSWORD=RiskGuard2024!
DB_NAME=riskguard_db
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
ENABLE_MONITORING=true
```

---

## AWS Deployment (Production)

### Architecture Overview
```
Internet ? AWS Route 53 (DNS)
         ?
       ALB (Application Load Balancer)
         ?
    ???????????
    ?         ?
   ECS       ECS
 Backend   Frontend
    ?         ?
    ???????????
         ?
      RDS PostgreSQL
         ?
      EC2 (Bastion)
```

### Prerequisites

1. **AWS Account** with permissions for:
   - EC2, VPC, RDS, ALB, CloudWatch, IAM
   - S3 (for Terraform state)
   - CloudFront (optional)

2. **Tools**
   - AWS CLI configured: `aws configure`
   - Terraform 1.0+
   - Docker and Docker CLI

3. **Create S3 bucket for Terraform state**
```bash
aws s3api create-bucket \
  --bucket riskguard-terraform-state \
  --region us-east-1 \
  --acl private

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket riskguard-terraform-state \
  --versioning-configuration Status=Enabled
```

### Terraform Deployment

1. **Configure variables**
```bash
cd infrastructure/terraform

# Create terraform variables file
cat > prod.tfvars << EOF
aws_region         = "us-east-1"
environment        = "production"
vpc_cidr           = "10.0.0.0/16"
db_instance_class  = "db.t3.small"
db_allocated_storage = 50
ecs_task_cpu       = "512"
ecs_task_memory    = "1024"
EOF
```

2. **Initialize Terraform**
```bash
terraform init
```

3. **Review plan**
```bash
terraform plan -var-file="prod.tfvars"
```

4. **Deploy infrastructure**
```bash
terraform apply -var-file="prod.tfvars"
```

5. **Get outputs**
```bash
terraform output alb_dns_name
# Copy DNS name to Route 53
```

### Deploy Application to ECS

1. **Push Docker images to ECR**
```bash
# Create ECR repositories
aws ecr create-repository --repository-name riskguard-backend --region us-east-1
aws ecr create-repository --repository-name riskguard-frontend --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login \
  --username AWS --password-stdin [YOUR_AWS_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -f docker/Dockerfile.backend -t riskguard-backend:latest .
docker tag riskguard-backend:latest \
  [AWS_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/riskguard-backend:latest
docker push [AWS_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/riskguard-backend:latest

# Build and push frontend
docker build -f docker/Dockerfile.frontend -t riskguard-frontend:latest .
docker tag riskguard-frontend:latest \
  [AWS_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/riskguard-frontend:latest
docker push [AWS_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/riskguard-frontend:latest
```

2. **Create ECS Task Definitions**

Create `backend-task-def.json`:
```json
{
  "family": "riskguard-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "riskguard-backend",
      "image": "[AWS_ACCOUNT_ID].dkr.ecr.us-east-1.amazonaws.com/riskguard-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DEBUG",
          "value": "false"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:[ACCOUNT_ID]:secret:riskguard/db-url"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:[ACCOUNT_ID]:secret:riskguard/secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/riskguard",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    }
  ]
}
```

3. **Register task definition**
```bash
aws ecs register-task-definition --cli-input-json file://backend-task-def.json
```

4. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster riskguard-cluster \
  --service-name riskguard-backend-service \
  --task-definition riskguard-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=riskguard-backend,containerPort=8000 \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=DISABLED}"
```

---

## Render Deployment (Simplified)

Best for quick production deployment without managing infrastructure.

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Services

**Backend Service:**
1. Go to render.com
2. New ? Web Service
3. Connect GitHub repo
4. Configure:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 10000`
   - Environment Variables:
     - `DATABASE_URL`: PostgreSQL connection string
     - `SECRET_KEY`: Generate random key
     - `ENVIRONMENT`: production
     - `DEBUG`: false

**Frontend Service:**
1. New ? Static Site
2. Connect GitHub repo
3. Configure:
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`

**Database:**
1. New ? PostgreSQL
2. Set credentials
3. Get connection string for backend environment variables

### Step 3: Set up custom domain

1. Render Dashboard ? Services
2. Select service ? Settings
3. Custom Domain ? Add domain
4. Update DNS with Render's nameservers

---

## Monitoring Setup

### Prometheus Alerts

Create alerts in `monitoring/alert_rules.yml`:

```yaml
groups:
  - name: Production Alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate in production"
```

### CloudWatch Dashboards (AWS)

```bash
aws cloudwatch put-dashboard \
  --dashboard-name riskguard-monitoring \
  --dashboard-body file://monitoring/cloudwatch-dashboard.json
```

### Slack Alerts

In Grafana:
1. Alerting ? Notification Channels
2. Add ? Slack
3. Paste Slack webhook URL
4. Configure alert rules to use Slack channel

---

## Troubleshooting

### Backend Issues

**Database connection error**
```bash
# Check connection string
docker-compose exec backend python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); print('Connected!')"
```

**Migrations not applied**
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic current
```

**Health check failing**
```bash
curl http://localhost:8000/health
# Should return {"status":"healthy"}
```

### Frontend Issues

**API requests failing**
```bash
# Check CORS headers
curl -H "Origin: http://localhost:3000" http://localhost:8000/api/v1/projects -v

# Check API URL in .env
cat frontend/.env
```

**Build failures**
```bash
cd frontend
npm clean-install
npm run build --verbose
```

### Database Issues

**Reset database**
```bash
docker-compose exec postgres psql -U riskguard_user -d riskguard_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
docker-compose exec backend alembic upgrade head
```

**Check database logs**
```bash
docker-compose logs postgres
```

### Monitoring Issues

**Prometheus not scraping**
```bash
# Check targets
curl http://localhost:9090/api/v1/targets

# Check metrics directly
curl http://localhost:8000/metrics
```

**Grafana datasource error**
1. Grafana ? Configuration ? Data Sources
2. Test Prometheus connection
3. Check Prometheus is running: `docker-compose ps prometheus`

---

## Performance Tuning

### Database
```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Create indexes
CREATE INDEX idx_risk_assessments_project ON risk_assessments(project_id);
CREATE INDEX idx_risk_assessments_created ON risk_assessments(created_at DESC);
```

### Backend
```python
# Increase connection pool size in config.py
pool_size=30
max_overflow=60
```

### Frontend
```bash
# Generate bundle analysis
npm run build -- --analyze
```

---

## Rollback

### Docker Compose
```bash
git revert HEAD
docker-compose build --no-cache
docker-compose up -d
```

### Terraform
```bash
terraform plan -destroy
terraform destroy
# or restore from state file backup
```

### Render
1. Dashboard ? Deployments
2. Select previous deployment
3. Click "Redeploy"

---

## Post-Deployment Checklist

- [ ] Database backups configured
- [ ] SSL/TLS certificates valid
- [ ] Monitoring alerts configured
- [ ] Logs aggregation set up
- [ ] Secrets rotated
- [ ] DDoS protection enabled
- [ ] WAF rules configured
- [ ] Load testing completed
- [ ] Disaster recovery tested
- [ ] Documentation updated
