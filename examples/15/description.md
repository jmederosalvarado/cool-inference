En este caso no se logra inferir el tipo de _a_ a algo distinto de Object.
La asignación de _b_ reduce la bolsa de _a_ a {String}. Sin embargo, como 
la asignación está dentro de una expresión paréntesis y esa a la vez está siendo
sumada en una expresión aritmética, le llega una restricción de Int que expande su
bolsa a {String, Int, @union}.