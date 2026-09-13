from typing import Dict, List, Any

class TKDLService:
    """
    Mock service to simulate Traditional Knowledge Digital Library (TKDL) Prior-Art Checking.
    In a real-world scenario, this would interface securely with the TKDL database or rely 
    on publicly available digitized classical texts.
    """
    
    def __init__(self):
        # A mock dictionary of common Ayurvedic botanicals and their known classical indications
        # used as defensive prior art against Section 3(p) patents.
        self.tk_database = {
            "curcuma longa": ["wound healing", "anti-inflammatory", "skin diseases", "turmeric"],
            "haldi": ["wound healing", "anti-inflammatory", "skin diseases", "turmeric"],
            "azadirachta indica": ["anti-bacterial", "skin infections", "fever", "neem"],
            "neem": ["anti-bacterial", "skin infections", "fever", "azadirachta indica"],
            "withania somnifera": ["stress", "vitality", "immunomodulator", "ashwagandha"],
            "ashwagandha": ["stress", "vitality", "immunomodulator", "withania somnifera"],
            "bacopa monnieri": ["memory", "cognitive enhancement", "brahmi"],
            "brahmi": ["memory", "cognitive enhancement", "bacopa monnieri"],
            "zingiber officinale": ["digestion", "cold", "cough", "ginger", "sunthi"],
            "ginger": ["digestion", "cold", "cough", "zingiber officinale"],
            "glycyrrhiza glabra": ["cough", "throat", "ulcers", "licorice", "yashtimadhu"]
        }

    def check_prior_art(self, ingredients: List[str], indication: str) -> Dict[str, Any]:
        """
        Check if the provided ingredients and indication match known traditional knowledge.
        """
        findings = []
        is_prior_art = False
        
        # Normalize indication for simple matching
        ind_lower = indication.lower()
        
        for ingredient in ingredients:
            ing_lower = ingredient.lower().strip()
            
            # Check if ingredient is in our mock TK database
            if ing_lower in self.tk_database:
                known_indications = self.tk_database[ing_lower]
                
                # Check if the user's indication overlaps with known indications
                match_found = any(known in ind_lower for known in known_indications)
                
                if match_found:
                    is_prior_art = True
                    findings.append({
                        "ingredient": ingredient,
                        "known_indications": known_indications,
                        "match_status": "Direct Match",
                        "description": f"The use of {ingredient} for {indication} is documented in traditional texts."
                    })
                else:
                    findings.append({
                        "ingredient": ingredient,
                        "known_indications": known_indications,
                        "match_status": "Partial/Novel Use",
                        "description": f"{ingredient} is documented for {', '.join(known_indications[:3])}, but its use for '{indication}' may be considered novel."
                    })
            else:
                findings.append({
                    "ingredient": ingredient,
                    "match_status": "No Traditional Record Found",
                    "description": f"This ingredient is not found in our simplified TKDL mock database."
                })

        # Determine Section 3(p) risk
        if is_prior_art and len(ingredients) > 1:
            risk_level = "HIGH"
            advice = "This formulation is highly likely to face rejection under Section 3(p) of the Patents Act, 1970, as it represents a mere admixture of known traditional ingredients for their known properties."
        elif is_prior_art:
            risk_level = "HIGH"
            advice = "This single ingredient's use is well-documented. You cannot patent it unless you demonstrate a synergistic extraction method or a completely novel formulation delivery system."
        else:
            risk_level = "LOW/MEDIUM"
            advice = "No direct traditional knowledge prior-art match found for this specific indication. Ensure you have clinical data to prove enhanced efficacy or synergism to overcome potential Section 3(d) or 3(p) objections."

        return {
            "ingredients_analyzed": len(ingredients),
            "findings": findings,
            "section_3p_risk": risk_level,
            "strategic_advice": advice,
            "disclaimer": "This is a simulated prior-art check against a limited mock database. For actual patent filing, a comprehensive search of the official TKDL and other databases by a registered patent agent is required."
        }
