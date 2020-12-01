A partir del tipo de _b_ se logra reducir el resto de los AUTO_TYPE a {Int}. 
Primero se reduce a _a_ al tipo B por ser el único con una función _met2_. Además
se reduce el tipo del parámetro _f_ a Int a partir del llamado de _met2_ con _b_ como entrada. 
Luego se puede reducir el retorno de _met2_ por estar ya _f_ reducido y en la segunda pasada 
se reduce el retorno de _met1_ a partir de la invocación de _met2_.