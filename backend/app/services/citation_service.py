"""
IP-SAKTI Sahayak — Citation Extraction Service
"""
import re
from typing import Optional
import logging

from app.models.schemas import Citation, Jurisdiction, Confidence

logger = logging.getLogger(__name__)

# Known statutes and treaties for citation validation
INDIA_STATUTES = {
    "patents act": "Patents Act, 1970",
    "patent act": "Patents Act, 1970",
    "patents rules": "Patents Rules, 2024",
    "biological diversity act": "Biological Diversity Act, 2002",
    "biodiversity act": "Biological Diversity Act, 2002",
    "biodiversity rules": "Biological Diversity Rules, 2024",
    "drugs and cosmetics act": "Drugs and Cosmetics Act, 1940",
    "drugs & cosmetics act": "Drugs and Cosmetics Act, 1940",
    "d&c act": "Drugs and Cosmetics Act, 1940",
    "geographical indications": "Geographical Indications of Goods Act, 1999",
    "gi act": "Geographical Indications of Goods Act, 1999",
    "trade marks act": "Trade Marks Act, 1999",
    "trademarks act": "Trade Marks Act, 1999",
    "trademark act": "Trade Marks Act, 1999",
    "copyright act": "Copyright Act, 1957",
    "designs act": "Designs Act, 2000",
    "plant variety": "Protection of Plant Varieties and Farmers' Rights Act, 2001",
    "pvp act": "Protection of Plant Varieties and Farmers' Rights Act, 2001",
    "fssai": "FSSAI Ayurveda-Aahar Regulations",
    "drugs and magic remedies": "Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954",
    "dmr act": "Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954",
    "tkdl": "Traditional Knowledge Digital Library",
    "dpdp act": "Digital Personal Data Protection Act, 2023",
}

INTERNATIONAL_TREATIES = {
    "trips": "TRIPS Agreement",
    "cbd": "Convention on Biological Diversity",
    "convention on biological diversity": "Convention on Biological Diversity",
    "nagoya protocol": "Nagoya Protocol",
    "nagoya": "Nagoya Protocol",
    "wipo gratk": "WIPO GRATK Treaty, 2024",
    "gratk": "WIPO GRATK Treaty, 2024",
    "pct": "Patent Cooperation Treaty",
    "patent cooperation treaty": "Patent Cooperation Treaty",
    "madrid": "Madrid System for International Trademark Registration",
    "madrid system": "Madrid System for International Trademark Registration",
    "hague": "Hague System for International Design Registration",
    "hague system": "Hague System for International Design Registration",
    "budapest treaty": "Budapest Treaty for Deposit of Microorganisms",
    "budapest": "Budapest Treaty for Deposit of Microorganisms",
}


class CitationService:
    """Extracts and validates citations from LLM responses."""
    
    def extract_citations(
        self,
        answer_text: str,
        source_metadatas: list[dict],
        jurisdiction: Jurisdiction
    ) -> list[Citation]:
        """
        Extract citations from the LLM answer text and validate against source metadata.
        
        Strategy:
        1. Parse the answer for statute/treaty references
        2. Match against known statutes/treaties
        3. Cross-reference with the source documents actually retrieved
        4. Assign confidence based on match quality
        """
        citations = []
        seen_sources = set()
        
        # First, create citations from the retrieved source metadata
        for meta in source_metadatas:
            title = meta.get("title", "Unknown Source")
            section = meta.get("section", None)
            source_key = f"{title}:{section}"
            
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                citations.append(Citation(
                    source_title=title,
                    section=section,
                    jurisdiction=jurisdiction,
                    confidence=Confidence.HIGH,
                    source_url=meta.get("official_source", None),
                    document_id=meta.get("doc_id", None)
                ))
        
        # Then, parse the answer text for additional statute/treaty references
        text_citations = self._parse_text_citations(answer_text, jurisdiction)
        for tc in text_citations:
            source_key = f"{tc.source_title}:{tc.section}"
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                citations.append(tc)
        
        return citations[:10]  # Cap at 10 citations
    
    def _parse_text_citations(self, text: str, jurisdiction: Jurisdiction) -> list[Citation]:
        """Parse the answer text for statutory and treaty references."""
        citations = []
        
        # Pattern for "Section X of the Act Name" or "Article X of Treaty"
        section_patterns = [
            r"[Ss]ection\s+(\d+[\w()]*)\s+of\s+(?:the\s+)?(.+?)(?:\.|,|\n|;)",
            r"[Rr]ule\s+(\d+[\w()]*)\s+of\s+(?:the\s+)?(.+?)(?:\.|,|\n|;)",
            r"[Aa]rticle\s+(\d+[\w()]*)\s+of\s+(?:the\s+)?(.+?)(?:\.|,|\n|;)",
        ]
        
        reference_db = (
            INDIA_STATUTES if jurisdiction == Jurisdiction.INDIA
            else INTERNATIONAL_TREATIES
        )
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                section_num = match.group(1).strip()
                act_name_raw = match.group(2).strip()
                
                # Try to match against known statutes/treaties
                matched_name = self._match_known_source(act_name_raw, reference_db)
                
                if matched_name:
                    citations.append(Citation(
                        source_title=matched_name,
                        section=section_num,
                        jurisdiction=jurisdiction,
                        confidence=Confidence.HIGH
                    ))
                else:
                    # Use the raw name but with lower confidence
                    citations.append(Citation(
                        source_title=act_name_raw,
                        section=section_num,
                        jurisdiction=jurisdiction,
                        confidence=Confidence.MEDIUM
                    ))
        
        return citations
    
    def _match_known_source(self, raw_name: str, reference_db: dict) -> Optional[str]:
        """Match a raw statute/treaty name against known references."""
        raw_lower = raw_name.lower().strip()
        
        # Direct match
        if raw_lower in reference_db:
            return reference_db[raw_lower]
        
        # Substring match
        for key, value in reference_db.items():
            if key in raw_lower or raw_lower in key:
                return value
        
        # Fuzzy match: check if significant words match
        raw_words = set(raw_lower.split())
        for key, value in reference_db.items():
            key_words = set(key.split())
            overlap = raw_words & key_words
            if len(overlap) >= 2 or (len(overlap) >= 1 and len(key_words) == 1):
                return value
        
        return None
