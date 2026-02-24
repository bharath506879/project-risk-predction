from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.database.connection import Base

class User(Base):
    """User model for authentication and project ownership"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="assessor", cascade="all, delete-orphan")

class Project(Base):
    """Project model for portfolio tracking"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    project_type = Column(String(50), nullable=False)  # Software, Construction, R&D, Marketing
    status = Column(String(50), default="Active")  # Active, Completed, On-Hold, Cancelled
    duration_months = Column(Integer)
    expected_budget = Column(Float)
    actual_budget = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    risk_assessments = relationship("RiskAssessment", back_populates="project", cascade="all, delete-orphan")

class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class RiskAssessment(Base):
    """Risk assessment results model"""
    __tablename__ = "risk_assessments"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assessor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Risk metrics
    probability = Column(Integer, nullable=False)  # 0-100
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    assessment_method = Column(String(50), nullable=False)  # Manual or Predictive Scan
    
    # Breakdown percentages
    schedule_impact = Column(Integer, default=0)
    cost_impact = Column(Integer, default=0)
    resource_impact = Column(Integer, default=0)
    complexity_impact = Column(Integer, default=0)
    advanced_impact = Column(Integer, default=0)
    
    # Input parameters
    input_parameters = Column(Text)  # JSON string of input data
    recommendations = Column(Text)   # JSON string of mitigation strategies
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="risk_assessments")
    assessor = relationship("User", back_populates="risk_assessments")

class URLScanResult(Base):
    """URL/Repository scan results for predictive analysis"""
    __tablename__ = "url_scan_results"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Source information
    url = Column(String(2048), nullable=False)
    repository_type = Column(String(50))  # GitHub, GitLab, Bitbucket, etc.
    project_category = Column(String(50))  # Software, Research, Construction, etc.
    
    # Extracted metrics
    documentation_quality = Column(String(50))  # Low, Medium, High
    update_frequency = Column(String(50))       # Low, Medium, High
    maturity_stage = Column(String(50))        # Early, Mid-Stage, Mature
    code_complexity = Column(String(50))       # Low, Medium, High
    
    # Heuristic risk score
    calculated_risk = Column(Integer)
    confidence_score = Column(Float, default=0.92)
    
    metadata = Column(Text)  # JSON string of extracted data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
