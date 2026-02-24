from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ==================== AUTH SCHEMAS ====================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ==================== PROJECT SCHEMAS ====================

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_type: str
    duration_months: Optional[int] = None
    expected_budget: Optional[float] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    actual_budget: Optional[float] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    project_type: str
    status: str
    duration_months: Optional[int]
    expected_budget: Optional[float]
    actual_budget: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== RISK ASSESSMENT SCHEMAS ====================

class RiskBreakdown(BaseModel):
    schedule: int
    cost: int
    resource: int
    complexity: int
    advanced: int

class ManualRiskInput(BaseModel):
    project_id: int
    duration_months: float
    completion_percentage: int
    delay_days: int
    budget_used_percentage: int
    resource_availability: str  # full, partial, shortage
    complexity: str  # low, medium, high
    advanced_enabled: bool = False
    
    # Advanced parameters
    scope_change_per_month: Optional[int] = None
    team_experience_years: Optional[int] = None
    external_dependencies: Optional[int] = None
    defect_rate_percentage: Optional[float] = None
    rework_percentage: Optional[float] = None
    stakeholder_stability: Optional[str] = None

class RiskAssessmentResponse(BaseModel):
    id: int
    project_id: int
    probability: int
    risk_level: str
    assessment_method: str
    schedule_impact: int
    cost_impact: int
    resource_impact: int
    complexity_impact: int
    advanced_impact: int
    recommendations: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== URL SCAN SCHEMAS ====================

class URLScanInput(BaseModel):
    url: str
    project_category: str  # Software, Research, Construction, Other

class ScanMetrics(BaseModel):
    documentation: str
    update_frequency: str
    maturity: str
    complexity: str

class URLScanResponse(BaseModel):
    id: int
    url: str
    probability: int
    risk_level: str
    confidence_score: float
    metrics: ScanMetrics
    recommendations: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== ANALYTICS SCHEMAS ====================

class RiskPortfolioSummary(BaseModel):
    total_projects: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    average_risk: float
    risk_volatility: float

class RiskTrend(BaseModel):
    period: str
    average_risk: float
    min_risk: int
    max_risk: int

class FactorAnalysis(BaseModel):
    factor_name: str
    impact_percentage: int
    affected_projects: int

class AnalyticsResponse(BaseModel):
    portfolio_summary: RiskPortfolioSummary
    recent_trends: List[RiskTrend]
    factor_analysis: List[FactorAnalysis]
    
    class Config:
        from_attributes = True
