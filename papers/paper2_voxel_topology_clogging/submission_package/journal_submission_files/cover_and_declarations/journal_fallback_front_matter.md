# Paper 2 Journal-Specific Front Matter

This file gives copy-ready front-matter variants for journal fallback decisions. It does not replace author approval or journal-specific formatting checks.

- Primary route: Chemical Engineering Science
- Fallback order: Powder Technology, Particuology, Advanced Powder Technology, Computers & Chemical Engineering, Fusion Engineering and Design, Nuclear Engineering and Design, Nuclear Fusion

## Global Boundaries

- Do not describe DEM-derived voxel fields as experimental CT.
- Do not claim a pressure-calibrated safety limit.
- Do not claim a universal critical clogging transition.
- Do not present one-way Stokes drag as resolved pore-scale gas flow.
- Keep the current conclusion bounded to a pre-clogging migration/filtering regime.

## Chemical Engineering Science

- Role: first_attempt
- Positioning: Mechanism-first packed-bed transport paper.
- Main risk: Pressure evidence is not CFD/LBM-calibrated; keep the pressure-free boundary explicit.

### Title

Breakthrough without pore-network clogging in gas-driven fine-debris transport through Li4SiO4 pebble beds

### Abstract

Fine debris in ceramic breeder pebble beds may be transported by purge gas before it produces a hydraulically degraded pore network. This creates a diagnostic ambiguity: outlet breakthrough, local deposition and connected-pore loss are often interpreted as one clogging sequence although they can occur on different structural scales. We combine DEM debris tracking with DEM-derived voxel pore-structure analysis for a physically stiff 10,000-pebble Li4SiO4 bed. Increasing drag-to-weight ratio promotes downstream migration and weak breakthrough, but the reconstructed outlet-connected void skeleton remains retained. Increasing loading raises local sub-voxel blockage while the pressure-free clogging index remains O(10^-5). The results define a bounded pre-clogging migration/filtering regime and motivate clogging criteria that combine local blockage, connected-pore loss and future pressure response rather than relying on breakthrough alone.

### Cover-Letter Angle

Submit as a fundamental packed-bed transport and structure-response study. Emphasize the non-equivalence of breakthrough, deposition and pore-network degradation, supported by DEM trajectories, voxel topology and benchmark crosswalks.

### Keywords

- packed bed
- fine-particle transport
- discrete element method
- pore topology
- breakthrough curve
- clogging index

## Powder Technology

- Role: realistic_fallback
- Positioning: Powder and particle-technology paper focused on fines retention, deposition and pre-clogging diagnostics.
- Main risk: Avoid making the paper look like a fusion-only application note; foreground particle mechanisms.

### Title

Gas-driven fine-debris retention and pre-clogging deposition in Li4SiO4 packed pebble beds

### Abstract

Fine-particle debris in ceramic pebble beds can be retained, deposited or transported through connected pore pathways under purge-gas drag. We simulate this process in a physically stiff 10,000-particle Li4SiO4 packed bed and post-process the DEM coordinates into voxel-based pore-structure descriptors. The baseline bed has porosity 0.4114, largest connected void fraction 0.9921 and fractal dimension 2.694. Larger drag-to-weight ratio shifts the debris population downstream and increases final breakthrough, while larger debris loading increases local blockage. In the current parameter window, however, the outlet-connected pore skeleton remains retained and the pressure-free clogging index stays far below the screening reference. The study provides a reproducible numerical workflow for distinguishing particle penetration, retention and pre-clogging deposition in packed beds.

### Cover-Letter Angle

Frame the work around powder/debris transport, deposition profiles and particle-scale retention in a packed bed. The novelty is the combined DEM trajectory and topology diagnostic workflow, not a blanket safety claim.

### Keywords

- powder transport
- fine debris
- packed pebble bed
- DEM
- deposition
- pre-clogging

## Computers & Chemical Engineering

- Role: computational_framework_route
- Positioning: Computational-methods paper focused on an automated DEM-to-topology-to-modeling workflow.
- Main risk: The manuscript must foreground workflow transferability and algorithmic traceability rather than a single application case.

### Title

A DEM-derived pore reconstruction workflow for fine-particle breakthrough and pre-clogging risk in packed pebble beds

### Abstract

Packed-bed debris transport studies require a reproducible path from particle trajectories to interpretable structure and risk metrics. We present a DEM-derived workflow that links stiff-particle bed generation, fine-debris migration, voxel-based pore reconstruction, connected-void topology, breakthrough and retention metrics, pressure-free clogging indicators, fractional tail fitting and surrogate-model hooks. The workflow is demonstrated for gas-driven fine-particle transport through a 10,000-pebble Li4SiO4 bed. Within the analyzed window, drag promotes downstream migration and weak breakthrough while the outlet-connected pore skeleton remains retained. The contribution is a traceable computational framework for separating particle penetration, local deposition and topology-level pre-clogging response, with explicit interfaces for later pressure-flow coupling.

### Cover-Letter Angle

Reframe the paper as a reproducible computational workflow. Emphasize automated case generation, data products, topology metrics, model-fitting outputs and conservative screening boundaries.

### Keywords

- computational workflow
- DEM
- pore reconstruction
- packed bed
- surrogate model
- clogging risk

## Particuology

- Role: strong_backup
- Positioning: Particle-systems paper emphasizing particle pathways, retention and topology response.
- Main risk: Application-specific Li4SiO4 details should support, rather than dominate, the particle-mechanism story.

### Title

Particle-level migration and retention mechanisms of fine debris in a connected granular pore network

### Abstract

The transport of fine particles through granular pore networks involves competing particle-level events: migration along connected channels, retention near pore throats, local deposition and possible loss of pore connectivity. We investigate these events using DEM simulations of fine debris in a 10,000-pebble Li4SiO4 bed, combined with voxel-based connected-pore analysis. The simulations show that increasing drag-to-weight ratio changes the dominant response from internal retention to downstream penetration and weak outlet breakthrough. Yet breakthrough does not coincide with measurable loss of the outlet-connected pore skeleton in the analyzed states. Increased debris loading strengthens local accumulation but remains a sub-voxel perturbation of the connected pore space. These results separate particle breakthrough from topology-level clogging and provide a particle-scale basis for pre-clogging indicators in granular beds.

### Cover-Letter Angle

Shorten the fusion engineering motivation and highlight particle-level mechanisms, granular pore-network diagnostics and the separation between breakthrough and structural clogging.

### Keywords

- particle systems
- granular pore network
- fine debris
- retention
- breakthrough
- topology

## Advanced Powder Technology

- Role: solid_backup
- Positioning: Numerical powder-technology paper focused on a reusable diagnostic workflow.
- Main risk: The manuscript must clearly explain novelty beyond one DEM case; focus on the diagnostic framework.

### Title

DEM-derived pore-topology diagnostics for fine-debris transport and deposition in packed ceramic beds

### Abstract

Numerical powder-transport studies often report outlet breakthrough or final deposition, but these outputs do not directly show whether the underlying pore network has degraded. We develop a DEM-derived pore-topology workflow for fine-debris transport in a packed ceramic pebble bed. The method combines particle-resolved debris trajectories, voxelized pore reconstruction, connected-void analysis, local blockage profiles and a pressure-free clogging index. Applied to a stiff 10,000-particle Li4SiO4 bed, the workflow shows that drag-driven debris migration can produce weak breakthrough while preserving the connected pore skeleton. Loading raises local deposition, but the present states remain in a pre-clogging regime. The framework is intended as a reproducible screening tool that can later be coupled with pressure-flow solvers.

### Cover-Letter Angle

Emphasize method reuse: DEM trajectories plus voxel topology as a powder-transport diagnostic pipeline. Keep the language around screening and future pressure coupling conservative.

### Keywords

- powder technology
- DEM
- voxel topology
- ceramic packed bed
- fine-particle deposition
- screening index

## Fusion Engineering and Design

- Role: application_safe_route
- Positioning: Fusion-blanket engineering paper focused on purge-pathway risk screening.
- Main risk: The evidence supports screening and mechanism interpretation, not validated blanket design limits.

### Title

Numerical screening of fine-debris migration and pre-clogging response in Li4SiO4 breeder pebble beds

### Abstract

Fine debris generated in ceramic breeder pebble beds may be entrained by purge gas, retained within pore pathways or transported toward downstream blanket components. We present a numerical screening workflow for this problem using a physically stiff DEM model of a 10,000-pebble Li4SiO4 bed and DEM-derived voxel analysis of the pore skeleton. The baseline bed is highly connected, and debris transport cases show that stronger drag promotes downstream migration and weak breakthrough. However, the outlet-connected pore skeleton remains retained in the analyzed window, and increasing debris loading raises local blockage without producing a pressure-calibrated clogging threshold. The study identifies a pre-clogging migration/filtering regime and defines the evidence needed for future blanket-relevant pressure-flow validation.

### Cover-Letter Angle

Foreground the fusion-blanket purge-pathway motivation and the practical screening value, while stating clearly that the current paper is not an experimental blanket validation or pressure-calibrated safety-limit study.

### Keywords

- fusion blanket
- Li4SiO4
- breeder pebble bed
- purge gas
- fine debris
- numerical screening

## Nuclear Fusion

- Role: high_risk_fusion_stretch
- Positioning: Fusion-technology stretch paper centered on blanket purge-path reliability and breeder-bed resilience.
- Main risk: High risk for the current version because the evidence is stronger as a packed-bed transport paper than as a fusion-performance study.

### Title

Debris-transport resilience of Li4SiO4 breeder pebble beds under purge-gas drag: a DEM-based mechanism study

### Abstract

Ceramic breeder pebble beds in fusion blankets must retain purge-gas pathways while accommodating fine debris generated by degradation or fragmentation processes. We analyze a DEM-based mechanism window for fine-debris migration in a physically stiff 10,000-pebble Li4SiO4 bed. The simulations couple particle-scale debris transport with DEM-derived pore-skeleton reconstruction, breakthrough statistics, local blockage profiles and connected-void metrics. The analyzed cases indicate that weak outlet arrival can occur before measurable loss of the outlet-connected pore skeleton, separating debris breakthrough from topology-level pre-clogging. The study provides a bounded numerical mechanism map for blanket-relevant purge-path risk and identifies the pressure-flow and operating-scenario evidence needed before reactor-performance conclusions can be drawn.

### Cover-Letter Angle

Use only if the introduction and discussion are substantially rewritten around fusion blanket performance, tritium extraction reliability and purge-path resilience. Keep the current evidence boundary explicit.

### Keywords

- fusion blanket
- ceramic breeder
- Li4SiO4
- purge gas
- debris transport
- DEM

## Nuclear Engineering and Design

- Role: nuclear_engineering_backup
- Positioning: Nuclear-engineering backup focused on component-level risk screening for breeder-bed purge pathways.
- Main risk: Requires stronger component-scale implication and uncertainty language than the current CES-style mechanism manuscript.

### Title

Screening fine-debris transport and pre-clogging risk in Li4SiO4 breeder-bed purge pathways

### Abstract

Fine debris in packed ceramic breeder beds can migrate, deposit or partially penetrate purge pathways, complicating component-level risk assessment for fusion blanket concepts. We develop a DEM-based numerical screening workflow for a stiff 10,000-pebble Li4SiO4 bed. Debris trajectories are post-processed into breakthrough curves, retention estimates, local blockage profiles and DEM-derived connected-pore descriptors. The results show a pre-clogging regime in which drag increases downstream migration and weak breakthrough without producing a pressure-calibrated clogging threshold or a detectable collapse of the outlet-connected pore skeleton. The work supports screening-level interpretation of purge-path debris risk and defines the additional pressure-flow evidence required for component-design use.

### Cover-Letter Angle

Frame the study as a conservative component-risk screening method, not as a licensing-grade safety calculation or validated blanket design limit.

### Keywords

- nuclear engineering
- fusion blanket
- breeder bed
- debris transport
- risk screening
- packed bed
