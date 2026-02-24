from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.services.risk_service import RiskCalculationService, RiskAssessmentService
from app.services.url_analysis_service import URLAnalysisService
from app.schemas.schemas import ManualRiskInput, URLScanInput, RiskAssessmentResponse

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_current_user_id(authorization: str = Header(None)):
    """Extract user ID from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    token = authorization.replace("Bearer ", "")
    token_data = AuthService.verify_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token_data["user_id"]

@router.post("/manual", response_model=RiskAssessmentResponse)
async def calculate_manual_risk(
    risk_input: ManualRiskInput,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate risk using manual input
    
    **Request:**
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
        "team_experience_years": 3,
        "external_dependencies": 1,
        "defect_rate_percentage": 5,
        "rework_percentage": 10,
        "stakeholder_stability": "mixed"
    }
    ```
    
    **Response:**
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
        "recommendations": ["Budget overrun detected...", "Schedule slip..."],
        "created_at": "2024-03-15T10:30:00Z"
    }
    ```
    """
    try:
        # Calculate risk
        risk_result = RiskCalculationService.calculate_risk_score(risk_input)
        
        # Save to database
        assessment = await RiskAssessmentService.create_assessment(
            db, risk_input.project_id, user_id, risk_input, risk_result
        )
        
        response = RiskAssessmentResponse.from_orm(assessment)
        # Deserialize recommendations from JSON string
        response.recommendations = eval(assessment.recommendations) if assessment.recommendations else []
        return response
        
    except Exception as e:
        logger.error(f"Risk calculation error: {e}")
        raise HTTPException(status_code=500, detail="Risk calculation failed")

@router.post("/url-scan")
async def analyze_url(
    scan_input: URLScanInput,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze URL/repository for predictive risk assessment
    
    **Request:**
    ```json
    {
        "url": "https://github.com/torvalds/linux",
        "project_category": "Software"
    }
    ```
    
    **Response:**
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
            "Status: Indicators within nominal ranges...",
            "Action: Modularize architecture..."
        ]
    }
    ```
    """
    try:
        # Extract heuristics from URL
        metrics = URLAnalysisService.extract_heuristics(
            scan_input.url, scan_input.project_category
        )
        
        # Save scan results
        scan_result = await URLAnalysisService.save_scan_result(
            db, scan_input.url, scan_input.project_category, metrics
        )
        
        # Get recommendations
        recommendations = URLAnalysisService.generate_url_recommendations(
            metrics, scan_input.project_category
        )
        
        risk_level = URLAnalysisService.determine_risk_level(metrics["calculated_risk"])
        
        return {
            "id": scan_result.id,
            "url": scan_result.url,
            "probability": metrics["calculated_risk"],
            "risk_level": risk_level,
            "confidence_score": metrics["confidence_score"],
            "metrics": {
                "documentation": metrics["documentation_quality"],
                "update_frequency": metrics["update_frequency"],
                "maturity": metrics["maturity_stage"],
                "complexity": metrics["code_complexity"]
            },
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"URL analysis error: {e}")
        raise HTTPException(status_code=500, detail="URL analysis failed")
