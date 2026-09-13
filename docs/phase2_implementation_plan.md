# IP-SAKTI Sahayak — Phase 2 Implementation Plan

Following the successful completion of the Core MVP (Phase 1), Phase 2 expands the assistant's capabilities with dedicated tools for two of the most critical and complex areas of Ayurvedic IP: **Access and Benefit-Sharing (ABS) Compliance** and **Traditional Knowledge Digital Library (TKDL) Prior-Art Checking**.

---

## Proposed Features

### 1. ABS Compliance Helper
A new dedicated module and UI wizard to help users navigate the Biological Diversity Act, 2002 (as amended in 2023). ABS compliance is mandatory but highly context-dependent.

**Decision Tree Flow:**
1. **User Identity:** Indian citizen vs. Foreign entity vs. Non-Resident Indian
2. **Resource Type:** Codified traditional knowledge vs. Uncodified biological resources
3. **Purpose:** Commercial utilization vs. Research vs. Bio-survey
4. **Profession:** Registered AYUSH practitioner vs. Manufacturer vs. Researcher

**Output:**
- The specific compliance requirement (e.g., *Prior Intimation to State Biodiversity Board* vs. *Prior Approval from National Biodiversity Authority*)
- Required forms (Form 1, Form A, etc.)
- Benefit-sharing obligations (e.g., % of ex-factory sales)
- Exemption status (if applicable under 2023 amendments)

### 2. TKDL Prior-Art Pointer
A tool to help users understand if their formulation might face a Section 3(p) rejection based on existing traditional knowledge.

**Mechanism:**
- User inputs a list of ingredients (e.g., *Curcuma longa, Azadirachta indica*) and intended use.
- The system checks these against a curated dictionary of known classical formulations and TKRC (Traditional Knowledge Resource Classification) concepts.
- **Output:** Identifies if the combination is likely considered "prior art" and advises on the level of inventive modification needed to overcome Section 3(p).

### 3. Advanced Confidence & Hallucination Scoring
Refining the existing RAG confidence metric (which currently relies on vector distance):
- **Cross-Validation Check**: LLM validates its own generated answer against the retrieved chunks before returning it.
- **Granular Scoring**: Confidence will be rated per-citation rather than just an overall score.
- **Strict Abstention Thresholds**: Tighter controls to trigger the "I cannot answer this" fallback for edge-case queries.

---

## Technical Implementation

### Backend Changes (`backend/`)
#### [NEW] `app/services/abs_service.py`
- Implements the ABS decision tree logic based on the 2023 Amendment rules.

#### [NEW] `app/services/tkdl_service.py`
- Implements the TKDL pointer logic.
- Seeds a JSON dictionary of top Ayurvedic botanical names and classical combinations to serve as a mock TKDL reference (since the real TKDL is closed-access).

#### [MODIFY] `app/api/routes/classify.py` → `app/api/routes/tools.py`
- Rename and expand the router to include `/api/tools/abs-check` and `/api/tools/tkdl-check`.

#### [MODIFY] `app/services/rag_service.py`
- Implement the "Self-Correction" prompt layer to validate answers before sending them to the user.

### Frontend Changes (`frontend/`)
#### [NEW] `src/app/abs-helper/page.js`
- Interactive wizard for ABS compliance, similar to the Formulation Classifier.

#### [NEW] `src/app/tkdl-check/page.js`
- Input form for ingredients/botanicals and an analysis results panel.

#### [MODIFY] `src/app/layout.js`
- Update the navigation header to include links to the new tools.

---

## Open Questions for Review

> [!IMPORTANT]
> **1. TKDL Data**: Since the actual TKDL database is restricted to patent offices and not publicly queryable via API, I will build the TKDL Pointer using a curated dictionary of the top 50 most common Ayurvedic botanicals and principles (e.g., Turmeric for wound healing, Neem for antifungal). This will serve as a proof-of-concept for how it would work if connected to the real database. Is this acceptable?

> [!IMPORTANT]
> **2. ABS Workflows**: The 2023 Biological Diversity Amendment introduced significant exemptions for registered AYUSH practitioners and codified traditional knowledge. I will ensure the logic prioritizes these new simplified pathways. Does the Ministry have any specific ABS pain points they want highlighted?

---

## Verification Plan

- **ABS Logic Tests**: Provide 5 different user profiles (e.g., Foreign Pharma Co., Indian AYUSH Startup, Registered Vaidya) and verify the helper routes them to the correct NBA/SBB requirement.
- **TKDL Pointer Tests**: Input known combinations (e.g., Turmeric + Neem for skin) and verify it flags it as potential prior art.
- **UI Verification**: Ensure the new tools match the existing premium glassmorphism design system.
