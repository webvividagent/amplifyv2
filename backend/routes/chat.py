from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from database import get_db
from models import Session as DBSession, Message, User, Repository
from models.message import MessageRole
from models.session import AgentType
from schemas import ChatRequest, ChatResponse, SessionResponse
from utils.auth import get_current_user
from llm import OllamaProvider
from llm.base import LLMRequest
from config import settings
from services.model_selector import model_selector

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db_repo = None
    if request.repository_id:
        db_repo = db.query(Repository).filter(
            (Repository.id == request.repository_id) & (Repository.user_id == user_id)
        ).first()
        if not db_repo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    
    model_to_use = request.model
    if not model_to_use:
        if request.agent_type == "coding":
            model_to_use = model_selector.get_code_model()
        elif request.agent_type == "review":
            model_to_use = model_selector.get_seer_model() or model_selector.get_general_model()
        elif request.agent_type == "reasoning":
            model_to_use = model_selector.get_reasoning_model() or model_selector.get_general_model()
        else:
            model_to_use = model_selector.get_general_model()
    
    if request.session_id:
        session = db.query(DBSession).filter(
            (DBSession.id == request.session_id) & (DBSession.user_id == user_id)
        ).first()
    else:
        session = DBSession(
            user_id=user_id,
            repository_id=request.repository_id if db_repo else None,
            agent_type=request.agent_type,
            model=model_to_use,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    user_message = Message(
        session_id=session.id,
        role=MessageRole.USER,
        content=request.message,
        files_referenced=request.files or [],
    )
    db.add(user_message)
    db.commit()
    
    messages_history = db.query(Message).filter(Message.session_id == session.id).all()
    formatted_messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in messages_history
    ]
    
    system_prompt = f"You are a helpful AI coding assistant specializing in {request.agent_type} tasks."
    
    try:
        provider = OllamaProvider()
        llm_request = LLMRequest(
            system_prompt=system_prompt,
            messages=formatted_messages,
            model=session.model,
            temperature=0.7,
            max_tokens=2000,
        )
        
        llm_response = await provider.generate(llm_request)
        
        assistant_message = Message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=llm_response.content,
            tokens_used=llm_response.tokens_used,
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        return ChatResponse(
            session_id=session.id,
            message_id=assistant_message.id,
            content=llm_response.content,
            tools_used=[],
            tokens_used=llm_response.tokens_used,
            created_at=assistant_message.created_at.isoformat(),
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(DBSession).filter(
        (DBSession.id == session_id) & (DBSession.user_id == user_id)
    ).first()
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    return SessionResponse.from_orm(session)


@router.get("/sessions/")
async def list_sessions(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(DBSession).filter(DBSession.user_id == user_id).all()
    return [SessionResponse.from_orm(s) for s in sessions]
