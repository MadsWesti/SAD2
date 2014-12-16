set term epslatex monochrome
set output 'sparseness.eps'
set pointsize 2
set xrange[0:378]
set yrange[0:500]
set ylabel 'Role count'
set xlabel 'Appearances'
unset key
plot 'sparseness.dat' u 1:2 notitle smooth csplines with lines, \
    'sparseness.dat' u 1:2 notitle w points
