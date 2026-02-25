# RiskGuard AI - Quick Start & Project Summary

## 📊 Project Overview

**RiskGuard AI** is a production-grade **full-stack risk assessment and predictive analytics platform** demonstrating enterprise DevOps architecture.

### Key Statistics
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Infrastructure**: Docker + Terraform + AWS
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Code**: ~5,000 lines (backend) + ~2,000 lines (frontend) + configs
- **Documentation**: 50+ pages of comprehensive guides

### Architecture Highlights
```
React Frontend (Port 3000)
         ↓
    Nginx Proxy (Port 80)
         ↓
   FastAPI Backend (Port 8000)
         ↓
   PostgreSQL (Port 5432)
         ↓
Prometheus/Grafana Monitoring (Ports 9090, 3001)
```

---

## 🚀 5-Minute Quick Start

### Prerequisites
```bash
#Check versions
docker --version    # 20.10+
docker-compose --version  # 2.0+
git --version       # 2.30+
```

### Step 1: Clone Project
```bash
git clone https://github.com/yourname/riskguard.git
cd riskguard
```

### Step 2: Start Services
```bash
docker-compose up -d
```

### Step 3: Access Application
```
Application:  http://localhost:3000
API Docs:     http://localhost:8000/api/docs
Prometheus:   http://localhost:9090
Grafana:      http://localhost:3001 (admin/admin)
```

### Step 4: Create Test Account
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Copy the access_token from response
```

### Step 5: Test API
```bash
# Create project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "project_type": "Software",
    "duration_months": 12,
    "expected_budget": 100000
  }'

# Get projects
curl -X GET http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📁 Project Structure Summary

```
riskguard/
│
├── .github/workflows/          ← GitHub Actions CI/CD
│   └── deploy.yml              
│
├── backend/                    ← FastAPI Application
│   ├── app/
│   │   ├── controllers/        ← HTTP endpoints
│   │   ├── services/           ← Business logic
│   │   ├── models/             ← SQLAlchemy ORM
│   │   ├── schemas/            ← Pydantic validation
│   │   ├── database/           ← DB connection
│   │   └── main.py             ← FastAPI app entry
│   ├── migrations/             ← Alembic DB migrations
│   ├── tests/                  ← Unit tests
│   ├── requirements.txt        ← Python dependencies
│   └── .env.example            
│
├── frontend/                   ← React Application
│   ├── src/
│   │   ├── components/         ← React components
│   │   ├── pages/              ← Page layouts
│   │   ├── services/           ← API client
│   │   ├── context/            ← Zustand stores
│   │   └── main.tsx            ← Entry point
│   ├── package.json            
│   ├── vite.config.ts          
│   ├── tsconfig.json           
│   └── tailwind.config.js      
│
├── docker/                     ← Docker configurations
│   ├── Dockerfile.backend      
│   └── Dockerfile.frontend     
│
├── infrastructure/            ← Production resources
│   ├── terraform/              ← AWS IaC
│   │   ├── main.tf             ← VPC, RDS, ECS, ALB
│   │   └── variables.tf        
│   └── nginx/                  ← Reverse proxy
│       ├── nginx.conf          
│       └── default.conf        
│
├── monitoring/                ← Observability
│   ├── prometheus.yml          ← Metrics config
│   ├── alert_rules.yml         ← Alert rules
│   └── grafana_datasources.yml 
│
├── docs/                      ← Documentation
│   ├── README.md               ← Main guide
│   ├── API_DOCUMENTATION.md    ← API reference
│   ├── DATABASE_SCHEMA.md      ← DB design
│   ├── DEPLOYMENT_GUIDE.md     ← Deployment steps
│   └── DEVOPS_CONCEPTS.md      ← DevOps explained
│
├── docker-compose.yml         ← Local environment
└── .gitignore
```

---

## 🛠️ Technology Stack

### Frontend Layer
| Technology | Purpose |
|-----------|---------|
| React 18 | UI library |
| TypeScript | Type safety |
| Vite | Fast build tool |
| Tailwind CSS | Utility CSS |
| Zustand | State management |
| Axios | HTTP client |
| Chart.js | Data visualization |

### Backend Layer
| Technology | Purpose |
|-----------|---------|
| FastAPI | Web framework |
| SQLAlchemy | ORM |
| Pydantic | Data validation |
| Prometheus | Metrics |
| Uvicorn | ASGI server |

### Database Layer
| Technology | Purpose |
|-----------|---------|
| PostgreSQL | Relational DB |
| Alembic | Migrations |

### DevOps Layer
| Technology | Purpose |
|-----------|---------|
| Docker | Container engine |
| Docker Compose | Multi-container |
| Terraform | Infrastructure |
| GitHub Actions | CI/CD |
| Prometheus | Monitoring |
| Grafana | Dashboards |
| Nginx | Reverse proxy |

---

## 💾 Database Schema at a Glance

### Tables

**users** - User accounts
```
id | email | username | hashed_password | created_at
```

**projects** - Project portfolio
```
id | user_id | name | project_type | status | duration_months
```

**risk_assessments** - Risk analysis results
```
id | project_id | probability | risk_level | schedule_impact | cost_impact
```

**url_scan_results** - Repository analysis results
```
id | url | documentation_quality | maturity_stage | calculated_risk
```

### Relationships
```
User (1) → (Many) Projects
User (1) → (Many) RiskAssessments
Project (1) → (Many) RiskAssessments
Project (1) → (Many) URLScanResults
```

---

## 📡 API Endpoints Reference

### Authentication
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Get access token

### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List projects
- `GET /api/v1/projects/{id}` - Get project
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Risk Engine
- `POST /api/v1/risk/manual` - Manual risk calculation
- `POST /api/v1/risk/url-scan` - URL analysis

### Analytics
- `GET /api/v1/analytics/summary` - Portfolio summary
- `GET /api/v1/analytics/trends` - Risk trends
- `GET /api/v1/analytics/factors` - Factor analysis

### System
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

---

## 🔄 CI/CD Pipeline Flow

```
Developer Push
    ↓
Git Webhook
    ↓
GitHub Actions Triggered
    ├─ Backend Tests (pytest)
    ├─ Frontend Tests (npm test)
    ├─ Linting (flake8, eslint)
    └─ Build check
         ↓
All tests pass?
    ├─ YES → Build Docker images
    │        ↓
    │        Push to Docker Hub/ECR
    │        ↓
    │        Deploy to Staging (develop branch)
    │        OR
    │        Deploy to Production (main branch)
    │
    └─ NO → Block deployment, notify developer
```

---

## 🔐 Security Features

- ✅ **JWT Authentication** - Token-based access control
- ✅ **Password Hashing** - Bcrypt with salt
- ✅ **HTTPS/TLS** - Encrypted transport
- ✅ **CORS Headers** - Cross-origin protection
- ✅ **Input Validation** - Pydantic schemas
- ✅ **SQL Injection Prevention** - Parameterized queries
- ✅ **Security Headers** - X-Frame-Options, CSP, etc.
- ✅ **VPC Isolation** - Private database subnet
- ✅ **Secrets Management** - Environment variables + AWS Secrets Manager

---

## 📊 Monitoring Dashboard Example

### Key Metrics Tracked
- **Request Volume**: HTTP requests/sec
- **Response Latency**: p50, p95, p99 response times
- **Error Rate**: 4xx, 5xx errors
- **Database Performance**: Query latency, connection pool
- **System Resources**: CPU, memory, disk usage
- **Business Metrics**: Risk assessments/day, users active

### Alert Rules
- Error rate > 5% for 5 minutes
- Response latency p95 > 2 seconds
- Database unavailable > 1 minute
- Memory usage > 85%
- Disk space < 10%

---

## 🚢 Deployment Paths

### Option 1: Local Development (5 min)
```bash
docker-compose up -d
# Access on localhost
```

### Option 2: Docker Compose (Production-like, 10 min)
```bash
# Set environment variables
export DB_PASSWORD=YourSecurePassword
export SECRET_KEY=YourSecureKey

docker-compose -f docker-compose.yml up -d --build
```

### Option 3: Render.com (Zero config, 15 min)
```bash
# Push to GitHub main branch
git push origin main

# Create web service in Render
# Choose GitHub repo
# Deploy! (Auto-managed)
```

### Option 4: AWS with Terraform (30 min)
```bash
cd infrastructure/terraform

terraform init
terraform plan -var-file="prod.tfvars"
terraform apply -var-file="prod.tfvars"

# Push Docker images to ECR
# Create ECS services
# Done!
```

---

## 🔧 Common Commands

### Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Backend shell
docker-compose exec backend bash

# Database shell
docker-compose exec postgres psql -U riskguard_user
```

### Testing
```bash
# Backend tests
pytest backend/tests -v

# Frontend tests
npm test

# Load testing
ab -n 1000 -c 10 http://localhost:3000
```

### Deployment
```bash
# Build images
docker build -f docker/Dockerfile.backend -t riskguard-backend:1.0 .

# Push to registry
docker push yourregistry/riskguard-backend:1.0

# Terraform
terraform apply -var-file="prod.tfvars"
terraform destroy
```

---

## 📚 Documentation Files

| File | Content |
|------|---------|
| [README.md](./README.md) | Project overview & architecture |
| [API_DOCUMENTATION.md](./docs/API_DOCUMENTATION.md) | Complete API reference |
| [DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md) | Database design & ER diagrams |
| [DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md) | Step-by-step deployment |
| [DEVOPS_CONCEPTS.md](./docs/DEVOPS_CONCEPTS.md) | DevOps explained in depth |

---

## 🎓 Learning Outcomes

After studying this project, you will understand:

✅ **Full-Stack Development**
- Frontend: Modern React with TypeScript
- Backend: FastAPI async architecture
- Database: PostgreSQL with ORM patterns

✅ **DevOps Practices**
- Containerization with Docker
- Orchestration with Docker Compose
- Infrastructure as Code with Terraform
- CI/CD pipelines with GitHub Actions

✅ **Production Practices**
- Monitoring & alerting
- Security best practices
- Scalability patterns
- Disaster recovery

✅ **Cloud Deployment**
- AWS VPC, RDS, ECS, ALB, S3
- Blue-green deployments
- Auto-scaling setup
- Cost optimization

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/name`
2. Commit changes: `git commit -m "Add feature"`
3. Push: `git push origin feature/name`
4. Create Pull Request
5. CI/CD tests automatically run
6. Merge after approval

---

## 📈 Scaling Checklist

- [ ] Horizontal scaling setup (load balancer)
- [ ] Database read replicas configured
- [ ] Caching layer (Redis) implemented
- [ ] CDN configured (Cloudfront)
- [ ] Auto-scaling policies active
- [ ] Monitoring alerts configured
- [ ] Disaster recovery tested
- [ ] Cost optimization reviewed

---

## 🆘 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Port already in use | `docker-compose down && docker-compose up -d` |
| Database connection error | Check DATABASE_URL in .env |
| API returns 401 | Ensure Authorization header with valid token |
| Frontend blank page | Check REACT_APP_API_URL in .env |
| Tests failing | `docker-compose down -v && docker-compose up -d` |

---

## 📞 Support Resources

- **Docker Docs**: https://docs.docker.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **Terraform Docs**: https://www.terraform.io/docs
- **AWS Docs**: https://docs.aws.amazon.com
- **GitHub Actions**: https://docs.github.com/en/actions

---

## 📅 Project Timeline (If Starting from Scratch)

- **Week 1**: Backend setup (FastAPI, models, schemas)
- **Week 2**: Frontend setup (React, API client, state)
- **Week 3**: Docker & Docker Compose setup
- **Week 4**: GitHub Actions CI/CD pipeline
- **Week 5**: Terraform infrastructure code
- **Week 6**: Monitoring (Prometheus, Grafana)
- **Week 7**: Testing & documentation
- **Week 8**: Production deployment & optimization

---

## 🎯 Key Performance Indicators

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 200 ms |
| Page Load Time | < 3 seconds |
| Error Rate | < 0.1% |
| Uptime | 99.95% |
| Deployment Frequency | Daily |
| Lead Time (Dev → Prod) | < 2 hours |

---

## 📝 License

MIT License - Free for educational and professional use

---

**Last Updated**: February 2024
**Version**: 1.0.0
**Status**: Production Ready ✅

---

## Next Steps

1. **Clone the repository**
2. **Follow Quick Start** (5 minutes)
3. **Explore the code** - Read through controllers, models, services
4. **Run tests** - Verify everything works
5. **Read documentation** - Understand architecture
6. **Deploy it** - Try one of the deployment options
7. **Extend it** - Add new features!

**Happy coding! 🚀**
