#!/usr/bin/env Rscript

library(effsize)
library(plyr)
library(ggplot2)
library(R.utils)

if (!exists("conn")) {
  source("common.R")
}

# Get the total energy of an experiment on a configuration
# e.g., energy.of(postgresql ~ native | ssl)    "energy of postgresql on linux or linux with ssl"
energy.of <- function (query) energy.of.q(substitute(query))
energy.of.q <- function (query) subset.of(energy, parse.query(query))

# Get all of the native Linux measurements.
linux <- energy[energy$configuration == 'native',]
# Get all of the Docker (container) measurements.
docker <- energy[energy$configuration == 'multidocker',]
# Get all of the Linux measurements with SSL enabled.
linux.ssl <- energy[energy$configuration == 'ssl',]

# Creates a dataframe including only time and energy of a given
# "runset" -- a pair of configuration and time.
make.runset <- function(experiment, configuration) {
  exp <- configuration[configuration$experiment == experiment,];
  energy <- exp[,c("energy")];
  time <- exp[,c("elapsed_time")];
  return(data.frame(time, energy));
};

correlate <- function (runset, method = "pearson") {
  return(cor(runset$time, runset$energy, method = method));
};

is.normal <- function(shapiro.results) shapiro.results$p.value >= 0.05;


compare.experiment <- function (experiment) {
  linux.runs <- make.runset(experiment, linux);
  docker.runs <- make.runset(experiment, docker);

  stopifnot(length(linux.runs$energy) == length(docker.runs$energy),
            length(linux.runs$energy) > 0);

  # A subset of the dataframe.
  exp.name <- experiment;
  relevent.data <- subset(
    energy,
    experiment == exp.name &
      configuration %in% c("native", "multidocker")
  );

  # If either of the distributions are not normal, then
  # the t-test isn't valid.
  normality <- list(linux = shapiro.test(linux.runs$energy),
                    docker = shapiro.test(docker.runs$energy));

  return(list(
    # Normality:
    are.normal = list(linux = is.normal(normality$linux),
                      docker = is.normal(normality$docker)),
    how.normal = normality,

    # Are they different? (both parametric and non-parametric)
    t.test = t.test(energy ~ configuration,
                    data = relevent.data,
                    paired = TRUE),
    kruskal.wallis = kruskal.test(list(
      linux.runs$energy,
      docker.runs$energy
    )),

    pairwise.wicoxon.rank.sum = pairwise.wilcox.test(
      relevent.data$energy,
      relevent.data$configuration),

    # How different?
    cohen.d = cohen.d(energy ~ configuration,
                      data = relevent.data),
    cliff.delta = cliff.delta(energy ~ configuration,
                              data = relevent.data),

    # Correlate energy with time.
    correlation = list(
      linear = list(
        linux = correlate(linux.runs, method = "pearson"),
        docker = correlate(docker.runs, method = "pearson")
      ),
      rank = list(
        linux = correlate(linux.runs, method = "spearman"),
        docker = correlate(docker.runs, method = "spearman")
      )
    ),

    time.plot = ggplot(data = relevent.data,
                       aes(configuration, elapsed_time)),
    energy.plot = ggplot(data = relevent.data,
                         aes(configuration, energy)),

    runs = list(
      linux = linux.runs,
      docker = docker.runs
    )
  ));
};

# HACK! The Postgress one, with three runs.
compare.postgres.experiment <- function () {
  experiment <- "postgresql";
  # A subset of the dataframe.
  relevent.data <- subset(
    energy,
    experiment == "postgresql"
  );

  linux.runs <- make.runset(experiment, linux);
  ssl.runs <- make.runset(experiment, linux.ssl);
  docker.runs <- make.runset(experiment, docker);

  stopifnot(length(linux.runs$energy) == length(docker.runs$energy),
            length(linux.runs$energy) > 0);

  # If either of the distributions are not normal, then
  # the t-test isn't valid.
  normality <- list(linux = shapiro.test(linux.runs$energy),
                    docker = shapiro.test(docker.runs$energy),
                    ssl = shapiro.test(ssl.runs$energy));

  linux.v.docker <- subset(relevent.data,
                           configuration %in% c('native', 'multidocker'));
  linux.v.ssl <- subset(relevent.data,
                        configuration %in% c('native', 'ssl'));
  docker.v.ssl <- subset(relevent.data,
                         configuration %in% c('multidocker', 'ssl'));

  return(list(
    # Normality:
    are.normal = list(linux = is.normal(normality$linux),
                      docker = is.normal(normality$docker),
                      ssl = is.normal(normality$ssl)),
    how.normal = normality,

    # Are they different? (both parametric and non-parametric)
    t.test = pairwise.t.test(relevent.data$energy,
                             relevent.data$configuration,
                             paired = TRUE),
    kruskal.wallis = kruskal.test(list(
      linux.runs$energy,
      docker.runs$energy,
      ssl.runs$energy
    )),

    pairwise.wicoxon.rank.sum = pairwise.wilcox.test(
      relevent.data$energy,
      relevent.data$configuration
    ),

    # How different?
    cohen.d = list(
      linux.v.docker = cohen.d(energy ~ configuration,
                               data = linux.v.docker),
      linux.v.ssl = cohen.d(energy ~ configuration,
                            data = linux.v.ssl),
      docker.v.ssl = cohen.d(energy ~ configuration,
                             data = docker.v.ssl)
    ),

    # Correlate energy with time.
    linear.correlation = list(
      linux = correlate(linux.runs, method = "pearson"),
      docker = correlate(docker.runs, method = "pearson"),
      ssl = correlate(docker.runs, method = "pearson")
    ),

    time.plot = ggplot(data = relevent.data,
                       aes(configuration, elapsed_time)),
    energy.plot = ggplot(data = relevent.data,
                         aes(configuration, energy)),

    runs = list(
      linux = linux.runs,
      docker = docker.runs,
      ssl = ssl.runs
    )
  ));
};

# Compute ALL THE STATS!
idle <- compare.experiment("idle")
redis <- compare.experiment("redis")
#postgres <- compare.experiment("postgresql")
postgres <- compare.postgres.experiment()
wordpress <- compare.experiment("wordpress")

# Maps labels to "99,999 J" format.
thousands.joules <- function (labs)
  lapply(labs, function (x)
    paste(format(x, big.mark=","), "J", sep=" "))

# Creates a Violin plot for energy.
format.energy.plot <- function(experiment.summary,
                               configurations = c("native", "multidocker")) {
  experiment.name <- deparse(substitute(experiment.summary));
  filename <- paste(experiment.name, "energy", sep="-");

  formatted.plot <-
    experiment.summary$energy.plot +
      geom_violin(draw_quantiles = c(0.5)) +
      labs(y = "Energy", x = NULL, title = capitalize(experiment.name)) +
      scale_y_continuous(labels = thousands.joules) +
      scale_x_discrete(labels = pretty.names,
                       limits = configurations) +
      theme_light() +
      theme(plot.title = element_text(hjust = 0.5));

  formatted.plot$filename <- filename;

  return(formatted.plot);
}


format.time.plot <- function(experiment.summary,
                               configurations = c("native", "multidocker")) {
  experiment.name <- deparse(substitute(experiment.summary));
  filename <- paste(experiment.name, "time", sep="-");

  formatted.plot <-
    experiment.summary$time.plot +
    geom_violin(draw_quantiles = c(0.5)) +
    labs(y = "Time", x = NULL, title = capitalize(experiment.name)) +
    scale_y_continuous(labels = append.unit("s")) +
    scale_x_discrete(labels = pretty.names,
                     limits = configurations) +
    theme_light() + 
    theme(plot.title = element_text(hjust = 0.5));


  formatted.plot$filename <- filename

  return(formatted.plot)
}


save.plot <- function (p) .save.plot(p, width = COLUMN.WIDTH, height = 3)

if (interactive()) {
  show(format.time.plot(redis))
} else {
  # When run as a script:
  save.plot(format.energy.plot(idle))
  save.plot(format.energy.plot(redis))
  save.plot(format.energy.plot(wordpress))
  save.plot(format.energy.plot(postgres))
  save.plot(format.time.plot(redis))
}
