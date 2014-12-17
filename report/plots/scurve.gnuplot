set term epslatex monochrome
set output 'scurve.eps'
set pointsize 2
set xrange[0:1]
set ylabel 'Probability of becoming a candidate pair'
set xlabel 'Jaccard similarity'
set size .75,.75
set key at 0.6,0.9
r1 = 25
b1 = 40
r2 = 20
b2 = 50
r3 = 10
b3 = 100
f(x) = 1-(1-x**r1)**b1
g(x) = 1-(1-x**r2)**b2
h(x) = 1-(1-x**r3)**b3
plot f(x) with lines linestyle 1 title 'r=25, b=40', \
    g(x) with lines  title 'r=20, b=50' linestyle 2, \
    h(x) with lines  title 'r=10, b=100' linestyle 3, \
    'scurve.dat' with points notitle

