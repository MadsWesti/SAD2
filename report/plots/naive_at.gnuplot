set term epslatex monochrome
set output 'naive_at.eps'
set pointsize 2
set xrange[0:5]
set ylabel 'Time (s)'
set xlabel 'Input data size (x100 movies | x1000 actors)'
unset key
plot 'naive_at.dat' u 1:2 smooth csplines with lines, \
    'naive_at.dat' u 1:2 w points
