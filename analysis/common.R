#!/usr/bin/env Rscript

library(DBI)
library(RSQLite)

# I didn't want to remove the absolute path that worked on Carson's computer,
# so this special cases so it still works on his computer, but just uses the
# energy file adjacent to this script otherwise.
database.path <- (function() {
  username <- Sys.getenv("USER")

  # HACK! To be able to re-source this in debug mode.
  if (exists("database.path"))
    return(database.path)

  if (username == "carsonmclean") {
      return("/Users/carsonmclean/Development/University/CMPUT496/collect-measurments/RESULTS/energy.sqlite")
  } else {
      script.dir <- dirname(sys.frame(1)$ofile)
      path <- paste(script.dir, "energy.sqlite", sep="/")
      return(path)
  }
})()

#############
# DATABASES #
#############

# Connect to the SQLite database.
conn <- dbConnect(RSQLite::SQLite(), database.path)

# Create a data frame of the energy estimates.
energy <- dbGetQuery(conn, "SELECT * FROM energy")
# Fix date/times.
energy$started <- as.POSIXct(energy$started / 1000, origin="1970-01-01")
energy$ended <- as.POSIXct(energy$ended / 1000, origin="1970-01-01")
energy$elapsed_time <- energy$elapsed_time / 1000
# Adjust factor order for plots.
energy$configuration.ordered <-
  factor(energy$configuration,
         levels=c('native', 'ssl', 'multidocker', 'aufs'),
         labels=c('Linux', 'Linux w/SSL', 'Docker', 'Docker w/AUFS'))

# Create a data frame of power measurements, with elapsed time, in seconds.
power <- dbGetQuery(conn, '
  SELECT run, configuration, experiment,
         power, timestamp,
         (timestamp - first_timestamp) / 1000.0
           as "elapsed.time"
    FROM measurement JOIN run ON measurement.run = run.id
                     JOIN (SELECT run, MIN(timestamp) as first_timestamp
                           FROM measurement
                       GROUP BY run) USING (run)
')
# Adjust factor order for plots.
power$configuration.ordered <-
  factor(power$configuration,
         levels=c('native', 'ssl', 'multidocker', 'aufs'),
         labels=c('Linux', 'Linux w/SSL', 'Docker', 'Docker w/AUFS'))

# Get a vector of configurations names and a vector of experiment names.
configurations <- dbGetQuery(conn, 'SELECT name FROM configuration')$name
experiments <- dbGetQuery(conn, 'SELECT name FROM experiment')$name

# Sometimes I type "docker" instead of "multidocker", so this fixes that.
canonical.name <- function(name)
  switch(name,
         docker = 'multidocker',
         linux = 'native',
         name)

pretty.names <- c(
  native = "Linux",
  multidocker = "Docker",
  ssl = "Linux w/SSL",
  aufs = "Docker w/AUFS",
  idle = "Idle",
  redis = "Redis",
  postgres.no.ssl = "PostgreSQL",
  wordpress = "WordPress"
);


# Returns the query for the given expression. Should be passed the return of
# substitute() or quote().
#
# Example expressions:
#
#    wordpress
#    redis ~ docker
#    postgresql ~ linux | docker | ssl
#
# > parse.query(quote(postgresql))
# > parse.query(quote(postgresql ~ linux))
# > parse.query(quote(postgresql ~ linux | docker))
# > parse.query(quote(postgresql ~ linux | docker | ssl))
parse.query <- function (expr) {
  # [1] "redis"
  # [1] "~"  [2] "experiment" [3] "configuration"
  # [1] "~"  [2] "redis"      [3] "|"  [4] "|"  [5] "linux"  [6] "ssl"  [7] "docker"
  names <- all.names(expr)

  if (names[1] != '~') {
    return(list(experiment=names[1]))
  }

  n.alternatives <- length(names[names == "|"]);
  first.at <- 3 + n.alternatives;
  last.at <- length(names);
  return(list(experiment=names[2],
              configurations=names[first.at:last.at]
  ))
  return(names)
}

# Returns a subset of the given data frame for a given experiment and
# configuration passed as a "query" vector, with named indices.
#
# e.g.,
# > subset.of(power, list(experiment="power", configuration="docker"))
# > subset.of(power, list(experiment="power", configurations=c("docker", "linux)))
# > subset.of(power, list(experiment="power"))
subset.of <- function (dataframe, query) {
  exp.name <- query$experiment

  # Make sure it's a valid experiment.
  if (!exp.name %in% experiments)
    stop(exp.name, " is not a valid experiment.",
         " Choose from: ", paste(experiments, collapse=", "))

  # Figure out the configurations
  if ("configuration" %in% names(query)) {
    config.names <- query$configuration
  } else if ("configurations" %in% names(query)) {
    config.names <- query$configurations
  } else {
    config.names <- configurations
  }
  config.names <- sapply(config.names, canonical.name)

  for (name in config.names) {
    if (!name %in% configurations)
      stop(name, " is not a valid configuration.",
           " Choose from: ", paste(configurations, collapse=", "))
  }

  data <- subset(dataframe,
                 experiment == exp.name &
                   configuration %in% config.names)
  stopifnot(nrow(data) > 0)
  return(data)
}

############
# PLOTTING #
############

# LaTeX settings:
TEXT.WIDTH <- 6.5  # inches
COLUMN.WIDTH <- 3.125  # inches
PAGE.HEIGHT <- 9  # inches

# Creates a scale function that appends an SI unit to the numbers in the scale.
append.unit <- function(unit)
  function (breaks)
    sapply(breaks, function (b) paste(b, unit))

# Saves the plot with the appropriate name.
.save.plot <- function (plot, width = TEXT.WIDTH, height = PAGE.HEIGHT / 4) {
  filename <- paste(plot$filename, "pdf", sep=".");
  ggsave(filename,
         plot = plot,
         width = width,
         height = height,
         units = "in");
}