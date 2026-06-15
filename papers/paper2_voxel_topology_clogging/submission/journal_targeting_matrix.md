# Paper 2 Journal Targeting Matrix

This internal strategy document maps the current Paper 2 evidence package to plausible target journals. It is not a substitute for journal instructions or author confirmation.

## Recommended Route

Working high-target route: **Chemical Engineering Science** as the first-attempt journal, using a mechanism-first packed-bed transport argument and explicit evidence boundaries.

Most realistic fallback route: **Powder Technology** or **Particuology/Advanced Powder Technology** if CES rejects the paper as too particle-technology-specific or too computationally bounded without validation-grade flow evidence.

Evidence-dependent upgrade: **Chemical Engineering Science** is now scientifically plausible as a bounded mechanism paper; the remaining near-term upgrade is administrative/repository readiness, while CEJ/IJMF-style upgrades require validation-grade flow or experimental evidence.

Hold route: **International Journal of Multiphase Flow** should wait for a flow upgrade, because the current gas forcing is one-way Stokes drag and not resolved pore-scale multiphase flow.

Computational route: **Computers & Chemical Engineering** is plausible if the paper is rewritten around a reproducible DEM-to-voxel-to-topology-to-surrogate workflow rather than primarily around one physical case.

Physics route: **Physics of Fluids** becomes plausible only if the manuscript is rewritten around anomalous transport, tailing and topology-response physics rather than fusion application.

Fusion/nuclear routes: **Nuclear Fusion** is a high-risk stretch route that would require a much stronger blanket-performance argument; **Fusion Engineering and Design**, **Nuclear Engineering and Design**, **Nuclear Materials and Energy** and **Transport in Porous Media** are viable if the framing shifts respectively toward blanket engineering, nuclear-engineering risk screening, fusion materials context or porous-media transport.

Not recommended now: **Chemical Engineering Journal** is higher risk for the present evidence package because it would likely need experimental or high-fidelity CFD validation and stronger process-performance claims.

Source-use note: the URLs below are scope-positioning anchors only. Final submission still requires a fresh Guide-for-Authors check for article type, declarations, data policy, graphical abstract, highlights and AI-use disclosure.

## Submission Ladder

| Rank | Route | Decision | Reason |
|---:|---|---|---|
| 1 | Chemical Engineering Science | Primary high-target route for the current manuscript. | Best balance between ambition and fit if the paper is written as a mechanism-first packed-bed transport study. |
| 2 | Chemical Engineering Journal | Stretch route only after stronger validation evidence. | Higher visibility, but the present paper lacks validation-grade pressure-flow or experimental evidence for CEJ-style performance claims. |
| 3 | Particuology | Strong particle-science fallback. | Good fit for DEM-based particulate transport mechanisms without forcing a process-performance claim. |
| 4 | Computers & Chemical Engineering | Alternative if the manuscript is reframed as a computational workflow paper. | The project has a reproducible DEM-to-reconstruction-to-topology-to-surrogate pipeline, but the story must foreground modelling workflow. |
| 5 | Advanced Powder Technology | Solid powder/particle backup. | Natural scope for DEM and packed-particle systems if novelty is framed beyond a single case study. |
| 6 | Fusion Engineering and Design | Application-safe fusion route. | Best nuclear/fusion fit if the paper is rewritten around blanket purge-path risk screening. |
| 7 | Transport in Porous Media | Porous-media route after stronger transport-model framing. | Useful if the paper emphasizes connectivity, BTC tailing and anomalous transport over Li4SiO4 engineering context. |
| 8 | Nuclear Materials and Energy | Fusion-materials backup. | Only use if the breeder-material context becomes central; current evidence is mainly transport and topology. |
| 9 | Nuclear Engineering and Design | Nuclear-engineering backup. | Needs a stronger component-level design and uncertainty discussion than the current mechanism manuscript. |

## Matrix

| Journal | Role | Fit | Scope basis | Best framing | Main risk | Required boundary | Decision |
|---|---|---:|---|---|---|---|---|
| Chemical Engineering Science | ambitious | 4 | Elsevier describes CES as selectively publishing outstanding research founded on the Science of Chemical Engineering. Source: https://shop.elsevier.com/journals/subjects/physical-sciences-and-engineering/chemical-engineering/chemical-engineering-general/chemical-engineering?page=2&type=journals | fundamental fine-particle migration, retention and pore-topology response in packed granular media | pressure response is not validation-grade CFD/LBM/experimental evidence; loading scan is single-seed; source-position/source-inventory law is not fitted | pre-clogging migration/filtering framework; no universal critical transition | first_attempt_with_boundaries |
| International Journal of Multiphase Flow | ambitious_after_flow_upgrade | 3 | Elsevier frames IJMF around mass, momentum and energy exchange among phases, including disperse flows, porous media and granular flows. Source: https://shop.elsevier.com/journals/international-journal-of-multiphase-flow/0301-9322 | gas-driven particulate transport in a connected packed-bed pore skeleton | one-way Stokes drag does not resolve local gas redistribution; no two-way gas-particle coupling | one-way drag model, not resolved pore-scale multiphase flow | hold_until_flow_upgrade |
| Computers & Chemical Engineering | computational_framework_route | 4 | Elsevier positions Computers & Chemical Engineering around modelling, simulation, numerical analysis, optimization, process systems engineering and informatics for chemical-engineering problems. Source: https://shop.elsevier.com/journals/computers-and-chemical-engineering/0098-1354 | an automated DEM-to-voxel-to-topology-to-surrogate workflow for packed-bed debris-transport risk screening | the current manuscript is written as a physical mechanism paper, not yet as a computational-methods paper | computational screening framework, not a validated reactor-design tool | consider_if_reframed_as_computational_workflow |
| Physics of Fluids | physics_upgrade_route | 3 | Physics-route option retained as an internal strategy; current manuscript would need a stronger flow/transport physics rewrite. Source: https://pubs.aip.org/aip/pof | anomalous fine-particle transport, tailing and topology response in a granular pore network | current flow is not resolved; fusion-blanket motivation must be shortened; physics novelty must dominate application narrative | mechanism-first flow/transport physics, not blanket-design validation | consider_only_after_physics_reframing |
| Powder Technology | realistic_fallback | 5 | Elsevier describes Powder Technology as covering wet and dry particulate systems, particle characterization, packing, flow and permeability of particle assemblies. Source: https://shop.elsevier.com/journals/powder-technology/0032-5910 | fine-particle retention, deposition and pore-structure diagnostics in a packed ceramic pebble bed | must avoid implying experimental CT, pressure-calibrated safety limits or critical transition | DEM-based pre-clogging mechanism study | fallback_if_ces_rejects_or_scope_mismatch |
| Particuology | strong_backup | 4 | Elsevier describes Particuology as covering discovery, formulation and engineering of particulate materials, processes and systems, including modelling and particle-fluid systems. Source: https://shop.elsevier.com/journals/particuology/1674-2001 | particle-level transport and retention mechanisms in granular pore networks | fusion-specific motivation may need shortening; topology framework must be tied to particle mechanisms | mechanism-first particle systems paper, not blanket-design validation | backup_after_powder_or_parallel_style_variant |
| Advanced Powder Technology | solid_backup | 4 | The Society of Powder Technology, Japan describes APT as integrating powder and particulate-material science and technology, including DEM/CFD numerical simulation. Source: https://www.sptj.jp/archives/old2023/eng/publication/apt/ | numerical powder/debris transport and retention in a packed bed | needs clear novelty beyond a DEM case study | workflow and mechanism rather than universal scale law | backup |
| Fusion Engineering and Design | application_safe_route | 4 | Elsevier describes FED as devoted to fusion energy technology, including theory, models, methods, designs, blankets, materials, tritium fuel cycle and safety. Source: https://shop.elsevier.com/journals/fusion-engineering-and-design/0920-3796 | fusion blanket ceramic breeder pebble-bed purge-pathway risk screening | less general powder-science impact; current study does not validate a blanket safety limit | numerical screening framework for blanket-relevant mechanisms | safe_fallback_if_particle_journals_reject |
| Nuclear Fusion | high_risk_fusion_stretch | 2 | IOP/IAEA position Nuclear Fusion around fusion plasma physics and fusion technology, including reactor concepts and enabling fusion systems. Source: https://iopscience.iop.org/journal/0029-5515 | blanket-relevant Li4SiO4 breeder-bed purge-path reliability and debris-induced transport risk | the current evidence is a packed-bed DEM transport study and may not be central enough to fusion performance or reactor design | fusion-relevant numerical mechanism study, not a validated blanket performance prediction | do_not_submit_current_version_unless_fusion_argument_is_substantially_upgraded |
| Nuclear Engineering and Design | nuclear_engineering_backup | 3 | Elsevier frames Nuclear Engineering and Design around nuclear-engineering design, safety, analysis and reactor-component studies. Source: https://shop.elsevier.com/journals/nuclear-engineering-and-design/0029-5493 | numerical risk screening for packed breeder-bed purge-path blockage in nuclear fusion blanket components | journal fit is broader nuclear engineering rather than powder transport; fusion blanket specificity must be made practical | screening-level risk metric, not a licensing-grade safety limit | backup_if_nuclear_engineering_framing_is_prioritized |
| Nuclear Materials and Energy | fusion_materials_backup | 3 | Fusion-materials backup retained for Li4SiO4 context, but current evidence is transport/topology rather than material degradation. Source: https://www.sciencedirect.com/journal/nuclear-materials-and-energy | ceramic breeder pebble-bed degradation and debris-transport risk under purge-gas conditions | materials response is not directly modeled; no irradiation, thermal cycling or experimental degradation data | numerical transport and structure-response study, not a materials degradation experiment | backup_if_fusion_materials_framing_is_prioritized |
| Transport in Porous Media | porous_media_backup | 3 | Springer describes the journal as publishing transport phenomena in rigid and deformable porous media, including numerical modelling and packed-bed transport examples. Source: https://link.springer.com/journal/11242/aims-and-scope | breakthrough, retention and connectivity response of fines in a packed granular porous medium | application-specific Li4SiO4 framing should be generalized; current pressure-flow evidence is cropped-domain screening rather than validated permeability data | porous-media transport descriptors, not pressure-calibrated permeability closure | backup_if_porosity_transport_framing_is_emphasized |
| Chemical Engineering Journal | not_recommended_current_version | 2 | High-impact chemical-engineering route retained as a stretch option; current manuscript lacks validation-grade pressure or experimental evidence for CEJ-style performance claims. Source: https://www.sciencedirect.com/journal/chemical-engineering-journal | application-facing particulate transport risk in packed beds | no experiment, no pressure-calibrated performance metric, and limited process-engineering demonstration for CEJ standards | avoid overselling current data as engineering validation | do_not_submit_current_version |

## Claim Adaptation Rules

- For Chemical Engineering Science: use a mechanism-first title and make the general packed-bed transport insight the main conclusion: breakthrough, retention and pore-network degradation are non-equivalent responses.
- For Powder Technology: emphasize particle transport, retention, deposition, topology and pre-clogging screening.
- For IJMF: do not submit the current version unless the flow model is upgraded or the one-way drag limitation is made central and acceptable.
- For Computers & Chemical Engineering: foreground the automated DEM-derived reconstruction, topology metrics, model fitting, surrogate prediction and reproducibility pipeline.
- For Physics of Fluids: foreground anomalous transport, tailing and general particle-laden flow physics; shorten the fusion-specific narrative.
- For Nuclear Fusion: submit only after the blanket-performance argument is substantially strengthened; otherwise the current manuscript is too transport-method focused.
- For fusion/nuclear-engineering journals: foreground Li4SiO4 blanket relevance, but keep the statement that the work is not an experimental or pressure-calibrated safety demonstration.
- For Transport in Porous Media: generalize the packed bed as a granular porous medium and emphasize BTC, retention, connectivity and fractional-tail modeling.
- For Chemical Engineering Journal: hold unless a validation-grade flow or experimental evidence layer is added.

## Title Strategy

Primary CES-style title: `Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds`.

CES-style alternatives:

- `Decoupling breakthrough, retention and pore-network degradation during fine-particle transport in packed pebble beds`
- `Gas-driven fine-particle transport through packed pebble beds: separating breakthrough from pore-network degradation`

Computational-workflow variant: `DEM-derived pore reconstruction and topology analysis of fine-particle breakthrough in packed pebble beds`.

Porous-media variant: `Breakthrough, retention and pore-connectivity response of fine particles in a packed granular porous medium`.

Fusion-engineering variant: `Numerical screening of debris-induced purge-path degradation in Li4SiO4 breeder pebble beds`.

Title patterns to avoid:

- Do not use 'experiment' or 'experimental' in the title.
- Do not lead with a journal-specific phrase such as 'powder technology' in the title.
- Do not promise a 'critical clogging transition' unless repeat-seed and pressure evidence support it.
- Do not call DEM-derived voxel reconstruction 'CT' in the title.
- Do not lead with software mechanics if targeting Chemical Engineering Science.

Preferred title keywords:

`breakthrough`, `retention`, `pore-network degradation`, `fine-particle transport`, `packed pebble beds`, `DEM-derived reconstruction`.

## Next Evidence That Changes The Journal Tier

1. Public repository DOI and author-confirmed declarations.
2. Validation-grade pressure-flow evidence beyond cropped-domain screening.
3. Additional source positions/seeds only if the paper claims a source-location scaling law.
4. Experimental or high-fidelity coupled-flow validation for a CEJ/IJMF-style performance claim.

## Non-Negotiable Boundaries

- Do not claim a universal critical clogging transition.
- Do not call DEM-derived voxel fields experimental CT.
- Do not present the current Ib as pressure-calibrated.
- Do not present one-way Stokes drag as resolved pore-scale gas flow.
