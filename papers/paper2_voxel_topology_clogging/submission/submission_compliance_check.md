# Paper 2 Submission Compliance Check

Decision: `not_ready_for_submission_form_entry`

Summary: `{"blocker": 7, "pass": 8, "warning": 2}`

| Item | Category | Status | Evidence |
|---|---|---|---|
| title | submission_form | pass | `submission_form_packet.json` |
| abstract | submission_form | pass | `submission_form_packet.json` |
| authors_and_affiliations | submission_form | pass | `submission_form_packet.json` |
| keywords | submission_form | pass | `submission_form_packet.json` |
| highlights | elsevier_artifact | pass | `submission_form_packet.json` |
| graphical_abstract | elsevier_artifact | pass | `submission_form_packet.json` |
| required_metadata_confirmations | administrative | blocker | `submission_metadata_gaps.json` |
| optional_metadata_confirmations | administrative | warning | `submission_metadata_gaps.json` |
| metadata_repository | administrative | blocker | `submission_metadata.yaml` |
| metadata_funding | administrative | blocker | `submission_metadata.yaml` |
| metadata_competing_interests | administrative | blocker | `submission_metadata.yaml` |
| metadata_acknowledgements | administrative | blocker | `submission_metadata.yaml` |
| metadata_corresponding_author | administrative | blocker | `submission_metadata.yaml` |
| upload_files | package | pass | `final_submission_gate.json` |
| final_gate_status | gate | blocker | `final_submission_gate.json` |
| scientific_scope_warnings | scope | warning | `final_submission_gate.json` |
| unresolved_reviewer_risks | scope | pass | `final_submission_gate.json` |

## Interpretation

- `pass`: the checked submission item is ready.
- `warning`: the item is acceptable only if the manuscript remains bounded to the current scope or if the journal does not require the optional metadata.
- `blocker`: the item must be resolved before actual submission.
