"""
IP-SAKTI Sahayak — Pydantic Models / Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime


# --- Enums ---

class Jurisdiction(str, Enum):
    INDIA = "india"
    INTERNATIONAL = "international"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FormulationCategory(str, Enum):
    CLASSICAL = "classical"
    PROPRIETARY = "proprietary"
    NEW_DRUG = "new_drug"
    PHYTOPHARMACEUTICAL = "phytopharmaceutical"
    NUTRACEUTICAL = "nutraceutical"
    COSMETIC = "cosmetic"


# --- Request Models ---

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000, description="User's IP/regulatory question")
    jurisdiction: Jurisdiction = Field(default=Jurisdiction.INDIA, description="Jurisdiction scope")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    language: str = Field(default="en", description="Response language code")


class ClassifyRequest(BaseModel):
    description: str = Field(..., min_length=10, max_length=3000, description="Product/formulation description")
    session_id: Optional[str] = Field(default=None, description="Session ID for multi-turn classification")


class ClassifyFollowupRequest(BaseModel):
    response: str = Field(..., min_length=1, max_length=2000, description="User's response to clarifying questions")
    session_id: str = Field(..., description="Session ID from initial classification")


# --- Response Models ---

class Citation(BaseModel):
    source_title: str = Field(..., description="Title of the cited document")
    section: Optional[str] = Field(default=None, description="Specific section, article, or rule number")
    jurisdiction: Jurisdiction
    confidence: Confidence = Field(default=Confidence.MEDIUM)
    source_url: Optional[str] = Field(default=None, description="URL to official source if available")
    document_id: Optional[str] = Field(default=None, description="Internal corpus document ID")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="The RAG-generated answer with inline citations")
    citations: list[Citation] = Field(default_factory=list, description="Structured citation list")
    confidence: Confidence = Field(default=Confidence.MEDIUM, description="Overall answer confidence")
    jurisdiction: Jurisdiction
    related_queries: list[str] = Field(default_factory=list, description="Suggested follow-up questions")
    disclaimer: str = Field(
        default="⚖️ This is information only, not legal advice. Please consult a qualified IP attorney for specific legal decisions.",
        description="Legal disclaimer"
    )
    session_id: str = Field(default="", description="Session ID for conversation continuity")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ClassifyResponse(BaseModel):
    category: Optional[FormulationCategory] = Field(default=None, description="Classification result (null if still classifying)")
    category_label: Optional[str] = Field(default=None, description="Human-readable category label")
    message: str = Field(..., description="Classification result or clarifying questions")
    ip_implications: Optional[list[str]] = Field(default=None, description="IP protection options for this category")
    regulatory_requirements: Optional[list[str]] = Field(default=None, description="Regulatory requirements")
    relevant_statutes: Optional[list[str]] = Field(default=None, description="Applicable statutes and rules")
    abs_implications: Optional[str] = Field(default=None, description="ABS compliance notes")
    is_complete: bool = Field(default=False, description="Whether classification is complete")
    session_id: str = Field(default="", description="Session ID for follow-up")
    disclaimer: str = Field(
        default="⚖️ This is information only, not legal advice. Please consult a qualified IP attorney for specific legal decisions.",
    )


class SourceDocument(BaseModel):
    id: str
    title: str
    jurisdiction: Jurisdiction
    category: str
    statute_type: str
    last_amended: Optional[str] = None
    official_source: Optional[str] = None
    sections_covered: list[str] = Field(default_factory=list)
    content_preview: Optional[str] = None


class SourceListResponse(BaseModel):
    sources: list[SourceDocument]
    total: int
    jurisdiction_filter: Optional[Jurisdiction] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    corpus_documents: int = 0
    vector_store_ready: bool = False
    llm_ready: bool = False

# --- ABS Models ---

class AbsStartRequest(BaseModel):
    session_id: Optional[str] = None

class AbsFollowupRequest(BaseModel):
    response: str
    session_id: str

class AbsResponse(BaseModel):
    session_id: str
    is_complete: bool
    message: Optional[str] = None
    options: Optional[list[str]] = None
    requirement: Optional[str] = None
    forms_required: Optional[list[str]] = None
    benefit_sharing: Optional[str] = None
    is_exempt: Optional[bool] = None
    summary: Optional[str] = None
    disclaimer: Optional[str] = None

# --- TKDL Models ---

class TkdlCheckRequest(BaseModel):
    ingredients: list[str]
    indication: str

class TkdlFinding(BaseModel):
    ingredient: str
    match_status: str
    description: str
    known_indications: Optional[list[str]] = None

class TkdlCheckResponse(BaseModel):
    ingredients_analyzed: int
    findings: list[TkdlFinding]
    section_3p_risk: str
    strategic_advice: str
    disclaimer: str
