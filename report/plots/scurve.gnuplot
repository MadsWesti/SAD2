set term epslatex monochrome
set output 'scurve.eps'
set pointsize 2
set xrange[0:1]
set ylabel 'Probability of becoming a candidate pair'
set xlabel 'Jaccard similarity'
set size .75,.75
unset key
r = 4.0
b = 16.0
f(x) = 1-(1-x**r)**b
plot f(x) with lines linestyle 1

