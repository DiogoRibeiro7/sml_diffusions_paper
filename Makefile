PAPER_DIR := paper

# latexmk drives the pdflatex/biber/pdflatex/pdflatex cycle and decides how many
# reruns are actually needed.  Invoking the passes by hand is fragile: a first
# pass that stops early can leave a truncated main.aux, which then breaks every
# later pass with a misleading "Missing \begin{document}".
LATEXMK := latexmk -pdf -interaction=nonstopmode -halt-on-error

.PHONY: all figures pdf paper verify clean

all: figures pdf

figures:
	python code/generate_results.py

# `pdf` is the primary name because `paper` is now a directory; `paper` is kept
# as a .PHONY alias so the documented command still works.
pdf:
	cd $(PAPER_DIR) && $(LATEXMK) main.tex

paper: pdf

# Regenerate every figure and table into a scratch directory and compare with
# the committed copies.  Figure output is timestamp-free, so this is exact.
verify:
	python code/verify_reproducibility.py

# -c removes auxiliary files but keeps main.pdf, which is tracked.
clean:
	cd $(PAPER_DIR) && latexmk -c main.tex
