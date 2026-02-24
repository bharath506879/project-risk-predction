import logging
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_

from app.models.models import RiskAssessment, Project, RiskLevel
from app.schemas.schemas import ManualRiskInput, RiskAssessmentResponse

logger = logging.getLogger(__name__)

class RiskCalculationService:
    """Deterministic risk calculation engine"""
    
    RISK_THRESHOLDS = {
        "LOW": 35,
        "HIGH": 65,
        "MAX": 99,
        "MIN": 1
    }
    
    @staticmethod
    def calculate_risk_score(input_data: ManualRiskInput) -> dict:
        """
        Deterministic multi-factor risk calculation engine
        
        This implements the same algorithm as the frontend but on the backend,
        ensuring consistency and auditability.
        """
        # Normalize duration
        duration_days = max(1, input_data.duration_months * 30)
        
        # Schedule Variance Index
        sv_index = (input_data.delay_days / duration_days) * 100
        
        # Cost Variance Index
        cv_index = max(0, input_data.budget_used_percentage - input_data.completion_percentage)
        
        # Calculate individual impact factors
        schedule_impact = sv_index * 1.5
        cost_impact = cv_index * 1.2
        
        # Resource impact
        resource_impact = 0
        if input_data.resource_availability == "shortage":
            resource_impact = 25
        elif input_data.resource_availability == "partial":
            resource_impact = 10
        
        # Complexity impact
        complexity_impact = 0
        if input_data.complexity == "high":
            complexity_impact = 15
        elif input_data.complexity == "medium":
            complexity_impact = 5
        
        # Advanced signal processing
        advanced_impact = 0
        if input_data.advanced_enabled:
            advanced_impact += (input_data.scope_change_per_month or 0) * 2
            advanced_impact -= (input_data.team_experience_years or 0) * 1.5
            advanced_impact += (input_data.external_dependencies or 0) * 1.0
            advanced_impact += (input_data.defect_rate_percentage or 0) * 0.5
            advanced_impact += (input_data.rework_percentage or 0) * 0.5
            
            if input_data.stakeholder_stability == "volatile":
                advanced_impact += 15
            elif input_data.stakeholder_stability == "stable":
                advanced_impact -= 5
            
            advanced_impact = max(-15, min(30, advanced_impact))
        
        # Completion buffer adjustment
        completion_buffer = 0
        if input_data.completion_percentage > 90:
            completion_buffer = -20
        elif input_data.completion_percentage < 10:
            completion_buffer = 5
        
        # Calculate raw score
        raw_score = (schedule_impact + cost_impact + resource_impact + 
                    complexity_impact + advanced_impact + completion_buffer)
        
        # Normalize to 0-100 range
        probability = max(
            RiskCalculationService.RISK_THRESHOLDS["MIN"],
            min(RiskCalculationService.RISK_THRESHOLDS["MAX"], round(raw_score))
        )
        
        # Determine risk level
        if probability > RiskCalculationService.RISK_THRESHOLDS["HIGH"]:
            level = RiskLevel.HIGH
        elif probability > RiskCalculationService.RISK_THRESHOLDS["LOW"]:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        # Calculate impact breakdown percentages
        total_impact_vectors = max(
            1, 
            abs(schedule_impact) + abs(cost_impact) + abs(resource_impact) + 
            abs(complexity_impact) + abs(advanced_impact)
        )
        
        breakdown = {
            "schedule": round((abs(schedule_impact) / total_impact_vectors) * 100),
            "cost": round((abs(cost_impact) / total_impact_vectors) * 100),
            "resource": round((abs(resource_impact) / total_impact_vectors) * 100),
            "complexity": round((abs(complexity_impact) / total_impact_vectors) * 100),
            "advanced": round((abs(advanced_impact) / total_impact_vectors) * 100)
        }
        
        # Generate recommendations based on risk factors
        recommendations = RiskCalculationService.generate_recommendations(
            probability, input_data, sv_index, cv_index
        )
        
        return {
            "probability": probability,
            "risk_level": level,
            "breakdown": breakdown,
            "recommendations": recommendations,
            "derived_metrics": {
                "sv_index": round(sv_index, 2),
                "cv_index": round(cv_index, 2)
            }
        }
    
    @staticmethod
    def generate_recommendations(probability: int, input_data: ManualRiskInput, 
                                sv_index: float, cv_index: float) -> List[str]:
        """Generate mitigation recommendations based on risk analysis"""
        recommendations = []
        
        # Resource-based recommendations
        if input_data.resource_availability == "shortage":
            recommendations.append("Resource constraint is critical. Augment team capacity immediately.")
        
        # Cost-based recommendations
        if cv_index > 20:
            recommendations.append("Budget burn exceeds baseline. Execute cost audit and revise projections.")
        
        # Schedule-based recommendations
        if sv_index > 10:
            recommendations.append("Schedule slip detected. Re-evaluate critical path and implement recovery plan.")
        
        # Scope-based recommendations
        if input_data.advanced_enabled and (input_data.scope_change_per_month or 0) > 2:
            recommendations.append("High scope churn detected. Implement strict change control board.")
        
        # Completion-based recommendations
        if input_data.completion_percentage < 10 and input_data.duration_months > 6:
            recommendations.append("Project is significantly behind. Review requirements and consider schedule adjustment.")
        
        # Low-risk recommendations
        if probability < RiskCalculationService.RISK_THRESHOLDS["LOW"]:
            recommendations.append("Metrics within tolerance. Maintain current operational baseline and monitoring.")
        
        # Complexity-based recommendations
        if input_data.complexity == "high":
            recommendations.append("High complexity project. Increase testing coverage and documentation frequency.")
        
        # Stakeholder-based recommendations
        if input_data.advanced_enabled and input_data.stakeholder_stability == "volatile":
            recommendations.append("Volatile stakeholder environment. Increase communication frequency and establish clear expectations.")
        
        # Default recommendation
        if not recommendations:
            recommendations.append("Review downstream architectural dependencies and validate assumptions.")
        
        return recommendations


class RiskAssessmentService:
    """Risk assessment persistence and retrieval service"""
    
    @staticmethod
    async def create_assessment(
        db: AsyncSession,
        project_id: int,
        assessor_id: int,
        input_data: ManualRiskInput,
        risk_result: dict
    ) -> RiskAssessment:
        """Create and persist a risk assessment"""
        assessment = RiskAssessment(
            project_id=project_id,
            assessor_id=assessor_id,
            probability=risk_result["probability"],
            risk_level=risk_result["risk_level"],
            assessment_method="Manual",
            schedule_impact=risk_result["breakdown"]["schedule"],
            cost_impact=risk_result["breakdown"]["cost"],
            resource_impact=risk_result["breakdown"]["resource"],
            complexity_impact=risk_result["breakdown"]["complexity"],
            advanced_impact=risk_result["breakdown"]["advanced"],
            input_parameters=json.dumps(input_data.dict()),
            recommendations=json.dumps(risk_result["recommendations"])
        )
        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        logger.info(f"Risk assessment created: {assessment.id}")
        return assessment
    
    @staticmethod
    async def get_assessment_by_id(db: AsyncSession, assessment_id: int) -> Optional[RiskAssessment]:
        """Get risk assessment by ID"""
        stmt = select(RiskAssessment).where(RiskAssessment.id == assessment_id)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    @staticmethod
    async def get_project_assessments(db: AsyncSession, project_id: int) -> List[RiskAssessment]:
        """Get all assessments for a project"""
        stmt = select(RiskAssessment).where(
            RiskAssessment.project_id == project_id
        ).order_by(RiskAssessment.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()
