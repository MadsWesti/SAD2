set term epslatex monochrome
set output 'lsh_at.eps'
set pointsize 2
set xrange[0:9]
set yrange[0:50]
set ylabel 'Time (s)'
set xlabel 'x100 movies | x1000 actors'
set key at 9,45
plot 'lsh_at.dat' u 1:2 notitle smooth csplines with lines, \
    'lsh_at.dat' u 1:2 title 'b=10, r=2' w points, \
    'lsh_at.dat' u 1:3 notitle smooth csplines with lines, \
    'lsh_at.dat' u 1:3 title 'b=10, r=5' w points, \
    'lsh_at.dat' u 1:4 notitle smooth csplines with lines, \
    'lsh_at.dat' u 1:4 title 'b=25, r=2' w points, \
    'minhashing_at.dat' u 1:4 notitle smooth csplines with lines, \
    'minhashing_at.dat' u 1:4 title 'MinHash k=10' w points, \
    'naive_at.dat' u 1:2 notitle smooth csplines with lines, \
    'naive_at.dat' u 1:2 title 'naive' w points, \
