# Creates the plots used in the paper.

# Hack! If it creates one plot, it creates all of them.
POWER_PLOTS = idle-power.pdf
ENERGY_PLOTS = idle-energy.pdf

PLOTS = $(POWER_PLOTS) $(ENERGY_PLOTS)
COMMON = common.R energy.sqlite

all: $(PLOTS)

$(POWER_PLOTS): power-plots.R $(COMMON)
	# Ignore this failure.
	-Rscript $<

$(ENERGY_PLOTS): ttesting.R $(COMMON)
	# Temporary! Ignore this failure.
	-Rscript $<

install: install.R
	Rscript install.R

.PHONY: all install
