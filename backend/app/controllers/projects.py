from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database.connection import get_db
from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_current_user_id(authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    """Extract and validate user ID from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        token = authorization.replace("Bearer ", "")
        token_data = AuthService.verify_token(token)
        if not token_data:
            raise HTTPException(status_code=401, detail="Invalid token")
        return token_data["user_id"]
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.post("", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project
    
    **Request:**
    ```json
    {
        "name": "Enterprise Migration",
        "description": "Cloud migration of legacy systems",
        "project_type": "Software",
        "duration_months": 12,
        "expected_budget": 500000
    }
    ```
    """
    try:
        project = await ProjectService.create_project(
            db, user_id, project_data.dict()
        )
        return ProjectResponse.from_orm(project)
    except Exception as e:
        logger.error(f"Project creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create project")

@router.get("", response_model=list[ProjectResponse])
async def get_projects(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get all projects for the current user"""
    projects = await ProjectService.get_user_projects(db, user_id)
    return [ProjectResponse.from_orm(p) for p in projects]

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project"""
    project = await ProjectService.get_project_by_id(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.from_orm(project)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    update_data: ProjectUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    project = await ProjectService.get_project_by_id(db, project_id, user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(project, key, value)
    
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.from_orm(project)

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    success = await ProjectService.delete_project(db, project_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}
