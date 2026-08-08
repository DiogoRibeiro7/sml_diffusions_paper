PAPER_DIR := paper

# latexmk drives the pdflatex/biber/pdflatex/pdflatex cycle and decides how many
# reruns are actually needed.  Invoking the passes by hand is fragile: a first
# pass that stops early can leave a truncated main.aux, which then breaks every
# later pass with a misleading "Missing \begin{document}".
LATEXMK := latexmk -pdf -interaction=nonstopmode -halt-on-error

.PHONY: all figures pdf theory companion paper verify test check numbers phrases clean

all: figures pdf

figures:
	python code/generate_results.py

# Two documents since the split: the theory paper and the application companion.
# They share a preamble and a bibliography but neither input the other, so they
# build independently and in either order.
pdf: theory companion

theory:
	cd $(PAPER_DIR) && $(LATEXMK) main.tex

companion:
	cd $(PAPER_DIR) && $(LATEXMK) companion.tex

# `paper` is kept as a .PHONY alias so the documented command still works.
paper: pdf

# Regenerate every figure and table into a scratch directory and compare with
# the committed copies.  Figure output is timestamp-free, so this is exact.
verify:
	python code/verify_reproducibility.py

test:
	python -m pytest tests -q

# Fail if wording retracted in an earlier review round has reappeared.
phrases:
	python code/check_forbidden_phrases.py

# Fail if a manuscript table carries a number that no generator produces.
numbers:
	python code/check_table_numbers.py

check: test verify phrases numbers

# -c removes auxiliary files but keeps the PDFs, which are tracked.
clean:
	cd $(PAPER_DIR) && latexmk -c main.tex companion.tex
