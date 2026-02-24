from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.services.project_service import AnalyticsService
from app.schemas.schemas import AnalyticsResponse

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

@router.get("/summary")
async def get_analytics_summary(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get portfolio analytics summary
    
    **Response:**
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
            }
        ],
        "factor_analysis": [
            {"factor_name": "Schedule Variance", "impact_percentage": 35},
            {"factor_name": "Budget Variance", "impact_percentage": 30}
        ]
    }
    ```
    """
    try:
        portfolio_summary = await AnalyticsService.get_portfolio_summary(db, user_id)
        volatility = await AnalyticsService.calculate_risk_volatility(db, user_id)
        trends = await AnalyticsService.get_risk_trends(db, user_id)
        factors = await AnalyticsService.get_factor_analysis(db, user_id)
        
        return {
            "portfolio_summary": {
                **portfolio_summary,
                "risk_volatility": volatility
            },
            "recent_trends": trends,
            "factor_analysis": [
                {
                    "factor_name": f["factor"],
                    "impact_percentage": f["impact"]
                } for f in factors
            ]
        }
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.get("/trends")
async def get_risk_trends(
    periods: int = 6,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get risk trends over time"""
    trends = await AnalyticsService.get_risk_trends(db, user_id, periods)
    return {"trends": trends}

@router.get("/factors")
async def get_factor_analysis(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get impact factor analysis"""
    factors = await AnalyticsService.get_factor_analysis(db, user_id)
    return {"factors": factors}
