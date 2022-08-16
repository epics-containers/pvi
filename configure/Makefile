# Makefile

TOP=..
include $(TOP)/configure/CONFIG

CFG += RULES_PVI

TARGETS = $(CONFIG_TARGETS)
CONFIGS += $(subst ../,,$(wildcard $(CONFIG_INSTALLS)))

include $(TOP)/configure/RULES
