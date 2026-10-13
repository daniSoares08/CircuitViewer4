# CircuitViewer4 - github.com/daniSoares08
# Open source (MIT License): free to use, copy, modify and redistribute.

NAME = CIRCVIE4
DESCRIPTION = "Circuit viewer 4"
COMPRESSED = YES
ARCHIVED = YES

SRC = src/main.c src/ui.c src/exercises.c src/search_overlay.c \
      src/appvar.c src/mna.c src/fmt.c src/engine.c src/narrate.c \
      src/narrate_ac.c src/narrate_power.c src/live_recipe.c

CFLAGS = -Wall -Wextra -Oz
LDFLAGS = -lgraphx -lkeypadc -lfileioc -ltice

include $(shell cedev-config --makefile)
