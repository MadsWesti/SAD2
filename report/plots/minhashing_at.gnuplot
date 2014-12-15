set term epslatex monochrome
set output 'minhashing_at.eps'
set pointsize 2
set xrange[0:9]
set ylabel 'Time (s)'
set xlabel 'Input data size (x100 movies | x1000 roles)'
set key at 4,300
plot 'minhashing_at.dat' u 1:2 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:2 title 'k=5' w points, \
    'minhashing_at.dat' u 1:3 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:3 title 'k=10' w points, \
    'minhashing_at.dat' u 1:4 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:4 title 'k=20' w points, \
    'minhashing_at.dat' u 1:5 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:5 title 'k=40' w points
