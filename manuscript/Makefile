# Build the manuscript. `make` -> main.pdf via pdflatex + bibtex.
# (latexmk is not required; this repo's TeX install is BasicTeX 2025.)
TEX = pdflatex -interaction=nonstopmode -halt-on-error

main.pdf: main.tex refs.bib $(wildcard figures/*.pdf)
	$(TEX) main
	-bibtex main
	$(TEX) main
	$(TEX) main

.PHONY: clean
clean:
	rm -f main.aux main.bbl main.blg main.log main.out main.pdf mainNotes.bib
