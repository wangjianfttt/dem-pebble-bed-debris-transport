#!/usr/bin/env python3
"""Create a figure provenance manifest for Paper 2."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
OUT_JSON = PAPER_DIR / "data" / "figure_provenance_manifest.json"
OUT_MD = PAPER_DIR / "notes" / "figure_provenance_manifest.md"


FIGURES = [
    {
        "figure_id": "Fig. 1",
        "stem": "paper2_fig1_voxel_topology_framework",
        "role": "packed-bed transport diagnostic separating breakthrough from pore-network clogging",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_paper2_figures.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig1_baseline_topology_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv",
        ],
        "evidence_level": "summary_visualization",
        "claim_boundary": "Mechanism overview only; detailed quantitative claims are supported by Figs. 2-4 and source tables.",
    },
    {
        "figure_id": "Fig. 2",
        "stem": "paper2_fig2_baseline_voxel_topology",
        "role": "baseline voxel-derived pore topology",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_paper2_figures.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig2_box_counting_source.csv",
            "papers/paper2_voxel_topology_clogging/data/baseline_topology_metrics_effective.json",
        ],
        "evidence_level": "production_postprocessing",
        "claim_boundary": "DEM-derived voxel reconstruction, not experimental CT.",
    },
    {
        "figure_id": "Fig. 3",
        "stem": "paper2_fig3_representative_debris_blockage",
        "role": "representative drive-state transport and blockage mechanism",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_paper2_figures.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig3_blockage_profiles_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_mechanism_summary_source.csv",
        ],
        "evidence_level": "production_result",
        "claim_boundary": "Supports pre-clogging migration/filtering states, not critical pore collapse.",
    },
    {
        "figure_id": "Fig. 11",
        "stem": "paper2_fig10_time_resolved_deposition",
        "role": "time-resolved deposition, front migration and delayed weak breakthrough in the representative case",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_time_resolved_deposition_main.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_time_resolved_deposition_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_time_resolved_blockage_profile_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig10_time_resolved_deposition_source.csv",
        ],
        "evidence_level": "production_time_resolved_postprocessing",
        "claim_boundary": "Representative time-resolved case only; supports delayed leading-tail breakthrough, not a universal speed law or critical-clogging threshold.",
    },
    {
        "figure_id": "Fig. 7",
        "stem": "paper2_fig4_loading_clogging_response",
        "role": "loading-dependent BTC, blockage and pressure-free clogging index",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_paper2_figures.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_btc_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_blockage_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv",
        ],
        "evidence_level": "single_seed_loading_scan",
        "claim_boundary": "Does not establish a monotonic loading law or critical transition.",
    },
    {
        "figure_id": "Fig. 4",
        "stem": "paper2_908_spatial_distribution_evidence",
        "role": "high-inventory localized-release population splitting and sparse-front saturation",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_908_spatial_distribution_evidence.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_908_spatial_quantiles.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_908_spatial_cdf_curves.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_908_population_split_evidence.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_908_front_reversal.csv",
        ],
        "evidence_level": "target_time_high_inventory_slowdown_mechanism",
        "claim_boundary": "Supports near-outlet sparse-front saturation and retained-bulk decoupling at the completed 10.00 ms high-inventory frame; not outlet breakthrough, not a fitted source-strength law and not critical clogging.",
    },
    {
        "figure_id": "Fig. 5",
        "stem": "paper2_fig7_localized_time_dynamics",
        "role": "time-resolved localized-release retention, downstream leakage and sparse-front separation",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_localized_time_dynamics.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_timeseries.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig7_localized_time_dynamics_source.csv",
        ],
        "evidence_level": "localized_release_time_dynamics",
        "claim_boundary": "Visualizes DEM tracking of localized-release cases; not a fitted source-position law and not a pressure-calibrated clogging threshold.",
    },
    {
        "figure_id": "Fig. 6",
        "stem": "paper2_openfoam_model_mesh_main",
        "role": "main-text OpenFOAM cropped-domain model and mesh context for returned pressure checks",
        "script": "papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_main_figure.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/figures/openfoam_paraview/N10000_peak_blockage_paraview_render_manifest.json",
            "papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_evidence_source.csv",
        ],
        "evidence_level": "main_text_visualization_of_returned_openfoam_case",
        "claim_boundary": "Documents the cropped-domain OpenFOAM model and mesh context only; not new pressure evidence, not experimental validation and not pressure calibration for Ib.",
    },
    {
        "figure_id": "Fig. 8",
        "stem": "paper2_fig6_mechanism_synthesis",
        "role": "cross-observable mechanism synthesis across drive, localized-release and loading axes",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_mechanism_synthesis.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_timeseries.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_observable_response_cases.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig6_mechanism_synthesis_source.csv",
        ],
        "evidence_level": "derived_mechanism_synthesis",
        "claim_boundary": "Synthesizes existing DEM and voxel post-processing outputs; not a fitted response law, not CFD validation and not a pressure-calibrated critical-clogging criterion.",
    },
    {
        "figure_id": "Fig. 9",
        "stem": "paper2_fig8_response_landscape",
        "role": "cross-case response landscape separating transport, deposition, source-release, pressure-proxy and topology observables",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_additional_mechanism_figures.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_dimensionless_mechanism_map_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_observable_response_cases.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig8_response_landscape_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig8_observable_heatmap_source.csv",
        ],
        "evidence_level": "derived_cross_case_visualization",
        "claim_boundary": "Mines existing source tables for visual synthesis; sparse case families are encoded as states and are not fitted as a universal response law.",
    },
    {
        "figure_id": "Fig. 10",
        "stem": "paper2_fig9_sparse_front_diagnostics",
        "role": "time-resolved high-inventory sparse-front diagnostics for localized release case 908",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_additional_mechanism_figures.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_908_spatial_quantiles.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig9_sparse_front_diagnostics_source.csv",
        ],
        "evidence_level": "target_time_sparse_front_diagnostic",
        "claim_boundary": "Supports retained-bulk and rare-front separation for the completed 908 target-time window; not outlet breakthrough and not a critical-clogging threshold.",
    },
    {
        "figure_id": "Fig. S1",
        "stem": "paper2_figS1_voxel_size_sensitivity",
        "role": "voxel-size sensitivity",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_voxel_size_sensitivity.py",
        "source_tables": ["papers/paper2_voxel_topology_clogging/tables/paper2_voxel_size_sensitivity_source.csv"],
        "evidence_level": "postprocessing_sensitivity",
        "claim_boundary": "Resolution support for the chosen voxel size; coarse grids under-resolve connectivity.",
    },
    {
        "figure_id": "Fig. S2",
        "stem": "paper2_figS2_voxel_coarsening_stress_test",
        "role": "voxel coarsening stress test",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_voxel_size_sensitivity.py",
        "source_tables": ["papers/paper2_voxel_topology_clogging/tables/paper2_voxel_size_sensitivity_source.csv"],
        "evidence_level": "postprocessing_sensitivity",
        "claim_boundary": "Used to bound reconstruction sensitivity, not as independent physical evidence.",
    },
    {
        "figure_id": "Fig. S3",
        "stem": "paper2_figS3_ergun_pressure_proxy",
        "role": "Ergun pressure-gradient proxy",
        "script": "papers/paper2_voxel_topology_clogging/scripts/compute_paper2_pressure_proxy.py",
        "source_tables": ["papers/paper2_voxel_topology_clogging/tables/paper2_pressure_proxy_source.csv"],
        "evidence_level": "closure_proxy",
        "claim_boundary": "Not CFD, not measured pressure and not pressure-calibrated Ib.",
    },
    {
        "figure_id": "Fig. S4",
        "stem": "paper2_figS4_time_resolved_deposition",
        "role": "time-resolved deposition and BTC for representative loading case",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_paper2_time_resolved_deposition.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_time_resolved_deposition_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_time_resolved_blockage_profile_source.csv",
        ],
        "evidence_level": "production_postprocessing",
        "claim_boundary": "Supports delayed leading-tail breakthrough for one representative case only.",
    },
    {
        "figure_id": "Fig. S5",
        "stem": "paper2_figS5_front_migration_metrics",
        "role": "front-migration speed fits",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_paper2_front_migration_metrics.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_front_migration_metrics_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_front_migration_events_source.csv",
        ],
        "evidence_level": "production_postprocessing",
        "claim_boundary": "One representative case; not a universal speed law.",
    },
    {
        "figure_id": "Fig. S6",
        "stem": "paper2_figS6_explicit_localized_release_early_segment",
        "role": "early explicit localized-release segment",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_explicit_localized_release_segment.py",
        "source_tables": ["papers/paper2_voxel_topology_clogging/tables/explicit_localized_release_early_timeseries.csv"],
        "evidence_level": "superseded_by_1M_segment",
        "claim_boundary": "Early-time mechanism support only; superseded by the 1M/10 ms summary.",
    },
    {
        "figure_id": "Fig. S7",
        "stem": "paper2_figS7_localized_release_tail_mechanism",
        "role": "localized-release tail mechanism",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_localized_release_mechanism.py",
        "source_tables": ["papers/paper2_voxel_topology_clogging/tables/explicit_localized_release_mechanism_metrics.csv"],
        "evidence_level": "production_result_906_only",
        "claim_boundary": "Supports 906 source-zone retention to 10 ms only.",
    },
    {
        "figure_id": "Fig. S8",
        "stem": "paper2_figS8_explicit_localized_production_summary",
        "role": "localized-release production status and available production summaries",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_explicit_localized_production_summary.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_timeseries.csv",
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_summary.csv",
        ],
        "evidence_level": "production_result_3_of_3_localized_jobs_completed",
        "claim_boundary": "Production mode includes target-time 906, 907 and 908 localized-release rows; the comparison remains bounded because it is not a fitted source-position or source-strength law.",
    },
    {
        "figure_id": "Fig. S9",
        "stem": "paper2_figS9_907_tail_capture_mechanism",
        "role": "completed 907 downstream-release tail-capture mechanism",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_907_tail_capture_mechanism.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_figS9_907_tail_capture_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_summary.csv",
        ],
        "evidence_level": "completed_907_production_result",
        "claim_boundary": "Supports 907 near-outlet retention to 10 ms; does not establish a general no-breakthrough law.",
    },
    {
        "figure_id": "Fig. S10",
        "stem": "paper2_figS10_source_position_comparison",
        "role": "source-position comparison for available 906 and 907 production windows",
        "script": "papers/paper2_voxel_topology_clogging/scripts/plot_source_position_comparison.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_figS10_source_position_comparison_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_summary.csv",
        ],
        "evidence_level": "bounded_source_position_comparison",
        "claim_boundary": "Compares completed localized-release windows only; 906 is a longer 40 ms upstream-source check while 907 and 908 are 10 ms target-time checks.",
    },
    {
        "figure_id": "Fig. S11",
        "stem": "paper2_figS11_mechanism_evidence_map",
        "role": "integrated mechanism-evidence map",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_paper2_mechanism_evidence.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_mechanism_evidence_matrix.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_front_migration_metrics_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_summary.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv",
        ],
        "evidence_level": "derived_mechanism_synthesis",
        "claim_boundary": "Synthesizes existing evidence for pre-clogging migration/filtering; does not add new transition or pressure-calibration claims.",
    },
    {
        "figure_id": "Fig. S12",
        "stem": "paper2_figS12_voxel_pressure_pilot",
        "role": "voxel-network pressure pilot",
        "script": "papers/paper2_voxel_topology_clogging/scripts/run_voxel_pressure_pilot.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_voxel_pressure_pilot_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_voxel_pressure_pilot_profiles.csv",
        ],
        "evidence_level": "pressure_informed_structural_pilot",
        "claim_boundary": "Solves a scalar Darcy-Laplace problem on connected pore voxels; not CFD, not LBM and not a calibrated pressure-drop measurement.",
    },
    {
        "figure_id": "Fig. S13",
        "stem": "paper2_figS13_cropped_flow_domains",
        "role": "cropped pore-domain inputs for future pressure-flow solvers",
        "script": "papers/paper2_voxel_topology_clogging/scripts/prepare_cropped_flow_domains.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_blockage_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_cropped_flow_domain_manifest.csv",
        ],
        "evidence_level": "solver_input_preparation",
        "claim_boundary": "Defines cropped pore-domain inputs only; not CFD, not LBM and not a measured or calibrated pressure result.",
    },
    {
        "figure_id": "Fig. S14",
        "stem": "paper2_figS14_cropped_flow_permeability",
        "role": "local voxel-network conductance response in cropped peak-blockage domains",
        "script": "papers/paper2_voxel_topology_clogging/scripts/run_cropped_flow_domain_permeability.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_cropped_flow_domain_manifest.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_cropped_flow_permeability_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_cropped_flow_pressure_profiles.csv",
        ],
        "evidence_level": "local_pressure_informed_structural_pilot",
        "claim_boundary": "Solves a scalar Darcy-Laplace network problem on cropped pore voxels; not CFD, not LBM and not a calibrated pressure-drop measurement.",
    },
    {
        "figure_id": "Fig. S15",
        "stem": "paper2_figS15_cropped_flow_permeability_sensitivity",
        "role": "conductance-exponent sensitivity for cropped peak-blockage domains",
        "script": "papers/paper2_voxel_topology_clogging/scripts/run_cropped_flow_permeability_sensitivity.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_cropped_flow_domain_manifest.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_cropped_flow_permeability_sensitivity_source.csv",
        ],
        "evidence_level": "local_pressure_proxy_robustness_check",
        "claim_boundary": "Tests sensitivity of a scalar voxel-network proxy to conductance exponent; not CFD, not LBM and not a calibrated pressure-drop measurement.",
    },
    {
        "figure_id": "Fig. S16",
        "stem": "paper2_figS16_dimensionless_mechanism_map",
        "role": "dimensionless mechanism map separating transport penetration, local blockage and topology loss",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_dimensionless_mechanism_map.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_dimensionless_mechanism_map_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv",
        ],
        "evidence_level": "derived_dimensionless_mechanism_synthesis",
        "claim_boundary": "Derived synthesis of existing evidence; not a full parameter sweep, not a universal regime diagram and not pressure-calibrated.",
    },
    {
        "figure_id": "Fig. S17",
        "stem": "paper2_figS17_near_threshold_repeat_seed_status",
        "role": "near-threshold repeat-seed stochastic variability",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_near_threshold_repeat_results.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_near_threshold_repeat_summary.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_repeat_seed_manuscript_summary_source.csv",
            "papers/paper2_voxel_topology_clogging/supplementary/table_s14_near_threshold_repeat_seed_summary.csv",
        ],
        "evidence_level": "bounded_repeat_seed_uncertainty",
        "claim_boundary": "Bounds stochastic variability for the near-threshold DEM setting; not a critical-transition law.",
    },
    {
        "figure_id": "Fig. S18",
        "stem": "paper2_figS18_subvoxel_hydraulic_evidence",
        "role": "sub-voxel blockage hydraulic-response scale check",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_subvoxel_hydraulic_evidence.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_subvoxel_hydraulic_evidence_source.csv",
            "papers/paper2_voxel_topology_clogging/data/paper2_subvoxel_hydraulic_evidence_summary.json",
        ],
        "evidence_level": "bounded_subvoxel_hydraulic_scale_check",
        "claim_boundary": "Scale-check evidence for sub-voxel hydraulic response only; not CFD, not measured pressure and not pressure-calibrated clogging.",
    },
    {
        "figure_id": "Fig. S19",
        "stem": "paper2_figS19_localized_mechanism_axes",
        "role": "localized-release source retention, downstream release and sparse-front decoupling",
        "script": "papers/paper2_voxel_topology_clogging/scripts/analyze_localized_mechanism_axes.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_timeseries.csv",
            "papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_summary.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_localized_mechanism_axes.csv",
        ],
        "evidence_level": "bounded_three_case_mechanism_comparison",
        "claim_boundary": "Supports retained-bulk and sparse-front decoupling; not a source-position scaling law, completed BTC, outlet breakthrough or critical clogging.",
    },
    {
        "figure_id": "Fig. S20",
        "stem": "paper2_figS20_mechanistic_decoupling_matrix",
        "role": "mechanistic decoupling matrix linking source release, sparse-front advance, local blockage and connectivity loss",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_mechanistic_decoupling_matrix.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_localized_mechanism_axes.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_pressure_proxy_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_mechanistic_decoupling_matrix.csv",
        ],
        "evidence_level": "derived_mechanistic_decoupling_synthesis",
        "claim_boundary": "Derived synthesis of existing localized-release and loading evidence; not a fitted law, completed BTC, pressure-calibrated criterion or critical-transition map.",
    },
    {
        "figure_id": "Fig. S21",
        "stem": "paper2_figS21_observable_response_map",
        "role": "cross-observable response map separating transport, deposition, pressure-proxy and topology observables",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_observable_response_map.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_observable_response_cases.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_observable_response_summary.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_localized_mechanism_axes.csv",
        ],
        "evidence_level": "derived_cross_observable_mechanism_synthesis",
        "claim_boundary": "Derived synthesis of existing DEM and voxel observables; not a fitted response law, not outlet breakthrough, not CFD validation and not a pressure-calibrated critical-clogging criterion.",
    },
    {
        "figure_id": "Fig. S22",
        "stem": "paper2_figS22_3d_resistance_amplification_sensitivity",
        "role": "3D hydraulic-resistance amplification sensitivity in cropped peak-blockage domains",
        "script": "papers/paper2_voxel_topology_clogging/scripts/run_3d_resistance_amplification_sensitivity.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_cropped_flow_domain_manifest.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_3d_resistance_amplification_sensitivity_source.csv",
            "papers/paper2_voxel_topology_clogging/supplementary/table_s15_3d_resistance_amplification_sensitivity.csv",
        ],
        "evidence_level": "reduced_3d_resistance_sensitivity",
        "claim_boundary": "Reduced scalar voxel-network sensitivity to debris-induced 3D resistance amplification; not OpenFOAM CFD, not LBM and not pressure-calibrated.",
    },
    {
        "figure_id": "Fig. S23",
        "stem": "paper2_figS23_openfoam_pressure_evidence",
        "role": "returned cropped-domain OpenFOAM pressure evidence for peak-blockage handoff cases",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_openfoam_evidence_assets.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_evidence_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_screening_source.csv",
        ],
        "evidence_level": "bounded_cropped_domain_openfoam_pressure_check",
        "claim_boundary": "Returned cropped-domain numerical pressure evidence only; not experimental pressure validation, not full-device CFD and not pressure-calibrated Ib.",
    },
    {
        "figure_id": "Fig. S24",
        "stem": "paper2_figS24_openfoam_model_mesh",
        "role": "ParaView-rendered OpenFOAM cropped-domain model and mesh slice",
        "script": "papers/paper2_voxel_topology_clogging/scripts/render_openfoam_paraview_figures.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/figures/openfoam_paraview/N10000_peak_blockage_paraview_render_manifest.json",
            "papers/paper2_voxel_topology_clogging/tables/paper2_flow_solver_handoff_manifest.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_evidence_source.csv",
        ],
        "evidence_level": "visualization_of_returned_openfoam_case",
        "claim_boundary": "Visualization of one representative returned cropped-domain OpenFOAM case and its mesh only; not new pressure evidence, not experimental validation and not blanket-scale CFD.",
    },
    {
        "figure_id": "Fig. S25",
        "stem": "paper2_figS25_parameter_evidence_coverage",
        "role": "parameter-evidence coverage map for bounded mechanism support",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_parameter_evidence_coverage_map.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_parameter_evidence_coverage_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_dimensionless_mechanism_map_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_repeat_seed_manuscript_summary_source.csv",
        ],
        "evidence_level": "derived_parameter_coverage_audit",
        "claim_boundary": "Discrete coverage audit of current mechanism evidence; not a full factorial parameter sweep, not an interpolated phase map and not a universal critical-clogging diagram.",
    },
    {
        "figure_id": "Fig. S26",
        "stem": "paper2_figS26_openfoam_case_matrix",
        "role": "ParaView-rendered OpenFOAM cropped-domain and mesh comparison across returned pressure cases",
        "script": "papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_case_matrix.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/figures/openfoam_paraview/N3000_peak_blockage_paraview_render_manifest.json",
            "papers/paper2_voxel_topology_clogging/figures/openfoam_paraview/N6000_peak_blockage_paraview_render_manifest.json",
            "papers/paper2_voxel_topology_clogging/figures/openfoam_paraview/N10000_peak_blockage_paraview_render_manifest.json",
            "papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_evidence_source.csv",
        ],
        "evidence_level": "visualization_of_returned_openfoam_case_set",
        "claim_boundary": "Visual comparison of the three returned cropped-domain OpenFOAM cases and their mesh slices only; not new pressure evidence, not experimental validation and not blanket-scale CFD.",
    },
    {
        "figure_id": "Fig. S27",
        "stem": "paper2_figS27_deep_mechanism_mining",
        "role": "cross-observable data-mining synthesis of drive, localized release, loading and topology-response separation",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_deep_mechanism_mining.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_deep_mechanism_mining_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_deep_mechanism_correlation_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_dimensionless_mechanism_map_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_evidence_source.csv",
        ],
        "evidence_level": "derived_cross_observable_data_mining",
        "claim_boundary": "Exploratory derived synthesis from existing source tables; not a fitted universal transition law, not a phase map and not pressure-calibrated safety evidence.",
    },
    {
        "figure_id": "Fig. S28",
        "stem": "paper2_figS28_tail_lag_mechanism_mining",
        "role": "time-resolved tail-lag data mining linking leading-tail breakthrough, retained bulk and rare sparse-front survival",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_tail_lag_mechanism_mining.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_tail_lag_mechanism_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_tail_lag_event_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_time_resolved_deposition_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_908_spatial_quantiles.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_908_spatial_cdf_curves.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig7_localized_time_dynamics_source.csv",
        ],
        "evidence_level": "derived_tail_lag_data_mining",
        "claim_boundary": "Exploratory tail-lag synthesis from existing time-resolved source tables; not an experimentally calibrated residence-time distribution, not a universal tailing law and not a critical-clogging transition.",
    },
    {
        "figure_id": "Fig. S29",
        "stem": "paper2_figS29_deposition_heterogeneity_mining",
        "role": "spatial heterogeneity data mining of axial deposition profiles, localization relaxation and downstream spreading",
        "script": "papers/paper2_voxel_topology_clogging/scripts/make_deposition_heterogeneity_mining.py",
        "source_tables": [
            "papers/paper2_voxel_topology_clogging/tables/paper2_deposition_heterogeneity_timeseries.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_deposition_heterogeneity_drive_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_time_resolved_blockage_profile_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_time_resolved_deposition_source.csv",
            "papers/paper2_voxel_topology_clogging/tables/paper2_fig3_blockage_profiles_source.csv",
        ],
        "evidence_level": "derived_deposition_heterogeneity_data_mining",
        "claim_boundary": "Derived spatial-heterogeneity synthesis from existing axial blockage profiles; not pore-scale bridge statistics, not experimental imaging and not a universal clogging law.",
    },
]


def rel(path: Path) -> str:
    """Return a project-relative path string."""
    return str(path.relative_to(PROJECT_ROOT))


def export_paths(stem: str) -> dict[str, str]:
    """Return expected figure export paths for one stem."""
    return {suffix: f"papers/paper2_voxel_topology_clogging/figures/{stem}.{suffix}" for suffix in ("png", "pdf", "svg")}


def path_exists(path_text: str) -> bool:
    """Return whether a project-relative path exists and is non-empty."""
    path = PROJECT_ROOT / path_text
    return path.exists() and path.stat().st_size > 0


def build_manifest() -> list[dict[str, object]]:
    """Build figure provenance rows and validate referenced files."""
    rows = []
    for figure in FIGURES:
        exports = export_paths(str(figure["stem"]))
        row = dict(figure)
        row["exports"] = exports
        row["exports_complete"] = all(path_exists(path) for path in exports.values())
        row["script_exists"] = path_exists(str(figure["script"]))
        row["source_tables_exist"] = {source: path_exists(source) for source in figure["source_tables"]}
        row["all_sources_available"] = all(row["source_tables_exist"].values())
        rows.append(row)
    return rows


def write_markdown(rows: list[dict[str, object]]) -> None:
    """Write a Markdown provenance summary."""
    lines = [
        "# Paper 2 Figure Provenance Manifest",
        "",
        "This manifest maps each manuscript or supplementary figure to the script, source data and evidence boundary used to generate it.",
        "",
        "| Figure | Stem | Evidence level | Script | Sources complete | Boundary |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        sources_ok = "yes" if row["all_sources_available"] and row["exports_complete"] and row["script_exists"] else "no"
        lines.append(
            f"| {row['figure_id']} | {row['stem']} | {row['evidence_level']} | `{row['script']}` | {sources_ok} | {row['claim_boundary']} |"
        )
    lines.extend(
        [
            "",
            "## Regeneration Commands",
            "",
            "```bash",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_paper2_figures.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/plot_908_spatial_distribution_evidence.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_908_population_split_evidence.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/analyze_908_front_reversal.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/analyze_voxel_size_sensitivity.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/compute_paper2_pressure_proxy.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/analyze_paper2_time_resolved_deposition.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/plot_time_resolved_deposition_main.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/analyze_paper2_front_migration_metrics.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/plot_explicit_localized_production_summary.py --mode production",
            "python3 papers/paper2_voxel_topology_clogging/scripts/plot_907_tail_capture_mechanism.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/plot_source_position_comparison.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/analyze_paper2_mechanism_evidence.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/run_voxel_pressure_pilot.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/prepare_cropped_flow_domains.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/run_cropped_flow_domain_permeability.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/run_cropped_flow_permeability_sensitivity.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_dimensionless_mechanism_map.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/analyze_localized_mechanism_axes.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_mechanistic_decoupling_matrix.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_observable_response_map.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/run_3d_resistance_amplification_sensitivity.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_parameter_evidence_coverage_map.py",
            "/Applications/ParaView-5.13.3.app/Contents/bin/pvpython papers/paper2_voxel_topology_clogging/scripts/render_openfoam_paraview_figures.py --case papers/paper2_voxel_topology_clogging/flow_solver_results/openfoam/N10000_peak_blockage --out-dir papers/paper2_voxel_topology_clogging/figures/openfoam_paraview --width 3600 --height 2400",
            "python3 papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_figure.py --render-dir papers/paper2_voxel_topology_clogging/figures/openfoam_paraview --case-label N10000_peak_blockage --out papers/paper2_voxel_topology_clogging/figures/paper2_figS24_openfoam_model_mesh --layout horizontal",
            "python3 papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_case_matrix.py --render-dir papers/paper2_voxel_topology_clogging/figures/openfoam_paraview --out papers/paper2_voxel_topology_clogging/figures/paper2_figS26_openfoam_case_matrix",
            "```",
            "",
            "Diagnostic localized-release figures are intentionally excluded from the formal provenance table unless explicitly marked diagnostic.",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Generate figure provenance JSON and Markdown files."""
    rows = build_manifest()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    write_markdown(rows)
    counts = {
        "figures": len(rows),
        "exports_complete": sum(bool(row["exports_complete"]) for row in rows),
        "sources_complete": sum(bool(row["all_sources_available"]) for row in rows),
        "scripts_available": sum(bool(row["script_exists"]) for row in rows),
    }
    print(json.dumps(counts, indent=2))
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
