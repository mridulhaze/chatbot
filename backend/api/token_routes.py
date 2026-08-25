import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends

from backend.models.schemas import (
    TokenCreateRequest,
    TokenCreateResponse,
    TokenPublicStatus,
    ServiceTypeSchema,
    SolvedSimilarProblem
)
from backend.services.token_service import get_token_domain_service
from backend.services.similarity_service import get_similarity_service

logger = logging.getLogger("NU_TOKEN_REST_API")
router = APIRouter(prefix="/api/v1/tokens", tags=["Token Public Endpoints"])

@router.get("/services", response_model=List[ServiceTypeSchema])
def list_active_services():
    service = get_token_domain_service()
    return service.get_services()

@router.post("/create", response_model=TokenCreateResponse)
def create_support_token(payload: TokenCreateRequest):
    service = get_token_domain_service()
    return service.create_token(payload)

@router.get("/status/{token_id}", response_model=TokenPublicStatus)
def check_token_status(token_id: str):
    service = get_token_domain_service()
    status_data = service.get_public_token_status(token_id.strip().upper())
    if not status_data:
        raise HTTPException(status_code=404, detail=f"Token {token_id} not found.")
    return status_data

@router.get("/similar-solved", response_model=List[SolvedSimilarProblem])
def get_similar_solved_cases(
    problem: str = Query(..., min_length=3),
    service_code: Optional[str] = Query(None),
    limit: int = Query(3, ge=1, le=10)
):
    sim_service = get_similarity_service()
    return sim_service.search_similar_solved_cases(
        problem_description=problem,
        service_code=service_code,
        limit=limit
    )
