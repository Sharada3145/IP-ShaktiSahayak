# IP-SAKTI Sahayak — Phase 2 Task Tracker

## Backend: New Services
- [x] `app/services/abs_service.py` — ABS decision tree logic
- [x] `app/services/tkdl_service.py` — TKDL dictionary and prior-art checking logic

## Backend: API Updates
- [x] Rename/refactor `app/api/routes/classify.py` to `app/api/routes/tools.py`
- [x] Add `POST /api/tools/abs-check` endpoint
- [x] Add `POST /api/tools/tkdl-check` endpoint
- [x] Update `app/main.py` router registration
- [ ] Enhance `app/services/rag_service.py` (cross-validation and confidence scoring)
- [x] Update `app/models/schemas.py` for new tools

## Frontend: ABS Helper
- [x] `src/app/abs-helper/page.js` — Interactive wizard UI
- [x] `src/app/abs-helper/abs.css` — Styles

## Frontend: TKDL Pointer
- [x] `src/app/tkdl-check/page.js` — Formulation input & results UI
- [x] `src/app/tkdl-check/tkdl.css` — Styles

## Frontend: Integration
- [x] Update `src/app/layout.js` navigation links
- [x] Verify full flow locally
