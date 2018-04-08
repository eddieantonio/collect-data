#!/usr/bin/env Rscript

# Installs the appropriate packages to run the tests.

# For plotting:
install.packages("ggplot2")
install.packages("hexbin")

# For connecting to the database:
install.packages("RSQLite")

# For Cohen's d and Cliff's delta.
install.packages("effsize")

install.packages("R.utils")