PAPER_DIR := paper

# latexmk drives the pdflatex/biber/pdflatex/pdflatex cycle and decides how many
# reruns are actually needed.  Invoking the passes by hand is fragile: a first
# pass that stops early can leave a truncated main.aux, which then breaks every
# later pass with a misleading "Missing \begin{document}".
LATEXMK := latexmk -pdf -interaction=nonstopmode -halt-on-error

.PHONY: all figures pdf clean

all: figures pdf

figures:
	python code/generate_results.py

# `pdf` rather than `paper`, which is now a directory name.
pdf:
	cd $(PAPER_DIR) && $(LATEXMK) main.tex

# -c removes auxiliary files but keeps main.pdf, which is tracked.
clean:
	cd $(PAPER_DIR) && latexmk -c main.tex
