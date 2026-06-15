# Paper 2 Submission Decision Ledger

This ledger separates bounded CES submission readiness, repeat-strengthened CES readiness and CEJ stretch readiness.

- Decision: `repeat_strengthened_ces_ready_after_admin`
- Recommended near-term route: `R02_wait_for_repeat_then_ces`
- Fallback if time-limited: `R01_submit_bounded_ces_after_admin`
- Not recommended now: `R03_cej_stretch`
- Boundary: Decision ledger organizes current evidence and blockers; it does not create new DEM, pressure-flow or submission evidence.

| Route | Current decision | Scientific status | Admin status | Current blocker | Next action |
|---|---|---|---|---|---|
| Chemical Engineering Science bounded mechanism paper | not_ready_admin_only | bounded_supported | open_admin_blockers=5 | administrative confirmations and public repository DOI | Resolve repository DOI/accession and author metadata; repeat-seed uncertainty is now available. |
| Chemical Engineering Science with repeat-seed uncertainty | not_ready_admin_only_repeat_evidence_available | repeat=production_repeat_runs_completed; production_completed=2; formal_processed=3; running=0 | open_admin_blockers=5 | administrative confirmations and public repository DOI | Resolve admin metadata and keep repeat wording bounded to stochastic variability. |
| Chemical Engineering Journal stretch route | do_not_submit_current_version | pressure_evidence_available | open_admin_blockers=5 | validation-grade flow or experimental evidence missing | Do not target CEJ until pressure-flow evidence is upgraded beyond bounded cropped-domain screening. |

## Go/No-Go Rules

### R01_submit_bounded_ces_after_admin: Chemical Engineering Science bounded mechanism paper

- Go: All admin blockers resolved; manuscript keeps pressure-free and pre-clogging boundaries.
- No-go: Any declaration, repository DOI or corresponding-author metadata remains unconfirmed.
- Evidence state: argument_map=pass; gate=not_ready_for_submission; top_gaps=[]

### R02_wait_for_repeat_then_ces: Chemical Engineering Science with repeat-seed uncertainty

- Go: Final restart files exist, protected pipeline post-processes full dumps, and uncertainty can be inserted without changing claims.
- No-go: Repeat runs fail, remain incomplete or contradict the current near-threshold mechanism.
- Evidence state: top_action=submission_admin_gate; repeat_running=0; production_completed=2; formal_processed=3

### R03_cej_stretch: Chemical Engineering Journal stretch route

- Go: Validation-grade OpenFOAM/OpenLB/LBM or experimental pressure evidence supports process-performance claims and repeat uncertainty is available.
- No-go: Only bounded cropped-domain pressure checks are available, or repeat evidence remains unavailable.
- Evidence state: valid_pressure_cases=3; pressure_ready=True; formal_processed=3
