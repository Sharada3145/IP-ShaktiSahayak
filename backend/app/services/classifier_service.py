"""
IP-SAKTI Sahayak — Formulation Classifier Service
"""
import uuid
import logging
from typing import Optional

from app.services.llm_service import LLMService
from app.core.prompts import (
    CLASSIFIER_SYSTEM_PROMPT,
    CLASSIFIER_INITIAL_PROMPT,
    CLASSIFIER_FOLLOWUP_PROMPT
)
from app.models.schemas import ClassifyResponse, FormulationCategory

logger = logging.getLogger(__name__)

# In-memory session storage for multi-turn classification
# In production, use Redis or a database
_classification_sessions: dict[str, list[dict]] = {}

CATEGORY_LABELS = {
    FormulationCategory.CLASSICAL: "Classical / Generic Ayurvedic Medicine",
    FormulationCategory.PROPRIETARY: "Patent / Proprietary Ayurvedic Medicine",
    FormulationCategory.NEW_DRUG: "New Drug / Non-classical Formulation",
    FormulationCategory.PHYTOPHARMACEUTICAL: "Phytopharmaceutical",
    FormulationCategory.NUTRACEUTICAL: "Ayurveda-Aahar / Nutraceutical",
    FormulationCategory.COSMETIC: "Cosmetic with Ayurvedic Claims",
}

# Keywords to detect classification in LLM response
CATEGORY_KEYWORDS = {
    FormulationCategory.CLASSICAL: ["classical", "generic medicine", "first schedule", "classical medicine", "charaka samhita", "sushruta samhita"],
    FormulationCategory.PROPRIETARY: ["proprietary", "patent medicine", "branded", "proprietary medicine"],
    FormulationCategory.NEW_DRUG: ["new drug", "non-classical", "novel formulation", "clinical trial"],
    FormulationCategory.PHYTOPHARMACEUTICAL: ["phytopharmaceutical", "purified extract", "standardized extract", "plant extract"],
    FormulationCategory.NUTRACEUTICAL: ["nutraceutical", "ayurveda-aahar", "food supplement", "dietary supplement", "aahar"],
    FormulationCategory.COSMETIC: ["cosmetic", "beautification", "personal care", "skin care", "cosmetic product"],
}


class ClassifierService:
    """Formulation Classification Service — classifies Ayurvedic products into regulatory categories."""
    
    _instance: Optional["ClassifierService"] = None
    
    def __init__(self):
        self.llm_service = LLMService.get_instance()
        logger.info("ClassifierService initialized")
    
    @classmethod
    def get_instance(cls) -> "ClassifierService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def classify(self, description: str, session_id: Optional[str] = None) -> ClassifyResponse:
        """Start or continue a formulation classification."""
        session_id = session_id or str(uuid.uuid4())
        
        # Build prompt
        user_prompt = CLASSIFIER_INITIAL_PROMPT.format(description=description)
        
        # Generate response
        response_text = self.llm_service.generate(CLASSIFIER_SYSTEM_PROMPT, user_prompt)
        
        # Store session
        _classification_sessions[session_id] = [
            {"role": "user", "content": f"Product description: {description}"},
            {"role": "assistant", "content": response_text}
        ]
        
        # Try to detect if classification is complete
        detected_category = self._detect_category(response_text)
        
        if detected_category:
            return self._build_complete_response(detected_category, response_text, session_id)
        else:
            return ClassifyResponse(
                message=response_text,
                is_complete=False,
                session_id=session_id
            )
    
    def followup(self, response: str, session_id: str) -> ClassifyResponse:
        """Handle a follow-up response in a multi-turn classification."""
        if session_id not in _classification_sessions:
            return ClassifyResponse(
                message="Session not found. Please start a new classification.",
                is_complete=False,
                session_id=session_id
            )
        
        # Get conversation history
        history = _classification_sessions[session_id]
        conversation_history = "\n".join(
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in history
        )
        
        # Build followup prompt
        user_prompt = CLASSIFIER_FOLLOWUP_PROMPT.format(
            conversation_history=conversation_history,
            response=response
        )
        
        # Generate response
        response_text = self.llm_service.generate(CLASSIFIER_SYSTEM_PROMPT, user_prompt)
        
        # Update session
        history.append({"role": "user", "content": response})
        history.append({"role": "assistant", "content": response_text})
        _classification_sessions[session_id] = history
        
        # Try to detect if classification is complete
        detected_category = self._detect_category(response_text)
        
        if detected_category:
            return self._build_complete_response(detected_category, response_text, session_id)
        else:
            return ClassifyResponse(
                message=response_text,
                is_complete=False,
                session_id=session_id
            )
    
    def _detect_category(self, response_text: str) -> Optional[FormulationCategory]:
        """Detect if the LLM response contains a definitive classification."""
        text_lower = response_text.lower()
        
        # Check for classification indicators
        classification_indicators = [
            "classified as", "falls under", "categorized as", "category:",
            "classification:", "this product is a", "this formulation is a",
            "your product is", "your formulation is"
        ]
        
        has_classification = any(indicator in text_lower for indicator in classification_indicators)
        
        if not has_classification:
            return None
        
        # Score each category
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def _build_complete_response(
        self, category: FormulationCategory, response_text: str, session_id: str
    ) -> ClassifyResponse:
        """Build a complete classification response with IP implications."""
        
        ip_map = {
            FormulationCategory.CLASSICAL: [
                "Section 3(p) of Patents Act bars patenting of traditional knowledge",
                "TKDL provides defensive protection against misappropriation",
                "Geographical Indication (GI) potential for region-specific preparations",
                "Trademark registration for brand differentiation",
                "Copyright protection for unique text/labeling"
            ],
            FormulationCategory.PROPRIETARY: [
                "Trademark registration is the primary IP tool",
                "Trade secret protection for proprietary formulation",
                "Patent possible if novel process or composition demonstrated",
                "Design registration for unique packaging",
                "Copyright for original marketing materials"
            ],
            FormulationCategory.NEW_DRUG: [
                "HIGH patent potential — novel composition, process, or use",
                "Clinical trial data is a valuable IP asset (data exclusivity)",
                "ABS compliance under Biological Diversity Act is CRITICAL",
                "PCT filing for international patent protection",
                "Trade secret for manufacturing process know-how"
            ],
            FormulationCategory.PHYTOPHARMACEUTICAL: [
                "Patent possible for extraction process and standardized composition",
                "Budapest Treaty for microorganism/cell line deposits",
                "ABS compliance MANDATORY for biological resources used",
                "Plant variety protection if novel cultivar developed",
                "Trade secret for extraction and standardization processes"
            ],
            FormulationCategory.NUTRACEUTICAL: [
                "Trademark registration is primary IP strategy",
                "Limited patent scope (composition claims may face prior art)",
                "FSSAI registration and compliance required",
                "Design registration for unique packaging",
                "Advertising restrictions under DMR Act apply"
            ],
            FormulationCategory.COSMETIC: [
                "Trademark and design registration are primary IP tools",
                "Trade secret for formulation composition",
                "Patent possible for novel delivery systems or processes",
                "D&C Act cosmetic license required",
                "Advertising claims must comply with DMR Act"
            ],
        }
        
        regulatory_map = {
            FormulationCategory.CLASSICAL: [
                "Licensed under D&C Act Rule 158B",
                "No clinical trials needed — traditional use evidence sufficient",
                "Must conform to standards in Ayurvedic Pharmacopoeia of India",
                "GMP compliance under Schedule T mandatory",
                "Labeling as per D&C Rules"
            ],
            FormulationCategory.PROPRIETARY: [
                "Licensed under D&C Act Rule 158C",
                "155-year traditional use evidence OR limited safety data",
                "Must declare all ingredients on label",
                "GMP compliance under Schedule T",
                "State licensing authority approval"
            ],
            FormulationCategory.NEW_DRUG: [
                "Requires clinical trials under Rule 170 of D&C Rules",
                "Clinical Trial Registry-India (CTRI) registration mandatory",
                "Phase I-III clinical trials required",
                "CDSCO approval needed",
                "Post-marketing surveillance required"
            ],
            FormulationCategory.PHYTOPHARMACEUTICAL: [
                "New drug pathway under D&C Act",
                "Requires safety and efficacy data",
                "Standardization and quality control mandatory",
                "GMP compliance required",
                "CDSCO approval needed"
            ],
            FormulationCategory.NUTRACEUTICAL: [
                "FSSAI licensing and registration",
                "Ayurveda-Aahar regulations compliance",
                "Cannot make therapeutic/disease claims",
                "Labeling as per FSSAI requirements",
                "Advertising restrictions apply"
            ],
            FormulationCategory.COSMETIC: [
                "D&C Act cosmetic license from State authority",
                "BIS standards compliance where applicable",
                "Ingredient safety assessment",
                "Labeling as per Cosmetics Rules",
                "No therapeutic claims permitted"
            ],
        }
        
        statutes_map = {
            FormulationCategory.CLASSICAL: [
                "Patents Act, 1970 — Section 3(p)",
                "D&C Act, 1940 — Rule 158B",
                "GI Act, 1999",
                "Trade Marks Act, 1999"
            ],
            FormulationCategory.PROPRIETARY: [
                "D&C Act, 1940 — Rule 158C",
                "Trade Marks Act, 1999",
                "Patents Act, 1970",
                "Copyright Act, 1957"
            ],
            FormulationCategory.NEW_DRUG: [
                "D&C Act, 1940 — Rule 170",
                "Patents Act, 1970",
                "Biological Diversity Act, 2002",
                "Biological Diversity Rules, 2024"
            ],
            FormulationCategory.PHYTOPHARMACEUTICAL: [
                "D&C Act, 1940",
                "Patents Act, 1970",
                "Biological Diversity Act, 2002",
                "Budapest Treaty"
            ],
            FormulationCategory.NUTRACEUTICAL: [
                "FSSAI Ayurveda-Aahar Regulations",
                "Trade Marks Act, 1999",
                "DMR Act, 1954",
                "FSSA Act, 2006"
            ],
            FormulationCategory.COSMETIC: [
                "D&C Act, 1940 — Cosmetics Rules",
                "Trade Marks Act, 1999",
                "Designs Act, 2000",
                "DMR Act, 1954"
            ],
        }
        
        abs_map = {
            FormulationCategory.CLASSICAL: "Generally lower ABS risk for well-documented classical formulations, but check if specific biological resources require NBA approval under Biological Diversity Act, 2002.",
            FormulationCategory.PROPRIETARY: "ABS compliance required if using biological resources. Check NBA/SBB requirements under Biological Diversity Act, 2002 (amended 2023).",
            FormulationCategory.NEW_DRUG: "ABS compliance is CRITICAL. Prior approval from National Biodiversity Authority (NBA) likely required for commercial use of biological resources. Benefit-sharing obligations apply.",
            FormulationCategory.PHYTOPHARMACEUTICAL: "ABS compliance MANDATORY. NBA approval required for accessing plant genetic resources. Nagoya Protocol obligations for international access.",
            FormulationCategory.NUTRACEUTICAL: "ABS compliance required if using biological resources for commercial purposes. Check Biological Diversity Rules, 2024.",
            FormulationCategory.COSMETIC: "ABS compliance required if using biological resources. Check NBA requirements under the amended Biological Diversity Act.",
        }
        
        # Clean up session
        if session_id in _classification_sessions:
            del _classification_sessions[session_id]
        
        return ClassifyResponse(
            category=category,
            category_label=CATEGORY_LABELS.get(category, str(category)),
            message=response_text,
            ip_implications=ip_map.get(category, []),
            regulatory_requirements=regulatory_map.get(category, []),
            relevant_statutes=statutes_map.get(category, []),
            abs_implications=abs_map.get(category, ""),
            is_complete=True,
            session_id=session_id
        )
