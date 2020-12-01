En este caso _b_ no logra ser inferido a algo más preciso que Object.
Se reduce primeramente a _b_ a {String}, para luego expandirlo a 
{String, Bool, @union} que ya no podrá ser reducido nuevamente. Como el ancestro
común más cercano de String y Bool es Object, a esto se logra inferir.
Además se logra una correcta reducción de _c_ por ser la últa expresión de un 
block siendo usado en una suma. Antes de visitar al block se le pasa una restricción
de {Int}.