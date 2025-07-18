from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models
from ..schemas.project import ProjectCreate, ProjectRead

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """
    List all projects across all companies.
    This helps the family see every project in the group, for reporting or tender prep.
    """
    projects = db.query(models.Project).all()
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get details for a single project.
    Useful when preparing a project profile for a tender or review.
    """
    project = db.query(models.Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/company/{company_id}", response_model=List[ProjectRead])
def list_company_projects(company_id: int, db: Session = Depends(get_db)):
    """
    List all projects for a specific company.
    Lets the heads see what each company is doing or has done, for compliance or tendering.
    """
    projects = db.query(models.Project).filter(models.Project.company_id == company_id).all()
    return projects

@router.post("/", response_model=ProjectRead)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Add a new project for a company.
    This lets the family quickly record new work, so nothing is missed when tracking performance or preparing tenders.
    """
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/{project_id}", response_model=ProjectRead)
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Update an existing project's details.
    Keeps project info up to date for accurate reporting and compliance.
    """
    db_project = db.query(models.Project).get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project (if entered in error or no longer needed).
    Helps keep the records room tidy and relevant.
    """
    db_project = db.query(models.Project).get(project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"ok": True} 