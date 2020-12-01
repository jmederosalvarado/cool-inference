El tipo de retorno de _met1_ se reduce a partir del tipo de retorno 
de la función _met2_ del tipo B. Además se infiere el tipo de _a_ a 
partir de su uso como argumento de _met2_. En la primera pasada no se 
logra una reducción de _a_ pues _f_ todavía no ha sido reducido. Sin embargo,
durante la segunda pasada ya es posible.