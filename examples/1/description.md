Ejemlo sencillo, se reduce el tipo de la variable _x_ dentro de la
expresión LetIn a Int a partir de su valor de inicialización. Luego, el tipo
estático del let será el mismo del case, que estará dado por la unión
de los tipos de todos sus casos. En este ejemplo hay sólo un caso y este
tiene tipo estático IO, pues la función out_string tiene tipo estático
SELF_TYPE. Luego a partir del tipo del let se reduce el tipo de la función
main a IO, logrando una inferencia correcta.