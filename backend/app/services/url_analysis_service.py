import logging
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.models.models import URLScanResult, Project
from app.schemas.schemas import URLScanInput, URLScanResponse

logger = logging.getLogger(__name__)

class URLAnalysisService:
    """Heuristic-based URL/repository analysis for predictive risk assessment"""
    
    @staticmethod
    def extract_heuristics(url: str, project_category: str) -> dict:
        """
        Extract heuristic signals from URL and repository
        
        In production, this would make actual HTTP requests to:
        - Clone/fetch repository metadata
        - Analyze commit history
        - Extract README quality
        - Assess documentation completeness
        - Evaluate maintainer activity
        
        For now, we use pattern matching and seeding for demo purposes.
        """
        
        seed = 0
        for char in url:
            seed = ((seed << 5) - seed) + ord(char)
            seed |= 0
        
        rand = abs(seed) % 100 / 100.0
        
        is_github = "github" in url or "gitlab" in url or "bitbucket" in url
        keywords_early = any(kw in url.lower() for kw in ["demo", "test", "proto", "alpha", "beta", "temp", "mvp"])
        keywords_mature = any(kw in url.lower() for kw in ["v1", "v2", "release", "stable", "prod", "main", "master", "core"])
        keywords_complex = any(kw in url.lower() for kw in ["enterprise", "microservice", "arch", "platform", "infra"])
        
        # Determine metrics based on keywords and patterns
        doc_quality = "High" if (is_github and keywords_mature) else ("Low" if (not is_github or keywords_early) else "Medium")
        update_freq = "High" if (keywords_mature or keywords_early) else ("Low" if rand < 0.3 else "Medium")
        complexity = "High" if keywords_complex else "Medium"
        maturity = "Early (Prototype)" if keywords_early else ("Mature (Production)" if keywords_mature else "Mid-Stage")
        
        # Calculate risk score
        score = 50
        if not is_github:
            score += 15
        else:
            score -= 5
        
        if maturity == "Early (Prototype)":
            score += 25
        elif maturity == "Mature (Production)":
            score -= 20
        
        if complexity == "High":
            score += 10
        
        if project_category == "Research":
            score += 10
        elif project_category == "Construction":
            score += 5
        
        score += (rand * 10) - 5
        score = max(5, min(98, score))
        
        return {
            "documentation_quality": doc_quality,
            "update_frequency": update_freq,
            "maturity_stage": maturity,
            "code_complexity": complexity,
            "calculated_risk": round(score),
            "confidence_score": 0.92,
            "heuristic_data": {
                "is_github": is_github,
                "keywords_detected": list(set([
                    *([k for k in ["demo", "test", "proto"] if k in url.lower()]),
                    *([k for k in ["stable", "prod", "release"] if k in url.lower()])
                ]))
            }
        }
    
    @staticmethod
    def determine_risk_level(score: int) -> str:
        """Map risk score to risk level"""
        if score > 65:
            return "High"
        elif score > 35:
            return "Medium"
        else:
            return "Low"
    
    @staticmethod
    def generate_url_recommendations(metrics: dict, category: str) -> List[str]:
        """Generate recommendations based on extracted metrics"""
        recommendations = []
        
        if metrics["documentation_quality"] == "Low":
            recommendations.append("Risk: Low documentation observability. Audit README completeness and API docs.")
        
        if metrics["update_frequency"] == "Low":
            recommendations.append("Risk: Stale activity detected. Verify maintainer availability and project health.")
        
        if "Early" in metrics["maturity_stage"]:
            recommendations.append("Action: Implement strict version control and establish robust CI/CD pipelines.")
        
        if metrics["code_complexity"] == "High":
            recommendations.append("Action: Modularize architecture to reduce coupling and improve testability.")
        
        if category == "Research":
            recommendations.append("Action: Define clear go/no-go milestones for experimental phases and prototype iterations.")
        
        if not recommendations:
            recommendations.append("Status: Indicators within nominal ranges. Continue standard monitoring and regular reviews.")
        
        return recommendations
    
    @staticmethod
    async def save_scan_result(
        db: AsyncSession,
        url: str,
        project_category: str,
        metrics: dict
    ) -> URLScanResult:
        """Save URL scan result to database"""
        scan = URLScanResult(
            url=url,
            project_category=project_category,
            repository_type="GitHub" if "github" in url else ("GitLab" if "gitlab" in url else "Other"),
            documentation_quality=metrics["documentation_quality"],
            update_frequency=metrics["update_frequency"],
            maturity_stage=metrics["maturity_stage"],
            code_complexity=metrics["code_complexity"],
            calculated_risk=metrics["calculated_risk"],
            confidence_score=metrics["confidence_score"],
            metadata=json.dumps(metrics["heuristic_data"])
        )
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        logger.info(f"URL scan result saved: {scan.id}")
        return scan
