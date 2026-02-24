import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import List, Optional

from app.models.models import Project, RiskAssessment, RiskLevel

logger = logging.getLogger(__name__)

class ProjectService:
    """Project management service"""
    
    @staticmethod
    async def create_project(db: AsyncSession, user_id: int, project_data: dict) -> Project:
        """Create a new project"""
        project = Project(
            user_id=user_id,
            name=project_data["name"],
            description=project_data.get("description"),
            project_type=project_data["project_type"],
            duration_months=project_data.get("duration_months"),
            expected_budget=project_data.get("expected_budget")
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        logger.info(f"Project created: {project.id} by user {user_id}")
        return project
    
    @staticmethod
    async def get_user_projects(db: AsyncSession, user_id: int) -> List[Project]:
        """Get all projects for a user"""
        stmt = select(Project).where(Project.user_id == user_id).order_by(Project.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_project_by_id(db: AsyncSession, project_id: int, user_id: int) -> Optional[Project]:
        """Get a specific project (with user authorization check)"""
        stmt = select(Project).where(
            (Project.id == project_id) & (Project.user_id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()
    
    @staticmethod
    async def delete_project(db: AsyncSession, project_id: int, user_id: int) -> bool:
        """Delete a project (with user authorization check)"""
        project = await ProjectService.get_project_by_id(db, project_id, user_id)
        if project:
            await db.delete(project)
            await db.commit()
            logger.info(f"Project deleted: {project_id}")
            return True
        return False

class AnalyticsService:
    """Analytics and reporting service"""
    
    @staticmethod
    async def get_portfolio_summary(db: AsyncSession, user_id: int) -> dict:
        """Get portfolio risk summary"""
        stmt = select(
            func.count().label("total"),
            func.sum((RiskAssessment.risk_level == RiskLevel.LOW).cast(int)).label("low_count"),
            func.sum((RiskAssessment.risk_level == RiskLevel.MEDIUM).cast(int)).label("medium_count"),
            func.sum((RiskAssessment.risk_level == RiskLevel.HIGH).cast(int)).label("high_count"),
            func.avg(RiskAssessment.probability).label("avg_probability")
        ).join(Project).where(Project.user_id == user_id)
        
        result = await db.execute(stmt)
        row = result.first()
        
        return {
            "total_projects": row.total or 0,
            "low_risk": row.low_count or 0,
            "medium_risk": row.medium_count or 0,
            "high_risk": row.high_count or 0,
            "average_risk": float(row.avg_probability) if row.avg_probability else 0
        }
    
    @staticmethod
    async def calculate_risk_volatility(db: AsyncSession, user_id: int) -> float:
        """Calculate standard deviation of risk scores"""
        stmt = select(RiskAssessment.probability).join(Project).where(
            Project.user_id == user_id
        )
        result = await db.execute(stmt)
        scores = [row[0] for row in result.all()]
        
        if len(scores) < 2:
            return 0.0
        
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / (len(scores) - 1)
        std_dev = variance ** 0.5
        
        return round(std_dev, 2)
    
    @staticmethod
    async def get_risk_trends(db: AsyncSession, user_id: int, periods: int = 6) -> List[dict]:
        """Get risk trends over time periods"""
        stmt = select(
            RiskAssessment.created_at,
            func.avg(RiskAssessment.probability)
        ).join(Project).where(
            Project.user_id == user_id
        ).group_by(
            func.date_trunc('day', RiskAssessment.created_at)
        ).order_by(RiskAssessment.created_at.desc()).limit(periods)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        trends = []
        for row in reversed(rows):
            trends.append({
                "period": row[0].strftime("%Y-%m-%d") if row[0] else "N/A",
                "average_risk": float(row[1]) if row[1] else 0
            })
        
        return trends
    
    @staticmethod
    async def get_factor_analysis(db: AsyncSession, user_id: int) -> List[dict]:
        """Analyze impact factors across portfolio"""
        stmt = select(
            func.avg(RiskAssessment.schedule_impact).label("schedule"),
            func.avg(RiskAssessment.cost_impact).label("cost"),
            func.avg(RiskAssessment.resource_impact).label("resource"),
            func.avg(RiskAssessment.complexity_impact).label("complexity"),
            func.avg(RiskAssessment.advanced_impact).label("advanced")
        ).join(Project).where(Project.user_id == user_id)
        
        result = await db.execute(stmt)
        row = result.first()
        
        if not row:
            return []
        
        factors = [
            {"factor": "Schedule Variance", "impact": int(row.schedule or 0)},
            {"factor": "Cost Variance", "impact": int(row.cost or 0)},
            {"factor": "Resource Constraint", "impact": int(row.resource or 0)},
            {"factor": "Complexity", "impact": int(row.complexity or 0)},
            {"factor": "Advanced Signals", "impact": int(row.advanced or 0)}
        ]
        
        # Filter out zero impacts for cleaner reporting
        return [f for f in factors if f["impact"] > 0]
