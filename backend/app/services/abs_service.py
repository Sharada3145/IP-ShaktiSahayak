from typing import Dict, Any, List

class ABSService:
    """
    Handles logic for Access and Benefit-Sharing (ABS) compliance based on the 
    Biological Diversity Act, 2002 and its 2023 Amendments.
    """
    
    def __init__(self):
        # In a real system, this state might be backed by a DB or cache
        self._abs_sessions: Dict[str, Dict[str, Any]] = {}

    def start_assessment(self) -> Dict[str, Any]:
        """Start a new ABS assessment session."""
        import uuid
        session_id = str(uuid.uuid4())
        
        self._abs_sessions[session_id] = {
            "step": "identity",
            "answers": {}
        }
        
        return {
            "session_id": session_id,
            "message": "Are you an Indian citizen, a Foreign entity/Non-Resident Indian (NRI), or an Indian corporate entity?",
            "options": ["Indian Citizen", "Foreign Entity / NRI", "Indian Corporate Entity"],
            "is_complete": False
        }

    def process_followup(self, session_id: str, response: str) -> Dict[str, Any]:
        """Process user answers through the ABS decision tree."""
        if session_id not in self._abs_sessions:
            raise ValueError("Invalid or expired session ID")
            
        session = self._abs_sessions[session_id]
        step = session["step"]
        answers = session["answers"]
        
        # Simple state machine for the wizard
        if step == "identity":
            answers["identity"] = response.lower()
            session["step"] = "resource_type"
            return {
                "session_id": session_id,
                "message": "Does your product use codified traditional knowledge (e.g., from an authoritative Ayurvedic text) or uncodified biological resources?",
                "options": ["Codified Traditional Knowledge", "Uncodified Biological Resources"],
                "is_complete": False
            }
            
        elif step == "resource_type":
            answers["resource_type"] = response.lower()
            session["step"] = "purpose"
            return {
                "session_id": session_id,
                "message": "What is the primary purpose of your activity?",
                "options": ["Commercial Utilization", "Research / Bio-survey", "Applying for IP/Patent"],
                "is_complete": False
            }
            
        elif step == "purpose":
            answers["purpose"] = response.lower()
            
            # If Indian identity and commercial use, check for practitioner exemption
            if "indian" in answers["identity"] and "commercial" in answers["purpose"]:
                session["step"] = "practitioner"
                return {
                    "session_id": session_id,
                    "message": "Are you a registered AYUSH practitioner, a local community member, or a commercial manufacturer?",
                    "options": ["Registered Practitioner", "Local Community Member", "Commercial Manufacturer"],
                    "is_complete": False
                }
            else:
                # Skip practitioner check for foreigners or non-commercial
                return self._finalize_assessment(session_id, answers)
                
        elif step == "practitioner":
            answers["practitioner"] = response.lower()
            return self._finalize_assessment(session_id, answers)

    def _finalize_assessment(self, session_id: str, answers: Dict[str, str]) -> Dict[str, Any]:
        """Evaluate the collected answers and generate compliance requirements."""
        
        requirement = "Prior Approval from National Biodiversity Authority (NBA)"
        forms = ["Form 1"]
        exemption = False
        benefit_sharing = "Mandatory (typically 0.1% to 0.5% of ex-factory gross sales, or upfront payment)"
        
        # 1. Identity Check
        is_foreign = "foreign" in answers["identity"]
        
        # 2. Practitioner Exemption (Section 7 exception)
        if "practitioner" in answers:
            if "practitioner" in answers["practitioner"] or "community" in answers["practitioner"]:
                exemption = True
                requirement = "Exempt under Section 7 of the BD Act (2023 Amendment)"
                forms = []
                benefit_sharing = "Not applicable for practitioners/communities using resources for local practice."
                
        # 3. Codified TK Exemption (2023 Amendment)
        if "codified" in answers["resource_type"] and not is_foreign and not exemption:
            exemption = True
            requirement = "Exempt under the 2023 Amendment for Indians using Codified Traditional Knowledge."
            forms = []
            benefit_sharing = "Not applicable due to codified TK exemption for Indian entities."
            
        # 4. Indian Commercial (Section 7 - Prior Intimation)
        if not is_foreign and not exemption and "commercial" in answers["purpose"]:
            requirement = "Prior Intimation to State Biodiversity Board (SBB)"
            forms = ["Form A (State specific)"]
            
        # 5. IPR Application (Section 6)
        if "ip" in answers["purpose"] or "patent" in answers["purpose"]:
            requirement = "Prior Approval from NBA is required before the grant of the IPR."
            forms = ["Form 3"]
            exemption = False  # IPR generally overrides exemptions
            
        result = {
            "session_id": session_id,
            "is_complete": True,
            "requirement": requirement,
            "forms_required": forms,
            "benefit_sharing": benefit_sharing,
            "is_exempt": exemption,
            "summary": self._generate_summary(answers, exemption, requirement),
            "disclaimer": "This is a preliminary assessment. ABS compliance can be highly specific to exact botanical sourcing. Consult the NBA guidelines or a legal expert."
        }
        
        # Clean up session
        del self._abs_sessions[session_id]
        return result
        
    def _generate_summary(self, answers: Dict[str, str], is_exempt: bool, req: str) -> str:
        ident = answers.get("identity", "entity")
        purp = answers.get("purpose", "activity")
        if is_exempt:
            return f"As an {ident} engaged in {purp}, you are likely exempt from standard ABS approval processes, but you must still adhere to sustainable harvesting guidelines."
        else:
            return f"As an {ident} engaged in {purp}, you are subject to the Biological Diversity Act and must secure {req} before proceeding."
