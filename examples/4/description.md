En este caso se logra la inferencia de dos funciones que se invocan mutuamente.
Los tipos de los parámetros _a_, _b_ de _f_ son reducidos a Int en el momento en que
se utilizan en operaciones aritméticas al invocar a _g_. La expresión _if then elese_
tomará como tipo estático a la intercepción de los tipos posibles de sus expresiones
_then_ y _else_, pero como el _then_ es visitado antes que el _else_, durante esta pasada
_b_ todavía tendrá una bolsa sin reducir, al igual que el retorno del llamado a la función
_g_ cuya declaración no se ha visitado. Esto indica que en esta primera pasada el tipo de
retorno de la finción _f_ no es inferido aún.
Al visitar la declaración de la función _g_ se tiene exactamente la misma situación.
Como en la pasada anterior se realizaron cambios, se vuelve a hacer un recorrido de visitas 
por el ast. En esta ocación en _f_ tanto _a_ como _b_ tienen sus tipos reducidos a Int, por tanto 
la expresión _if then else_ tendrá un tipo estático Int dado por la intercepción de la bolsa
de b ({Int}) con la del llamado a la función _g_ ({Todos los tipos}).
Al visitar la declaración de _g_ se intersectará {Int} con {Int} ya que _f_ tiene su bolsa
de retorno reducida, logrando también una reducción correta.
