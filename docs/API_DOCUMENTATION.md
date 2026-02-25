# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require `Authorization: Bearer {token}` header.

Get token by logging in:
```bash
POST /auth/login
{
  "email": "user@example.com",
  "password": "password"
}
```

---

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "created_at": "2024-03-15T10:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Email/username already exists
- `422 Unprocessable Entity`: Invalid email format

---

### POST /auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "created_at": "2024-03-15T10:00:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid email or password

---

## Projects Endpoints

### POST /projects
Create a new project.

**Request Body:**
```json
{
  "name": "Enterprise Cloud Migration",
  "description": "Migrate legacy systems to AWS",
  "project_type": "Software",
  "duration_months": 12,
  "expected_budget": 500000
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Enterprise Cloud Migration",
  "description": "Migrate legacy systems to AWS",
  "project_type": "Software",
  "status": "Active",
  "duration_months": 12,
  "expected_budget": 500000,
  "actual_budget": 0,
  "created_at": "2024-03-15T10:30:00Z",
  "updated_at": "2024-03-15T10:30:00Z"
}
```

---

### GET /projects
Retrieve all projects for the authenticated user.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Enterprise Cloud Migration",
    "project_type": "Software",
    "status": "Active",
    "created_at": "2024-03-15T10:30:00Z"
  },
  {
    "id": 2,
    "name": "Building Construction",
    "project_type": "Construction",
    "status": "Completed",
    "created_at": "2024-02-20T14:15:00Z"
  }
]
```

---

### GET /projects/{project_id}
Retrieve specific project details.

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Enterprise Cloud Migration",
  "description": "Migrate legacy systems to AWS",
  "project_type": "Software",
  "status": "Active",
  "duration_months": 12,
  "expected_budget": 500000,
  "actual_budget": 125000,
  "created_at": "2024-03-15T10:30:00Z",
  "updated_at": "2024-03-16T09:45:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Project not found

---

### PUT /projects/{project_id}
Update project details.

**Request Body (all fields optional):**
```json
{
  "name": "Updated Project Name",
  "status": "On-Hold",
  "actual_budget": 150000
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Updated Project Name",
  "project_type": "Software",
  "status": "On-Hold",
  "actual_budget": 150000,
  "updated_at": "2024-03-16T14:20:00Z"
}
```

---

### DELETE /projects/{project_id}
Delete a project and all associated assessments.

**Response (200 OK):**
```json
{
  "message": "Project deleted successfully"
}
```

---

## Risk Assessment Endpoints

### POST /risk/manual
Calculate risk using manual input parameters.

**Request Body:**
```json
{
  "project_id": 1,
  "duration_months": 12,
  "completion_percentage": 45,
  "delay_days": 10,
  "budget_used_percentage": 50,
  "resource_availability": "partial",
  "complexity": "high",
  "advanced_enabled": true,
  "scope_change_per_month": 2,
  "team_experience_years": 5,
  "external_dependencies": 1,
  "defect_rate_percentage": 3.5,
  "rework_percentage": 8,
  "stakeholder_stability": "stable"
}
```

**Parameters:**
- `duration_months`: Expected project duration
- `completion_percentage`: Current project completion (0-100)
- `delay_days`: Days behind schedule
- `budget_used_percentage`: Budget spent (0-100)
- `resource_availability`: "full" | "partial" | "shortage"
- `complexity`: "low" | "medium" | "high"
- `stakeholder_stability`: "stable" | "mixed" | "volatile"

**Response (201 Created):**
```json
{
  "id": 1,
  "project_id": 1,
  "probability": 62,
  "risk_level": "Medium",
  "assessment_method": "Manual",
  "schedule_impact": 25,
  "cost_impact": 30,
  "resource_impact": 15,
  "complexity_impact": 20,
  "advanced_impact": 10,
  "recommendations": [
    "Budget burn exceeds baseline. Execute cost audit and revise budget projections.",
    "Schedule slip detected. Re-evaluate critical path and implement recovery plan.",
    "High complexity project. Increase testing coverage and documentation frequency."
  ],
  "created_at": "2024-03-15T10:45:00Z"
}
```

**Risk Level Mapping:**
- `probability < 35`: Low
- `35 <= probability <= 65`: Medium
- `probability > 65`: High

---

### POST /risk/url-scan
Analyze repository/URL for predictive risk assessment.

**Request Body:**
```json
{
  "url": "https://github.com/torvalds/linux",
  "project_category": "Software"
}
```

**Parameters:**
- `url`: Repository or project URL
- `project_category`: "Software" | "Research" | "Construction" | "Other"

**Response (201 Created):**
```json
{
  "id": 1,
  "url": "https://github.com/torvalds/linux",
  "probability": 35,
  "risk_level": "Low",
  "confidence_score": 0.92,
  "metrics": {
    "documentation": "High",
    "update_frequency": "High",
    "maturity": "Mature (Production)",
    "complexity": "High"
  },
  "recommendations": [
    "Status: Indicators within nominal ranges. Continue standard monitoring.",
    "Action: Modularize architecture to reduce coupling and improve testability."
  ]
}
```

**Extracted Metrics:**
- `documentation`: Assessment of README and docs quality
- `update_frequency`: How often the project is updated
- `maturity`: Project lifecycle stage
- `complexity`: Code and architecture complexity

---

## Analytics Endpoints

### GET /analytics/summary
Get portfolio-wide risk analytics summary.

**Query Parameters:**
None (uses authenticated user's projects)

**Response (200 OK):**
```json
{
  "portfolio_summary": {
    "total_projects": 5,
    "low_risk_count": 2,
    "medium_risk_count": 2,
    "high_risk_count": 1,
    "average_risk": 48.5,
    "risk_volatility": 12.3
  },
  "recent_trends": [
    {
      "period": "2024-03-15",
      "average_risk": 45.0,
      "min_risk": 20,
      "max_risk": 75
    },
    {
      "period": "2024-03-16",
      "average_risk": 50.0,
      "min_risk": 25,
      "max_risk": 80
    }
  ],
  "factor_analysis": [
    {
      "factor_name": "Schedule Variance",
      "impact_percentage": 35
    },
    {
      "factor_name": "Budget Variance",
      "impact_percentage": 30
    },
    {
      "factor_name": "Resource Constraint",
      "impact_percentage": 20
    }
  ]
}
```

**Metrics Explained:**
- `risk_volatility`: Standard deviation of risk scores (?)
- `factor_analysis`: Which risk factors impact the portfolio most
- `recent_trends`: Historical risk trajectory

---

### GET /analytics/trends
Get risk trends over time.

**Query Parameters:**
- `periods`: Number of time periods to retrieve (default: 6)

**Response (200 OK):**
```json
{
  "trends": [
    {
      "period": "2024-03-10",
      "average_risk": 42.0
    },
    {
      "period": "2024-03-11",
      "average_risk": 45.5
    },
    {
      "period": "2024-03-12",
      "average_risk": 48.2
    }
  ]
}
```

---

### GET /analytics/factors
Get factor contribution analysis.

**Response (200 OK):**
```json
{
  "factors": [
    {
      "factor": "Schedule Variance",
      "impact": 35
    },
    {
      "factor": "Cost Variance",
      "impact": 30
    },
    {
      "factor": "Resource Constraint",
      "impact": 20
    },
    {
      "factor": "Complexity",
      "impact": 15
    }
  ]
}
```

---

## Health & Monitoring

### GET /health
Check API health status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "RiskGuard API",
  "version": "1.0.0"
}
```

---

### GET /metrics
Get Prometheus metrics (OpenMetrics format).

**Response:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/projects",status="200"} 150
http_requests_total{method="POST",endpoint="/api/risk/manual",status="201"} 45

# HELP http_request_duration_seconds HTTP request duration
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="POST",endpoint="/api/risk/manual",le="0.1"} 30
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

**Common HTTP Status Codes:**
- `200 OK`: Successful GET request
- `201 Created`: Successful POST/creation
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

**Example Error:**
```json
{
  "detail": "Project not found"
}
```

---

## Rate Limiting

No rate limiting is currently enforced, but production should implement:
- 100 requests per minute for public endpoints
- 1000 requests per minute for authenticated endpoints

---

## Pagination (Future)

Standard pagination format:
```
GET /projects?skip=0&limit=10
```

Response:
```json
{
  "items": [...],
  "total": 45,
  "skip": 0,
  "limit": 10
}
```

---

## Versioning

Current API version: `v1`
Future versions will use `/api/v2`, `/api/v3`, etc.

Backwards compatibility is maintained within major versions.
