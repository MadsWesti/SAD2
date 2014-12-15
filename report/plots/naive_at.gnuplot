set term epslatex monochrome
set output 'naive_at.eps'
set pointsize 2
set xrange[0:9]
set ylabel 'Time (s)'
set xlabel 'Input data size (x100 movies | x1000 roles)'
unset key
plot 'naive_at.dat' u 1:2 smooth csplines with lines, \
    'naive_at.dat' u 1:2 w points, \
    'naive_at.dat' u 1:3 smooth csplines with lines, \
    'naive_at.dat' u 1:3 w points
