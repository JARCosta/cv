# Force latexmk to use XeLaTeX for PDF generation
$pdflatex = 'xelatex -interaction=nonstopmode -synctex=1 %O %S';
$pdf_mode = 1;
# Clean auxiliary files more aggressively on -C
$clean_ext .= ' %R.out %R.log %R.aux %R.fls %R.fdb_latexmk';

# Use XeLaTeX
$xelatex = 'xelatex -interaction=nonstopmode -synctex=1 %O %S';
# Send all outputs (pdf, aux, log, etc.) to ./out
$out_dir = 'out';
$aux_dir = 'out';
# Ensure engine receives output dir
$xelatex =~ s/%O/-output-directory=$out_dir %O/;