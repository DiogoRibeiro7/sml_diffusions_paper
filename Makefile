.PHONY: all figures paper clean

all: figures paper

figures:
	python code/generate_results.py

paper:
	pdflatex -interaction=nonstopmode -halt-on-error main.tex
	biber main
	pdflatex -interaction=nonstopmode -halt-on-error main.tex
	pdflatex -interaction=nonstopmode -halt-on-error main.tex

clean:
	rm -f main.aux main.bbl main.bcf main.blg main.log main.out main.run.xml main.fdb_latexmk main.fls
