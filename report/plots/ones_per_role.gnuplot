set term epslatex monochrome
set output 'ones_per_role.eps'
set pointsize 2
set xrange[0:10]
set ylabel 'Average movies per role'
set xlabel 'minimum rank'
unset key
plot 'ones_per_role.dat' u 1:($2/$3) smooth csplines with lines, \
    'ones_per_role.dat' u 1:($2/$3) w points
