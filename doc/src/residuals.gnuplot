set logscale y
set title "Residuals"
set ylabel 'Residual'
set xlabel 'Iteration'
plot "< cat simpleFoam.log | grep 'Solving for Ux' | cut -d' ' -f9" title 'Ux' with lines,\
"< cat log | grep 'Solving for Uy' | cut -d' ' -f9" title 'Uy' with lines,\
"< cat log | grep 'Solving for Uz' | cut -d' ' -f9" title 'Uz' with lines,\
"< cat log | grep 'Solving for p' | cut -d' ' -f9 | tr -d ','" title 'p' with lines
pause 1
reread

