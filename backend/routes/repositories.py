from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from models import Repository, User
from schemas import RepositoryCreate, RepositoryResponse, RepositorySearchRequest
from utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/repositories", tags=["repositories"])


@router.post("/", response_model=RepositoryResponse)
async def create_repository(
    repo_create: RepositoryCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_repo = Repository(
        user_id=db_user.id,
        name=repo_create.name,
        git_url=repo_create.git_url,
        local_path=repo_create.local_path,
        language=repo_create.language,
        description=repo_create.description,
    )
    
    db.add(db_repo)
    db.commit()
    db.refresh(db_repo)
    
    return RepositoryResponse.from_orm(db_repo)


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: UUID,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_repo = db.query(Repository).filter(
        (Repository.id == repo_id) & (Repository.user_id == user_id)
    ).first()
    
    if not db_repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    
    return RepositoryResponse.from_orm(db_repo)


@router.get("/", response_model=list[RepositoryResponse])
async def list_repositories(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repositories = db.query(Repository).filter(Repository.user_id == user_id).all()
    return [RepositoryResponse.from_orm(repo) for repo in repositories]


@router.post("/{repo_id}/index")
async def index_repository(
    repo_id: UUID,
    force_reindex: bool = False,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_repo = db.query(Repository).filter(
        (Repository.id == repo_id) & (Repository.user_id == user_id)
    ).first()
    
    if not db_repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    
    return {
        "repo_id": str(repo_id),
        "indexing": True,
        "progress": 0,
        "message": "Indexing started (background task)"
    }


@router.post("/{repo_id}/search")
async def search_repository(
    repo_id: UUID,
    search_request: RepositorySearchRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_repo = db.query(Repository).filter(
        (Repository.id == repo_id) & (Repository.user_id == user_id)
    ).first()
    
    if not db_repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    
    return {
        "query": search_request.query,
        "results": [],
        "total": 0
    }
