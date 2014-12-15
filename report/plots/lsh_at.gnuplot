set term epslatex monochrome
set output 'lsh_at.eps'
set pointsize 2
set xrange[0:5]
set ylabel 'Time (s)'
set xlabel 'x10 bands | x30 hashes)'
set title "imdb-r.txt with min_rank = 7.0"
unset key
plot 'lsh_at.dat' u 1:2 smooth csplines with lines, \
    'lsh_at.dat' u 1:2 w points, \
