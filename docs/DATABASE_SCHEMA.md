# PostgreSQL database schema documentation

## Tables

### users
- **id** (INT, PK): User ID
- **email** (VARCHAR, UNIQUE): User email address
- **username** (VARCHAR, UNIQUE): Username for login
- **hashed_password** (VARCHAR): Bcrypt hashed password
- **full_name** (VARCHAR): User's full name
- **is_active** (BOOLEAN): Account active status
- **created_at** (TIMESTAMP): Account creation timestamp
- **updated_at** (TIMESTAMP): Last update timestamp

### projects
- **id** (INT, PK): Project ID
- **user_id** (INT, FK → users.id): Project owner
- **name** (VARCHAR): Project name
- **description** (TEXT): Project description
- **project_type** (VARCHAR): Software, Construction, R&D, Marketing
- **status** (VARCHAR): Active, Completed, On-Hold, Cancelled
- **duration_months** (INT): Expected project duration
- **expected_budget** (FLOAT): Expected project budget
- **actual_budget** (FLOAT): Actual spending
- **created_at** (TIMESTAMP): Project creation date
- **updated_at** (TIMESTAMP): Last update date

### risk_assessments
- **id** (INT, PK): Assessment ID
- **project_id** (INT, FK → projects.id): Associated project
- **assessor_id** (INT, FK → users.id): User who created assessment
- **probability** (INT): Risk probability 0-100
- **risk_level** (VARCHAR): Low, Medium, High
- **assessment_method** (VARCHAR): Manual or Predictive Scan
- **schedule_impact** (INT): Schedule impact percentage
- **cost_impact** (INT): Cost impact percentage
- **resource_impact** (INT): Resource constraint impact
- **complexity_impact** (INT): Complexity impact
- **advanced_impact** (INT): Advanced signals impact
- **input_parameters** (TEXT): JSON of input data
- **recommendations** (TEXT): JSON array of recommendations
- **created_at** (TIMESTAMP): Assessment timestamp

### url_scan_results
- **id** (INT, PK): Scan result ID
- **project_id** (INT, FK → projects.id, NULL): Associated project (optional)
- **url** (VARCHAR): Repository/project URL
- **repository_type** (VARCHAR): GitHub, GitLab, Bitbucket, etc.
- **project_category** (VARCHAR): Software, Research, Construction
- **documentation_quality** (VARCHAR): Low, Medium, High
- **update_frequency** (VARCHAR): Low, Medium, High
- **maturity_stage** (VARCHAR): Early, Mid-Stage, Mature
- **code_complexity** (VARCHAR): Low, Medium, High
- **calculated_risk** (INT): Risk score
- **confidence_score** (FLOAT): Confidence in prediction
- **metadata** (TEXT): JSON of extracted data
- **created_at** (TIMESTAMP): Scan timestamp

## Relationships

```
User (1) ----> (Many) Project
User (1) ----> (Many) RiskAssessment
Project (1) ----> (Many) RiskAssessment
Project (1) ----> (Many) URLScanResult
```

## Indexes
- users.email (UNIQUE): Fast email lookup for authentication
- projects.name: Fast project name search
