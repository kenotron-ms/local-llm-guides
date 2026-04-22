# ── Local LLM Guides ──────────────────────────────────────────────────────────
# Usage:
#   make          — render all diagrams + regenerate mockup.html
#   make diagrams — re-render .dot → PNG only
#   make mockup   — regenerate mockup.html only
#   make clean    — remove all generated files

DOTS := $(wildcard diagrams/*.dot)
PNGS := $(DOTS:diagrams/%.dot=diagrams/rendered/%.png)

.PHONY: all diagrams mockup clean

all: diagrams mockup

# ── Diagrams ──────────────────────────────────────────────────────────────────

diagrams: $(PNGS)

diagrams/rendered/%.png: diagrams/%.dot
	@mkdir -p diagrams/rendered
	@dot -Tpng $< -o $@
	@echo "  ✓  $*"

# ── Mockup ────────────────────────────────────────────────────────────────────

mockup: mockup.html

mockup.html: $(PNGS) generate_mockup.py
	@python3 generate_mockup.py
	@echo "  ✓  mockup.html"

# ── Clean ─────────────────────────────────────────────────────────────────────

clean:
	@rm -f diagrams/rendered/*.png mockup.html
	@echo "  cleaned"
