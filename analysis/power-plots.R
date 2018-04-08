#!/usr/bin/env Rscript

library(ggplot2)

# Get the power thing.
if (!exists("subset.of")) {
  source("common.R")
}

# Get all power measurements of an experiment on a configuration
# e.g., power.of(idle ~ linux)                  "power of idle on linux"
power.of <- function (query) power.of.q(substitute(query))
power.of.q <- function (query) subset.of(power, parse.query(query))

# Returns a density plot, with plain styles.
# run.expr is of the form: experiment ~ configuration.
# e.g., redis ~ linux; or wordpress ~ docker.
power.density.plot <- function(expr, faceted = TRUE) {
  power.subset <- power.of.q(substitute(expr))
  plot <- ggplot(power.subset, aes(x = elapsed.time, y = power)) +
    geom_hex(bins = 35) +
    scale_fill_gradient(low = "#cccccc",
                        high = "black",
                        guide = FALSE) + 
    xlab("Time") + scale_x_continuous(labels = append.unit("s")) +
    ylab("Power") + scale_y_continuous(labels = append.unit("W")) +
    theme_light()
  
  # XXX: special breaks for Wordpress
  if (substitute(expr) == "wordpress")
    plot <- plot + scale_x_continuous(labels = append.unit("s"),
                                      breaks=c(0, 300, 600, 900, 1200))

  # Add the facet grid:
  if (faceted)
    plot <- plot + facet_grid(. ~ configuration.ordered)

  # Append the file name for use with save.plot().
  experiment <- parse.query(substitute(expr))$experiment
  plot$filename <- paste(experiment, "power", sep="-")

  return(plot)
}

save.plot <- function (p) .save.plot(p, width = TEXT.WIDTH, height = 3.5)

if (interactive()) {
  show(power.density.plot(wordpress))
} else {
  # When run as a script:
  save.plot(power.density.plot(idle))
  save.plot(power.density.plot(postgresql))
  save.plot(power.density.plot(redis))
  save.plot(power.density.plot(wordpress))
}