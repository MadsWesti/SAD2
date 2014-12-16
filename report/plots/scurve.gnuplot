set term epslatex monochrome
set output 'scurve.eps'
set pointsize 2
set xrange[0:1]
set ylabel 'Probability of becoming a candidate pair'
set xlabel 'Jaccard similarity'
set size .75,.75
set key at 0.4,0.9
r = 4.0
b = 16.0
r2 = 10.0
b2 = 10.0
f(x) = 1-(1-x**r)**b
g(x) = 1-(1-x**r2)**b2
plot f(x) with lines linestyle 1 title 'r=4, b=16', \
    g(x) with lines  title 'r=10, b=10' linestyle 2

