"""
IP-SAKTI Sahayak — Tools API Routes
Includes Formulation Classifier, ABS Helper, and TKDL Prior-Art Pointer.
"""
import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ClassifyRequest, ClassifyFollowupRequest, ClassifyResponse,
    AbsStartRequest, AbsFollowupRequest, AbsResponse,
    TkdlCheckRequest, TkdlCheckResponse
)
from app.services.classifier_service import ClassifierService
from app.services.abs_service import ABSService
from app.services.tkdl_service import TKDLService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tools", tags=["Tools"])

# Global service instances for the tools
abs_service = ABSService()
tkdl_service = TKDLService()


# --- Formulation Classifier ---
@router.post("/classify", response_model=ClassifyResponse)
async def classify_formulation(request: ClassifyRequest):
    try:
        classifier = ClassifierService.get_instance()
        response = classifier.classify(request.description, request.session_id)
        return response
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Error classifying formulation: {str(e)}")


@router.post("/classify/followup", response_model=ClassifyResponse)
async def classify_followup(request: ClassifyFollowupRequest):
    try:
        classifier = ClassifierService.get_instance()
        response = classifier.followup(request.response, request.session_id)
        return response
    except Exception as e:
        logger.error(f"Classification followup error: {e}")
        raise HTTPException(status_code=500, detail=f"Error in classification follow-up: {str(e)}")


# --- ABS Helper ---
@router.post("/abs-check", response_model=AbsResponse)
async def start_abs_check(request: AbsStartRequest):
    try:
        # We allow session_id in request to restart or continue if needed, but for simplicity:
        response = abs_service.start_assessment()
        return response
    except Exception as e:
        logger.error(f"ABS start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/abs-check/followup", response_model=AbsResponse)
async def abs_followup(request: AbsFollowupRequest):
    try:
        response = abs_service.process_followup(request.session_id, request.response)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"ABS followup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- TKDL Prior-Art Pointer ---
@router.post("/tkdl-check", response_model=TkdlCheckResponse)
async def tkdl_check(request: TkdlCheckRequest):
    try:
        response = tkdl_service.check_prior_art(request.ingredients, request.indication)
        return response
    except Exception as e:
        logger.error(f"TKDL check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
