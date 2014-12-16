set term epslatex monochrome
set output 'minhashing_at.eps'
set pointsize 2
set xrange[0:9]
set yrange[0:200]
set ylabel 'Time (s)'
set xlabel 'Input data size (x100 movies | x1000 actors)'
set key at 6,190
plot 'minhashing_at.dat' u 1:2 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:2 title 'k=3' w points, \
    'minhashing_at.dat' u 1:3 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:3 title 'k=5' w points, \
    'minhashing_at.dat' u 1:4 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:4 title 'k=10' w points, \
    'minhashing_at.dat' u 1:5 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:5 title 'k=20' w points, \
    'naive_at.dat' u 1:2 notitle smooth csplines with lines, \
    'naive_at.dat' u 1:2 title 'naive' w points
