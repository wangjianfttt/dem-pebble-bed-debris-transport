#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) {
  stop("Usage: Rscript code/figures/reproduce_main_figures.R OUTPUT_DIRECTORY")
}

script_arg <- grep("^--file=", commandArgs(), value = TRUE)
script_dir <- dirname(normalizePath(sub("^--file=", "", script_arg[[1]]), mustWork = TRUE))
root <- normalizePath(file.path(script_dir, "../.."), mustWork = TRUE)
data_dir <- file.path(root, "data/figure_source")
out_dir <- normalizePath(args[[1]], mustWork = FALSE)
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
source(file.path(script_dir, "figure_common.R"))

cell_levels <- c("0.10\n0.05", "0.20\n0.05", "0.10\n0.10", "0.20\n0.10")
add_cell <- function(df) {
  df %>% mutate(
    cell = factor(condition_label(gas_velocity_m_s, df_over_dp), levels = cell_levels),
    gas = factor(sprintf("U[s] = %.2f m s^-1", gas_velocity_m_s)),
    ratio = factor(sprintf("d[f]/d[p] = %.2f", df_over_dp))
  )
}
shape_values <- c("U[s] = 0.10 m s^-1" = 21, "U[s] = 0.20 m s^-1" = 22)
colour_values <- c("d[f]/d[p] = 0.05" = colours[["blue"]],
                   "d[f]/d[p] = 0.10" = colours[["orange"]])

# Figure 1: complete transport matrix -------------------------------------------------
release <- read_csv(file.path(data_dir, "postequilibrated_transport_matrix_release_source.csv"),
                    show_col_types = FALSE) %>% add_cell()
summary <- read_csv(file.path(data_dir, "postequilibrated_transport_matrix_summary_source.csv"),
                    show_col_types = FALSE) %>% add_cell()
matrix_specs <- tibble::tribble(
  ~metric, ~ylabel, ~reference, ~scale_factor,
  "mean_dx_dp", "Mean axial displacement, Δx/d_p", NA_real_, 1,
  "fpt_5dp_reached_fraction", "Fraction reaching 5d_p", NA_real_, 1,
  "mean_dz_dp", "Mean vertical displacement, Δz/d_p", 0, 1,
  "centered_msd_exponent", "Centered-MSD exponent, γ_MSD", 1, 1,
  "mean_sampled_contact_fraction", "Sampled contact fraction", NA_real_, 1,
  "pressure_gradient_tail_mean_Pa_m", "Pressure gradient (kPa m^-1)", NA_real_, 1e-3
)
matrix_panel <- function(metric_name, ylabel, reference = NA_real_, scale_factor = 1) {
  rr <- release %>% transmute(cell, gas, ratio, value = .data[[metric_name]] * scale_factor)
  ss <- summary %>% filter(metric == metric_name) %>%
    transmute(cell, gas, ratio, mean = mean * scale_factor,
              low = ci95_low * scale_factor, high = ci95_high * scale_factor)
  p <- ggplot() +
    geom_point(data = rr, aes(cell, value, shape = gas, colour = ratio), fill = "white",
               size = 2, stroke = 0.65,
               position = position_jitter(width = 0.075, height = 0, seed = 31)) +
    geom_errorbar(data = ss, aes(cell, ymin = low, ymax = high, colour = ratio),
                  width = 0.14, linewidth = 0.45) +
    geom_point(data = ss, aes(cell, mean, shape = gas, fill = ratio),
               colour = colours[["black"]], size = 2.45, stroke = 0.45) +
    scale_shape_manual(values = shape_values) + scale_colour_manual(values = colour_values) +
    scale_fill_manual(values = colour_values) +
    labs(x = "Uₛ (m s⁻¹) / d_f/d_p", y = ylabel) + paper_theme()
  if (is.finite(reference)) {
    p <- p + geom_hline(yintercept = reference, linetype = 3,
                        colour = colours[["grey"]], linewidth = 0.4)
  }
  p
}
matrix_plots <- lapply(seq_len(nrow(matrix_specs)), function(i) {
  matrix_panel(matrix_specs$metric[[i]], matrix_specs$ylabel[[i]],
               matrix_specs$reference[[i]], matrix_specs$scale_factor[[i]]) +
    labs(title = sprintf("(%s)", letters[[i]]))
})
fig1 <- wrap_plots(matrix_plots, ncol = 3, guides = "collect") &
  theme(legend.position = "none")
save_figure(fig1, file.path(out_dir, "postequilibrated_transport_matrix"), 183, 122)

# Figure 2: first passage, held-out prediction and state durations -------------------
base_curve <- read_csv(file.path(data_dir, "pooled_first_passage_curve_source.csv"),
                       show_col_types = FALSE) %>%
  mutate(series = factor(series, levels = c("CFD-DEM passage", "Classical", "Time-fractional")))
base_info <- read_csv(file.path(root, "data/first_passage/pooled_first_passage_summary.csv"),
                      show_col_types = FALSE) %>%
  filter(gas_velocity_m_s == 0.10, df_over_dp == 0.05)
cv_long <- read_csv(file.path(data_dir, "pooled_first_passage_cv_source.csv"),
                    show_col_types = FALSE) %>%
  mutate(cell = factor(cell, levels = cell_levels),
         model = factor(model, levels = c("Classical", "Time-fractional")))
tr_long <- read_csv(file.path(data_dir, "transition_scaling_source.csv"),
                    show_col_types = FALSE) %>%
  mutate(quantile = factor(quantile, levels = c("P50", "P90", "P99")))
wait_env <- read_csv(file.path(data_dir, "waiting_survival_envelope_source.csv"),
                     show_col_types = FALSE) %>%
  mutate(state = factor(state, levels = c("Low mobility", "Reverse")))
p2a <- ggplot(base_curve, aes(time_s * 1000, passage, colour = series, linetype = series)) +
  geom_step(data = filter(base_curve, series == "CFD-DEM passage"), linewidth = 0.65, direction = "hv") +
  geom_line(data = filter(base_curve, series != "CFD-DEM passage"), linewidth = 0.75) +
  annotate("text", x = Inf, y = -Inf,
           label = sprintf("n = %d/300; alpha = %.2f",
                           base_info$observed_passage_count, base_info$fractional_alpha),
           hjust = 1.05, vjust = -0.7, size = 2.25) +
  scale_colour_manual(values = c("CFD-DEM passage" = colours[["black"]],
                                 "Classical" = colours[["blue"]],
                                 "Time-fractional" = colours[["orange"]])) +
  scale_linetype_manual(values = c("CFD-DEM passage" = 1, "Classical" = 2,
                                   "Time-fractional" = 1)) +
  coord_cartesian(ylim = c(0, 1)) +
  labs(x = "Time from release (ms)", y = "Fraction reaching 5d_p") + paper_theme()
cv_mean <- cv_long %>% group_by(cell, model) %>% summarise(rmse = mean(rmse), .groups = "drop")
p2b <- ggplot(cv_long, aes(cell, rmse, colour = model,
                           group = interaction(cell, held_out_release_seed))) +
  geom_line(colour = colours[["light_grey"]], linewidth = 0.38,
            position = position_dodge(width = 0.34)) +
  geom_point(shape = 21, fill = "white", size = 1.8, stroke = 0.55,
             position = position_dodge(width = 0.34)) +
  geom_point(data = cv_mean, aes(group = model, fill = model), shape = 21,
             colour = colours[["black"]], size = 2.35, stroke = 0.4,
             position = position_dodge(width = 0.34)) +
  scale_colour_manual(values = c("Classical" = colours[["blue"]],
                                 "Time-fractional" = colours[["orange"]])) +
  scale_fill_manual(values = c("Classical" = colours[["blue"]],
                               "Time-fractional" = colours[["orange"]])) +
  labs(x = "Uₛ (m s⁻¹) / d_f/d_p", y = "Held-out CDF RMSE") + paper_theme()
tr_mean <- tr_long %>% group_by(step_dp, quantile) %>%
  summarise(normalized = geom_mean(normalized), .groups = "drop")
p2c <- ggplot(tr_long, aes(step_dp, normalized, colour = quantile,
                           group = interaction(case, quantile))) +
  geom_line(alpha = 0.16, linewidth = 0.35) +
  geom_line(data = tr_mean, aes(group = quantile), linewidth = 0.8) +
  geom_point(data = tr_mean, aes(shape = quantile, group = quantile), size = 1.7, stroke = 0.35) +
  scale_x_log10(breaks = c(0.5, 1, 2, 5)) + scale_y_log10() +
  scale_colour_manual(values = c("P50" = colours[["black"]], "P90" = colours[["green"]],
                                 "P99" = colours[["purple"]])) +
  labs(x = "Transition length, ℓ/d_p", y = "Normalized transition time") + paper_theme()
p2d <- ggplot(wait_env, aes(transition_time_s * 1000, empirical, colour = state, fill = state)) +
  geom_ribbon(aes(ymin = low, ymax = high), alpha = 0.14, colour = NA) +
  geom_line(linewidth = 0.75) + geom_line(aes(y = fitted), linetype = 2, linewidth = 0.55) +
  scale_x_log10() + scale_y_log10(limits = c(1e-3, 1.05)) +
  scale_colour_manual(values = c("Low mobility" = colours[["purple"]],
                                 "Reverse" = colours[["green"]])) +
  scale_fill_manual(values = c("Low mobility" = colours[["purple"]],
                               "Reverse" = colours[["green"]])) +
  labs(x = "State duration (ms)", y = "Survival probability") + paper_theme()
fig2 <- ((p2a + labs(title = "(a)") + theme(legend.position = "top")) +
         (p2b + labs(title = "(b)") + theme(legend.position = "top"))) /
        ((p2c + labs(title = "(c)") + theme(legend.position = "top")) +
         (p2d + labs(title = "(d)") + theme(legend.position = "top")))
save_figure(fig2, file.path(out_dir, "pooled_first_passage_models"), 183, 122)

# Figure 3: release-level spreading and velocity persistence -------------------------
memory <- read_csv(file.path(data_dir, "postequilibrated_transport_memory_source.csv"),
                   show_col_types = FALSE) %>% add_cell()
memory_point_panel <- function(metric_name, ylabel, reference = NA_real_) {
  rr <- memory %>% transmute(cell, gas, ratio, value = .data[[metric_name]])
  mm <- rr %>% group_by(cell, gas, ratio) %>% summarise(value = mean(value), .groups = "drop")
  p <- ggplot(rr, aes(cell, value, shape = gas, colour = ratio)) +
    geom_point(fill = "white", size = 2, stroke = 0.62,
               position = position_jitter(width = 0.075, height = 0, seed = 31)) +
    geom_point(data = mm, aes(fill = ratio), colour = colours[["black"]],
               size = 2.45, stroke = 0.42) +
    scale_shape_manual(values = shape_values) + scale_colour_manual(values = colour_values) +
    scale_fill_manual(values = colour_values) +
    labs(x = "Uₛ (m s⁻¹) / d_f/d_p", y = ylabel) + paper_theme()
  if (is.finite(reference)) {
    p <- p + geom_hline(yintercept = reference, linetype = 3,
                        colour = colours[["grey"]], linewidth = 0.4)
  }
  p
}
memory_window_panel <- function(fields, ylabel) {
  dd <- memory %>% select(case, cell, all_of(fields)) %>%
    pivot_longer(all_of(fields), names_to = "window", values_to = "value") %>%
    mutate(window = factor(window, levels = fields, labels = c("20 ms", "50 ms")))
  means <- dd %>% group_by(cell, window) %>% summarise(value = mean(value), .groups = "drop")
  ggplot(dd, aes(cell, value, colour = window, group = interaction(cell, case))) +
    geom_line(colour = colours[["light_grey"]], linewidth = 0.34,
              position = position_dodge(width = 0.34)) +
    geom_point(shape = 21, fill = "white", size = 1.75, stroke = 0.52,
               position = position_dodge(width = 0.34)) +
    geom_point(data = means, aes(fill = window, group = window), shape = 21,
               colour = colours[["black"]], size = 2.2, stroke = 0.4,
               position = position_dodge(width = 0.34)) +
    scale_colour_manual(values = c("20 ms" = colours[["blue"]], "50 ms" = colours[["orange"]])) +
    scale_fill_manual(values = c("20 ms" = colours[["blue"]], "50 ms" = colours[["orange"]])) +
    labs(x = "Uₛ (m s⁻¹) / d_f/d_p", y = ylabel) + paper_theme()
}
p3a <- memory_point_panel("centered_msd_exponent", "Centered-MSD exponent, γ_MSD", 1)
p3b <- memory_point_panel("velocity_positive_integral_time_s", "Positive correlation integral (s)")
p3c <- memory_window_panel(c("velocity_variance_ratio_20ms", "velocity_variance_ratio_50ms"),
                           "Endpoint/origin velocity variance")
p3d <- memory_window_panel(c("non_gaussian_parameter_20ms", "non_gaussian_parameter_50ms"),
                           "Axial non-Gaussian parameter") +
  geom_hline(yintercept = 0, linetype = 3, colour = colours[["grey"]], linewidth = 0.4)
fig3 <- ((p3a + labs(title = "(a)") + theme(legend.position = "none")) +
         (p3b + labs(title = "(b)") + theme(legend.position = "none"))) /
        ((p3c + labs(title = "(c)") + theme(legend.position = "top")) +
         (p3d + labs(title = "(d)") + theme(legend.position = "none")))
save_figure(fig3, file.path(out_dir, "postequilibrated_transport_memory"), 183, 112)

# Figure 4: mechanism sensitivity -----------------------------------------------------
disp_boot <- read_csv(file.path(data_dir, "transport_mechanism_displacement_source.csv"),
                      show_col_types = FALSE)
lag_plot <- read_csv(file.path(data_dir, "transport_mechanism_msd_source.csv"),
                     show_col_types = FALSE)
fraction_rows <- read_csv(file.path(data_dir, "transport_mechanism_fraction_source.csv"),
                          show_col_types = FALSE)
condition_cols <- c("Reference" = colours[["black"]],
                    "Local-fluid initial velocity" = colours[["blue"]],
                    "Debris gravity = 0" = colours[["orange"]])
p4a <- ggplot(disp_boot, aes(metric, paired_mean_difference, colour = comparison,
                             shape = comparison)) +
  geom_hline(yintercept = 0, linetype = 3, colour = colours[["grey"]], linewidth = 0.4) +
  geom_errorbar(aes(ymin = bootstrap_ci95_low, ymax = bootstrap_ci95_high),
                width = 0.12, linewidth = 0.48, position = position_dodge(width = 0.35)) +
  geom_point(size = 2.25, stroke = 0.5, position = position_dodge(width = 0.35)) +
  scale_colour_manual(values = condition_cols[c("Local-fluid initial velocity", "Debris gravity = 0")]) +
  scale_shape_manual(values = c("Local-fluid initial velocity" = 22, "Debris gravity = 0" = 24)) +
  labs(x = NULL, y = "Paired change in displacement (d_p)") + paper_theme()
p4b <- ggplot(lag_plot, aes(lag_s, msd_ratio, colour = condition)) +
  geom_hline(yintercept = 1, linetype = 3, colour = colours[["grey"]], linewidth = 0.4) +
  geom_line(linewidth = 0.78) + scale_x_log10() +
  scale_colour_manual(values = condition_cols[-1]) +
  labs(x = "Lag time (s)", y = "Centered axial MSD / reference") + paper_theme()
p4c <- ggplot(fraction_rows, aes(value, measure, colour = condition, shape = condition)) +
  geom_point(size = 2.25, stroke = 0.5, position = position_dodge(width = 0.5)) +
  scale_colour_manual(values = condition_cols) +
  scale_shape_manual(values = c("Reference" = 21, "Local-fluid initial velocity" = 22,
                                "Debris gravity = 0" = 24)) +
  scale_x_continuous(limits = c(0, 1), breaks = c(0, 0.5, 1)) +
  labs(x = "Particle fraction", y = NULL) + paper_theme()
fig4 <- (p4a + labs(title = "(a)") + theme(legend.position = "none")) +
  (p4b + labs(title = "(b)") + theme(legend.position = "top")) +
  (p4c + labs(title = "(c)") + theme(legend.position = "none")) +
  plot_layout(widths = c(1, 1.05, 1.25))
save_figure(fig4, file.path(out_dir, "transport_mechanism_sensitivity"), 183, 74)

# Figure 5: model-applicability diagnostics ------------------------------------------
model_metrics <- read_csv(file.path(data_dir, "model_applicability_grid_source.csv"),
                          show_col_types = FALSE) %>%
  mutate(zone = factor(zone, levels = c("Release zone", "Interior window")))
force_samples <- read_csv(file.path(data_dir, "model_applicability_occupied_position_source.csv"),
                          show_col_types = FALSE)
zone_cols <- c("Release zone" = colours[["blue"]], "Interior window" = colours[["orange"]])
zone_shapes <- c("Release zone" = 21, "Interior window" = 22)
p5a <- ggplot(model_metrics, aes(cells_per_dp, porosity, colour = zone, shape = zone, group = zone)) +
  geom_line(linewidth = 0.65) + geom_point(fill = "white", size = 2.25, stroke = 0.65) +
  geom_segment(data = model_metrics %>% group_by(zone) %>%
                 summarise(x = min(cells_per_dp), xend = max(cells_per_dp),
                           y = first(porosity_reference), .groups = "drop"),
               aes(x = x, xend = xend, y = y, yend = y, colour = zone), inherit.aes = FALSE,
               linetype = 2, linewidth = 0.55) +
  scale_colour_manual(values = zone_cols) + scale_shape_manual(values = zone_shapes) +
  scale_x_continuous(breaks = c(10, 15, 20)) +
  labs(x = "Resolved cells per d_p", y = "Comparison-window porosity") + paper_theme()
p5b <- ggplot(model_metrics, aes(cells_per_dp, pressure_ratio, colour = zone,
                                 shape = zone, group = zone)) +
  geom_hline(yintercept = 1, linetype = 3, colour = colours[["grey"]], linewidth = 0.4) +
  geom_line(linewidth = 0.65) + geom_point(fill = "white", size = 2.25, stroke = 0.65) +
  scale_colour_manual(values = zone_cols) + scale_shape_manual(values = zone_shapes) +
  scale_x_continuous(breaks = c(10, 15, 20)) +
  labs(x = "Resolved cells per d_p", y = "Resolved/unresolved pressure gradient") + paper_theme()
p5c <- ggplot(model_metrics, aes(cells_per_dp, ux_relative_l2, colour = zone,
                                 shape = zone, group = zone)) +
  geom_line(linewidth = 0.65) + geom_point(fill = "white", size = 2.25, stroke = 0.65) +
  scale_colour_manual(values = zone_cols) + scale_shape_manual(values = zone_shapes) +
  scale_x_continuous(breaks = c(10, 15, 20)) +
  labs(x = "Resolved cells per d_p", y = "Filtered axial-velocity relative L2") + paper_theme()
force_median <- median(force_samples$magnitude_ratio)
force_reversed <- mean(force_samples$reversed)
p5d <- ggplot(force_samples, aes(magnitude_ratio)) +
  stat_ecdf(geom = "step", linewidth = 0.75, colour = colours[["purple"]]) +
  geom_vline(xintercept = 1, linetype = 3, colour = colours[["grey"]], linewidth = 0.4) +
  geom_vline(xintercept = force_median, linetype = 2, colour = colours[["purple"]], linewidth = 0.5) +
  annotate("text", x = Inf, y = 0.05,
           label = sprintf("n = %d\nmedian = %.2f\ndirection reversed = %.1f%%",
                           nrow(force_samples), force_median, 100 * force_reversed),
           hjust = 1.04, vjust = 0, size = 2.2) +
  scale_x_log10() + labs(x = "Fixed-coefficient force-magnitude ratio",
                         y = "Cumulative fraction") + paper_theme()
fig5 <- ((p5a + labs(title = "(a)") + theme(legend.position = "top")) +
         (p5b + labs(title = "(b)") + theme(legend.position = "none"))) /
        ((p5c + labs(title = "(c)") + theme(legend.position = "none")) +
         (p5d + labs(title = "(d)") + theme(legend.position = "none")))
save_figure(fig5, file.path(out_dir, "model_applicability_diagnostic"), 183, 112)

message("Reproduced five Paper 3 main figures in: ", out_dir)
