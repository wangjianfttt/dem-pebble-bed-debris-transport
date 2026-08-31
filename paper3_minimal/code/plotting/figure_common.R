suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(dplyr)
  library(tidyr)
  library(readr)
  library(scales)
})

colours <- c(
  blue = "#0072B2", orange = "#D55E00", green = "#009E73",
  purple = "#CC79A7", black = "#1A1A1A", grey = "#777777",
  light_grey = "#B8B8B8"
)

paper_theme <- function(base_size = 7.2) {
  theme_classic(base_family = "Arial", base_size = base_size) +
    theme(
      axis.title = element_text(size = base_size + 0.5, colour = colours[["black"]]),
      axis.text = element_text(size = base_size - 0.1, colour = colours[["black"]]),
      axis.line = element_line(linewidth = 0.38, colour = colours[["black"]]),
      axis.ticks = element_line(linewidth = 0.35, colour = colours[["black"]]),
      axis.ticks.length = grid::unit(-1.35, "mm"),
      axis.text.x = element_text(margin = margin(t = 3.5)),
      axis.text.y = element_text(margin = margin(r = 3.5)),
      legend.title = element_blank(),
      legend.text = element_text(size = base_size - 0.3),
      legend.key.height = grid::unit(3.5, "mm"),
      legend.key.width = grid::unit(5.5, "mm"),
      plot.margin = margin(4, 5, 4, 5),
      plot.title = element_text(face = "bold", size = base_size + 1.4, hjust = 0,
                                margin = margin(b = 1.5)),
      plot.title.position = "panel"
    )
}

save_figure <- function(plot, stem, width_mm, height_mm) {
  dir.create(dirname(stem), recursive = TRUE, showWarnings = FALSE)
  width_in <- width_mm / 25.4
  height_in <- height_mm / 25.4

  svglite::svglite(paste0(stem, ".svg"), width = width_in, height = height_in,
                    bg = "white", system_fonts = list(sans = "Arial"))
  print(plot)
  grDevices::dev.off()

  grDevices::cairo_pdf(paste0(stem, ".pdf"), width = width_in, height = height_in,
                       family = "Arial", onefile = TRUE)
  print(plot)
  grDevices::dev.off()

  ragg::agg_tiff(paste0(stem, ".tiff"), width = width_mm, height = height_mm,
                 units = "mm", res = 600, background = "white",
                 compression = "lzw", scaling = 1)
  print(plot)
  grDevices::dev.off()

  ragg::agg_png(paste0(stem, ".png"), width = width_mm, height = height_mm,
                units = "mm", res = 300, background = "white", scaling = 1)
  print(plot)
  grDevices::dev.off()
}

condition_label <- function(ug, ratio) {
  sprintf("%.2f\n%.2f", ug, ratio)
}

geom_mean <- function(x) exp(mean(log(x), na.rm = TRUE))
