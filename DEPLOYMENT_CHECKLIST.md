# RiskGuard AI - Deployment & Verification Checklist

## Pre-Deployment Verification

### Environment Setup
- [ ] Git repository created and initialized
- [ ] GitHub repository configured with push access
- [ ] All git branches created (main, develop, staging)
- [ ] .env files created from .env.example templates
- [ ] Sensitive values replaced in .env files
- [ ] .env files added to .gitignore (not committed)

### Local Development Verification
- [ ] Docker Desktop installed and running
- [ ] `docker --version` returns 20.10+
- [ ] `docker-compose --version` returns 2.0+
- [ ] Windows PowerShell or WSL2 configured (for Windows)
- [ ] Project directory structure verified (21 folders present)
- [ ] All source files present (50+ files, 0 missing)

### Backend Verification
- [ ] Backend directory structure: `backend/app/` has models, schemas, services, controllers
- [ ] `requirements.txt` contains all dependencies
- [ ] FastAPI imports work: `from fastapi import FastAPI`
- [ ] SQLAlchemy configured: `backend/app/database/connection.py` exists
- [ ] Models defined: `backend/app/models/models.py` has 4 classes
- [ ] Pydantic schemas exist: `backend/app/schemas/schemas.py` complete
- [ ] Main app file: `backend/app/main.py` properly configured
- [ ] Health check endpoint available at `/health`
- [ ] Metrics endpoint available at `/metrics`

### Frontend Verification
- [ ] Frontend directory structure: `frontend/src/` has components, pages, services, context
- [ ] `package.json` has React, Vite, Tailwind dependencies
- [ ] TypeScript configured: `tsconfig.json` exists with strict mode
- [ ] Vite config: `vite.config.ts` has API proxy configured
- [ ] Tailwind CSS: `tailwind.config.js` and `postcss.config.js` present
- [ ] API service: `src/services/api.ts` has all endpoint methods
- [ ] State store: `src/context/store.ts` has auth and projects stores
- [ ] Environment config: `.env.example` has REACT_APP_API_URL

### Database Verification
- [ ] PostgreSQL schema migration file exists: `backend/migrations/001_initial_schema.py`
- [ ] All 4 tables defined: users, projects, risk_assessments, url_scan_results
- [ ] Foreign key relationships configured
- [ ] Primary keys and indexes defined
- [ ] Database connection string format: `postgresql+asyncpg://user:pass@host/dbname`

### Docker Verification
- [ ] Dockerfile for backend: `docker/Dockerfile.backend` exists
- [ ] Dockerfile for frontend: `docker/Dockerfile.frontend` exists
- [ ] docker-compose.yml has 6 services defined
- [ ] Postgres service configured with correct environment
- [ ] Backend service depends on postgres_ready
- [ ] Frontend service depends on backend service
- [ ] Volume mounts configured for persistence
- [ ] Network bridge configured for service communication
- [ ] Health checks configured for each container

### CI/CD Verification
- [ ] GitHub Actions workflow file: `.github/workflows/deploy.yml` exists
- [ ] Workflow has 6 stages: Tests, Lint, Build, Push, Deploy Staging, Deploy Production
- [ ] Backend tests stage configured with pytest
- [ ] Frontend tests stage configured with npm
- [ ] Docker build stage configured with BuildX
- [ ] Staging deployment trigger: develop branch
- [ ] Production deployment trigger: main branch
- [ ] GitHub secrets configured: DOCKER_USERNAME, DOCKER_PASSWORD, RENDER_API_KEY

### Infrastructure Verification
- [ ] Terraform directory: `infrastructure/terraform/` exists
- [ ] Main config file: `main.tf` has 30+ AWS resources
- [ ] Variables file: `variables.tf` defines all parameters
- [ ] Outputs configured for ALB, RDS, ECS endpoints
- [ ] VPC CIDR block: 10.0.0.0/16
- [ ] Public subnets in 2 AZs (10.0.1.0/24, 10.0.2.0/24)
- [ ] Private subnets in 2 AZs (10.0.10.0/24, 10.0.11.0/24)
- [ ] Security groups defined: ALB, ECS, RDS
- [ ] RDS PostgreSQL configuration (db.t3.micro/small)
- [ ] ALB with health checks on /health endpoint
- [ ] ECS cluster foundation ready

### Monitoring Verification
- [ ] Prometheus config: `monitoring/prometheus.yml` exists
- [ ] Alert rules file: `monitoring/alert_rules.yml` has 4 alerts
- [ ] Grafana datasource: `monitoring/grafana_datasources.yml` configured
- [ ] Scrape configs include: api, postgres, nginx, prometheus
- [ ] Alert rules cover: error rate, latency, database, memory
- [ ] Service ports configured: Prometheus 9090, Grafana 3001

### Documentation Verification
- [ ] README.md exists (4,000+ words)
- [ ] API_DOCUMENTATION.md exists (2,500+ words)
- [ ] DATABASE_SCHEMA.md exists with ER diagram
- [ ] DEPLOYMENT_GUIDE.md exists (3,500+ words)
- [ ] DEVOPS_CONCEPTS.md exists (5,000+ words)
- [ ] QUICKSTART.md exists with quick start instructions
- [ ] All docs use proper markdown formatting
- [ ] Code examples are executable
- [ ] Links are correct (no 404s)

---

## Phase 1: Local Development (5-10 minutes)

### Step 1: Start Docker Services
```bash
cd c:\projrct\ risk\ predction
docker-compose up -d
```

- [ ] Command completes without errors
- [ ] 6 containers running: postgres, backend_api, frontend_ui, nginx, prometheus, grafana
- [ ] Verify with: `docker-compose ps`

### Step 2: Verify Database
```bash
docker-compose logs postgres
```

- [ ] "ready to accept connections" message appears
- [ ] Database initialized successfully
- [ ] No connection errors in logs

### Step 3: Verify Backend
```bash
docker-compose logs backend_api
```

- [ ] FastAPI application started
- [ ] "Application startup complete" message
- [ ] No Python errors

### Step 4: Verify Frontend
```bash
docker-compose logs frontend_ui
```

- [ ] Nginx server starts successfully
- [ ] No errors in logs

### Step 5: Test Health Endpoints
```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

- [ ] Health endpoint returns 200 OK with status
- [ ] Metrics endpoint returns Prometheus format text

### Step 6: Verify API Access
```bash
curl http://localhost:3000
```

- [ ] Frontend loads (HTML response)
- [ ] No connection refused errors

### Step 7: Check Monitoring
```
http://localhost:9090        # Prometheus
http://localhost:3001        # Grafana (admin/admin)
```

- [ ] Prometheus targets all up
- [ ] Grafana dashboard loads
- [ ] Data sources connected

### Step 8: Cleanup
```bash
docker-compose down  # if testing only
docker-compose down -v  # if reset needed
```

---

## Phase 2: Integration Testing (10-15 minutes)

### Authentication Flow Test

#### Step 1: Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'
```

- [ ] Returns 200 OK
- [ ] Response includes user_id, email, username
- [ ] Password not returned in response

#### Step 2: Login User
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

- [ ] Returns 200 OK
- [ ] Response includes access_token
- [ ] Token type is "bearer"
- [ ] Token is JWT (3 parts separated by dots)

#### Step 3: Save Token
```powershell
$TOKEN="your_token_here"
echo $TOKEN  # Verify token is saved
```

- [ ] Token saved in variable
- [ ] Can echo token without error

### Project Management Test

#### Step 4: Create Project
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "project_type": "Software",
    "duration_months": 12,
    "expected_budget": 100000,
    "team_size": 5,
    "tech_stack": "React + FastAPI"
  }'
```

- [ ] Returns 201 Created
- [ ] Response includes project_id
- [ ] All fields returned correctly

#### Step 5: List Projects
```bash
curl -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN"
```

- [ ] Returns 200 OK
- [ ] Response is array of projects
- [ ] Created project appears in list

#### Step 6: Get Project Detail
```bash
curl -X GET http://localhost:8000/api/v1/projects/1 \
  -H "Authorization: Bearer $TOKEN"
```

- [ ] Returns 200 OK
- [ ] Correct project ID returned
- [ ] All project fields present

#### Step 7: Update Project
```bash
curl -X PUT http://localhost:8000/api/v1/projects/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Project Name",
    "status": "Active"
  }'
```

- [ ] Returns 200 OK
- [ ] Updated fields reflected in response

### Risk Assessment Test

#### Step 8: Manual Risk Assessment
```bash
curl -X POST http://localhost:8000/api/v1/risk/manual \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "schedule_pressure_5": 4,
    "completion_rate_pct": 75,
    "delay_days": 10,
    "budget_variance_pct": -5,
    "resource_availability_4": 3,
    "complexity_5": 3,
    "innovation_toggle": false,
    "external_risk_toggle": false,
    "contract_type": "Fixed Price",
    "stakeholder_coordination_4": 3,
    "change_frequency_4": 2
  }'
```

- [ ] Returns 200 OK
- [ ] Response includes assessment_id
- [ ] Includes probability (0-100)
- [ ] Includes risk_level (Low/Medium/High)
- [ ] Includes impact breakdown
- [ ] Includes recommendations

#### Step 9: URL Scan Analysis
```bash
curl -X POST http://localhost:8000/api/v1/risk/url-scan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "url": "https://github.com/torvalds/linux"
  }'
```

- [ ] Returns 200 OK
- [ ] URL analysis results returned
- [ ] Includes maturity_stage
- [ ] Includes documentation_quality
- [ ] Includes update_frequency
- [ ] Includes code_complexity
- [ ] Includes calculated_risk score

### Analytics Test

#### Step 10: Portfolio Summary
```bash
curl -X GET http://localhost:8000/api/v1/analytics/summary \
  -H "Authorization: Bearer $TOKEN"
```

- [ ] Returns 200 OK
- [ ] Includes total_projects count
- [ ] Includes average_risk
- [ ] Includes portfolio breakdown

#### Step 11: Risk Trends
```bash
curl -X GET http://localhost:8000/api/v1/analytics/trends \
  -H "Authorization: Bearer $TOKEN"
```

- [ ] Returns 200 OK
- [ ] Includes time-series data
- [ ] Shows trend over time

#### Step 12: Factor Analysis
```bash
curl -X GET http://localhost:8000/api/v1/analytics/factors \
  -H "Authorization: Bearer $TOKEN"
```

- [ ] Returns 200 OK
- [ ] Lists risk factors and weights
- [ ] Shows factor impact analysis

### Error Handling Test

#### Step 13: Test Invalid Token
```bash
curl -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer invalid_token"
```

- [ ] Returns 401 Unauthorized
- [ ] Error message indicates invalid token

#### Step 14: Test Missing Token
```bash
curl -X GET http://localhost:8000/api/v1/projects
```

- [ ] Returns 403 Forbidden or 401 Unauthorized
- [ ] Error message indicates missing credentials

#### Step 15: Test Invalid Request
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Missing required fields"
  }'
```

- [ ] Returns 422 Unprocessable Entity
- [ ] Error details validation errors

---

## Phase 3: Docker Compose Verification (5 minutes)

### Service Health Checks
```bash
docker-compose ps
```

- [ ] All 6 services showing as "Up"
- [ ] No services in "Exited" state
- [ ] Health checks showing "healthy"

### Log Review
```bash
docker-compose logs --tail=50 backend_api
docker-compose logs --tail=50 postgres
docker-compose logs --tail=50 frontend_ui
```

- [ ] No ERROR level logs in backend
- [ ] No "Connection refused" errors
- [ ] No database connection errors
- [ ] No JavaScript/build errors in frontend

### Database Verification
```bash
docker-compose exec postgres psql -U riskguard_user -d riskguard \
  -c "SELECT table_name FROM information_schema.tables 
      WHERE table_schema = 'public';"
```

- [ ] Returns 4 tables: users, projects, risk_assessments, url_scan_results
- [ ] No error "could not connect to server"

### Container Logs Cleanup
```bash
docker-compose logs -f  # View live logs
# Press Ctrl+C to stop following logs
```

- [ ] Can view logs without errors
- [ ] Can attach and detach without issues

---

## Phase 4: Staging Deployment (15-20 minutes)

### Prerequisites
- [ ] GitHub account created
- [ ] Repository pushed to GitHub
- [ ] Render.com account created
- [ ] Docker Hub account created (for image registry)

### GitHub Setup
```bash
git init
git add .
git commit -m "Initial commit: RiskGuard production setup"
git branch -M main
git remote add origin https://github.com/yourname/riskguard.git
git push -u origin main
```

- [ ] All files committed
- [ ] Repository visible on GitHub
- [ ] Main branch contains all code

### GitHub Actions Configuration
```bash
# Add secrets to GitHub:
# DOCKER_USERNAME = your docker hub username
# DOCKER_PASSWORD = your docker hub token
# RENDER_API_KEY = your render API key
```

- [ ] Navigate to Settings → Secrets and variables → Actions
- [ ] Add DOCKER_USERNAME
- [ ] Add DOCKER_PASSWORD
- [ ] Add RENDER_API_KEY

### Docker Hub Preparation
```bash
# Create repository: riskguard-backend
# Create repository: riskguard-frontend
# Generate access token for authentication
```

- [ ] Both repositories created on Docker Hub
- [ ] Access token generated
- [ ] Token value saved for GitHub secrets

### Render.com Deployment
```
1. Create Web Service
2. Connect GitHub repository
3. Select develop branch
4. Configure environment variables:
   - DATABASE_URL
   - SECRET_KEY
   - ENVIRONMENT=staging
5. Deploy
```

- [ ] Web service created
- [ ] Build log shows successful build
- [ ] Application URL reachable
- [ ] Health check endpoint returns 200

### Staging Verification
```bash
curl https://your-staging-app.onrender.com/health
curl https://your-staging-app.onrender.com/api/v1/auth/register
```

- [ ] Health endpoint accessible
- [ ] API endpoints accessible
- [ ] No CORS errors in frontend
- [ ] Database connected successfully

### Staging Monitoring
```
Open: https://your-staging-app.onrender.com/metrics
```

- [ ] Prometheus metrics accessible
- [ ] Metrics showing request counts
- [ ] No 404 errors in metrics

---

## Phase 5: Production Deployment (AWS) (30-40 minutes)

### AWS Preparation
- [ ] AWS account created
- [ ] AWS CLI installed: `aws --version`
- [ ] AWS credentials configured: `aws configure`
- [ ] Terraform installed: `terraform --version` (1.0+)

### Terraform Setup
```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan -var-file="prod.tfvars"

# Review output and approve
terraform apply -var-file="prod.tfvars"
```

- [ ] terraform init completes without errors
- [ ] terraform validate returns no errors
- [ ] terraform plan shows resources to create
- [ ] terraform apply completes successfully
- [ ] Outputs show ALB_DNS_NAME and RDS_ENDPOINT

### AWS Resource Verification
```bash
# Verify VPC created
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=riskguard-vpc"

# Verify RDS
aws rds describe-db-instances --db-instance-identifier riskguard-db

# Verify ALB
aws elbv2 describe-load-balancers --names riskguard-alb
```

- [ ] VPC exists with correct CIDR
- [ ] RDS instance in creating/available state
- [ ] ALB created with health checks

### Build and Push Docker Images
```bash
# Backend
docker build -f docker/Dockerfile.backend \
  -t yourregistry/riskguard-backend:latest .
docker push yourregistry/riskguard-backend:latest

# Frontend  
docker build -f docker/Dockerfile.frontend \
  -t yourregistry/riskguard-frontend:latest .
docker push yourregistry/riskguard-frontend:latest
```

- [ ] Both images build without errors
- [ ] Images pushed to registry successfully
- [ ] Image sizes reasonable (<200MB each)

### Database Migration
```bash
# Run migrations on production database
python backend/migrations/001_initial_schema.py
```

- [ ] Tables created successfully
- [ ] No "already exists" errors (migration idempotent)
- [ ] Schema matches design

### Health Check
```bash
curl http://ALB_DNS_NAME/health
```

- [ ] Returns 200 OK
- [ ] Response includes {"status": "healthy"}

### Production Access
```
Application: http://ALB_DNS_NAME
API Docs: http://ALB_DNS_NAME/api/docs
```

- [ ] Frontend loads
- [ ] API endpoints accessible
- [ ] Database connected
- [ ] Metrics available

---

## Phase 6: Monitoring Setup (10-15 minutes)

### Prometheus Configuration
```bash
# If using Docker Compose:
docker-compose exec prometheus curl http://localhost:9090/api/v1/targets
```

- [ ] All targets showing as "UP"
- [ ] Scrape intervals < 15 seconds
- [ ] No errors in scrape logs

### Grafana Dashboards
```
1. Open http://localhost:3001 (or production Grafana)
2. Login: admin / admin
3. Add Prometheus datasource
4. Import dashboards or create new ones
```

- [ ] Prometheus datasource shows "healthy"
- [ ] Can query metrics: `up` should return 1s
- [ ] Dashboards display correctly

### Alert Rules Verification
```bash
# Check alert status
curl http://localhost:9090/api/v1/alerts
```

- [ ] All 4 alert rules loaded
- [ ] Alerts in "Pending" or "Firing" state
- [ ] No "Invalid" alerts

### Log Forwarding (Optional)
```bash
# For production, configure:
# CloudWatch, ELK, Datadog, or New Relic
```

- [ ] Logs collected centrally
- [ ] Can search logs by service
- [ ] Error tracking enabled

---

## Phase 7: Smoke Testing (5-10 minutes)

### Critical Path Testing

Test the most important user flows:

```bash
# 1. Registration
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke@test.com","username":"smoketest","password":"Smoke123!","full_name":"Smoke Test"}'

# 2. Get Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke@test.com","password":"Smoke123!"}' | jq -r '.access_token')

# 3. Create Project
PROJECT_ID=$(curl -s -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Smoke Test","project_type":"Software","duration_months":6,"expected_budget":50000}' | jq -r '.id')

# 4. Risk Assessment
curl -s -X POST http://localhost:8000/api/v1/risk/manual \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"project_id\":$PROJECT_ID,\"schedule_pressure_5\":3,\"completion_rate_pct\":80,\"delay_days\":5,\"budget_variance_pct\":0,\"resource_availability_4\":3,\"complexity_5\":2,\"innovation_toggle\":false,\"external_risk_toggle\":false,\"contract_type\":\"Fixed Price\",\"stakeholder_coordination_4\":3,\"change_frequency_4\":2}" | jq '.'

# 5. View Analytics
curl -s -X GET http://localhost:8000/api/v1/analytics/summary \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

Verification:
- [ ] All requests return 200/201 responses
- [ ] No 500 errors
- [ ] All data persists across calls
- [ ] Response times < 500ms

### Frontend Test
```
1. Navigate to http://localhost:3000
2. Register with test account
3. Login
4. Create project
5. Perform risk assessment
6. View analytics
```

- [ ] Pages load without errors
- [ ] Forms submit successfully
- [ ] Data appears in tables/charts
- [ ] No JavaScript console errors

---

## Phase 8: Performance Testing (Optional, 15-20 minutes)

### Load Testing Setup
```bash
# Install Apache Bench (comes with Apache)
# Or install hey: go get -u github.com/rakyll/hey
```

### API Load Test
```bash
# 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:8000/health

# Or with hey
hey -n 100 -c 10 http://localhost:8000/health
```

Expected results:
- [ ] Response times P95 < 200ms
- [ ] No failed requests
- [ ] Requests/sec > 50

### Database Query Performance
```bash
# Monitor slow queries
docker-compose exec postgres \
  psql -U riskguard_user -d riskguard \
  -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

- [ ] Most queries < 50ms
- [ ] No timeouts
- [ ] Connection pool not exhausted

---

## Post-Deployment Checklist

### Security Verification
- [ ] HTTPS/TLS enabled on ALB
- [ ] SSL certificate valid (not self-signed in production)
- [ ] Security headers present (X-Frame-Options, CSP, etc.)
- [ ] Database password changed from default
- [ ] Secret key rotated and strong (>32 characters)
- [ ] All default credentials removed
- [ ] API rate limiting configured
- [ ] CORS allows only expected origins

### Backup & Recovery
- [ ] RDS automated backups enabled (7 days)
- [ ] Backup retention policy documented
- [ ] Tested restore from backup
- [ ] Disaster recovery plan written
- [ ] RTO: Recovery Time Objective defined
- [ ] RPO: Recovery Point Objective defined

### Monitoring & Alerting
- [ ] Alerts configured for critical issues
- [ ] Alert channels active (Slack, email, PagerDuty)
- [ ] Dashboards created for KPIs
- [ ] Log aggregation working
- [ ] Regular log review schedule set

### Documentation
- [ ] Runbook created for common issues
- [ ] Team trained on deployment process
- [ ] Incident response plan documented
- [ ] Change management process defined
- [ ] Access control documented

### Scaling Preparation
- [ ] Auto-scaling policies tested
- [ ] Load test scenarios documented
- [ ] Scaling thresholds configured
- [ ] Cost projections calculated
- [ ] Reserved instance purchase considered

---

## Troubleshooting Guide

### Common Issues & Solutions

#### Issue: "docker-compose: command not found"
**Solution**: 
```bash
# Upgrade Docker Desktop
# Or install Docker Compose separately
pip install docker-compose
```

#### Issue: "Database connection refused"
**Solution**:
```bash
# Wait for postgres to be ready
docker-compose logs postgres
# Look for "ready to accept connections"

# Restart services
docker-compose down
docker-compose up -d --build
```

#### Issue: "Port 5432 already in use"
**Solution**:
```bash
# Find process using port
netstat -ano | findstr :5432

# Kill process or change docker-compose port
# Edit docker-compose.yml:
#   postgres:
#     ports:
#       - "5433:5432"  # Use 5433 instead
```

#### Issue: "CORS error in frontend"
**Solution**:
Check backend CORS settings:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Issue: "API returns 401 Unauthorized"
**Solution**:
```bash
# Verify token is valid
# Check Authorization header format: "Bearer TOKEN"
# Verify SECRET_KEY matches in backend

# Debug:
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/projects
```

#### Issue: "Terraform apply fails"
**Solution**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Validate configuration
terraform validate

# Check resource state
terraform state list

# Destroy and retry
terraform destroy
terraform apply -var-file="prod.tfvars"
```

---

## Final Verification Checklist

Before marking as "Production Ready":

- [ ] All 6 Docker services starting successfully
- [ ] All API endpoints tested and working
- [ ] Database migrations completed
- [ ] Frontend loads without errors
- [ ] Authentication flow working (register → login → authenticated requests)
- [ ] Risk assessment engine producing results
- [ ] Analytics endpoints returning data
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards displaying data
- [ ] Health checks passing (all services)
- [ ] CI/CD pipeline triggered on commit
- [ ] Staging deployment working
- [ ] Production infrastructure deployed
- [ ] SSL/TLS certificates installed
- [ ] Backups configured
- [ ] Monitoring alerts active
- [ ] Logs being collected
- [ ] Documentation complete and accessible
- [ ] Team trained on deployment and operations
- [ ] Incident response plan ready

**Status: Ready for production deployment ✅**

---

## Success Metrics

After deployment, track these metrics:

| Metric | Target | Actual |
|--------|--------|--------|
| Application Uptime | 99.95% | _____ |
| API Response Time (p95) | < 200ms | _____ |
| Error Rate | < 0.1% | _____ |
| Database Query Time | < 50ms | _____ |
| Page Load Time | < 3s | _____ |
| User Registration Success | 99% | _____ |
| Assessment Calculation Speed | < 100ms | _____ |
| Metrics Collection Uptime | 99% | _____ |

---

**Congratulations! Your RiskGuard deployment is complete! 🎉**
