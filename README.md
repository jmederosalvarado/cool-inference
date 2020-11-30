# Cool Inference

## Utilización

AL ejecutar la linea siguiente se imprimira en la terminal los detalles del
proceso de inferencia de tipos y chequeo semántico. Para una mejor visualización
de estos detalles, instalar [rich](https://github.com/willmcgugan/rich).
En la carpeta que contiene el archivo con el código se generara un nuevo archivo
que contiene el mismo código pero con los tipos ya inferidos. Se provee una carpeta
con ejemplos de programas de cool y la salida esperada.

```bash
python -m cool_inference <path to cool file>
```

## Detalles

### Inferencia de tipos

La inferencia de tipos en cool se realiza en una fase posterior al chequeo
semántico. A cada nodo con un identificador se le asocia una _bolsa de tipos_,
la cuales son similares a conjuntos. Estas bolsas de tipo indican cuales son
los posibles tipos que puede tener el atributo, método o parámetro al que se
asocia la bolsa. Al comienzo de esta fase se inicializan estas bolsas de
tipos, aquellas de los nodos con `AUTO_TYPE` contienen inicialmente todos los
tipos conocidos en el programa, y la del resto de los nodos, el tipo que
aparece en la declaración del mismo. Luego se procede a _reducir_ estas
bolsas de tipo a partir de operaciones de unión e intersección entre las
bolsas, de manera tal que al final de estas reducciones se permita tomar una
decisión acerca del tipo de estos nodos.

#### Valores especiales en las bolsas de tipos

Las bolsas de tipos pueden contener, además de los tipos que hasta el momento
pueden adoptar el nodo al cual esta está asociado, dos tipos especiales,
estos son:

- `@union`: indica que la bolsa de tipo actual fue resultado de una union
  entre varios tipos/bolsas. El valor `@union` se introduce en una bolsa la
  primera vez que esta se trata de reducir mediante su itersección con un
  conjunto de tipos, y esta intersección tiene tamaño 0. Esta situacón indica 
  que la bolsa no puede ser reducida, vea el caso siguiente:
  
  a : Int ;
  b : String ;
  c : AUTO_TYPE ;
  met() : AUTO_TYPE {
    {
      c <- a ;
      c <- b ;
    }
  }

  En este caso, la bolsa de _c_ es reducida a {Int}, por interceptar 
  {tipo_1, ... tipo_k, Int, tipo_k+2, ... tipo_n} con {Int}. Note que el primer 
  conjunto es el inicial de _c_, que posee a todos los tipos del programa por ser 
  AUTO_TYPE y el segundo es el de _a_.
  Luego se trata de reducir a la bolsa de _c_, actualmente de valor {Int} con la de
  _b_, de valor {String}. la intersección tendrá tamaño 0, lo que indica que no es 
  posible una reducción y que _c_ debe tener en sus bolsas tanto a Int como a String.
  Entonces se le da a _c_ el valor de la unión de {Int} y {String}, agregándole el
  tipo especial `@union`. A partir de aquí, ni Int, ni String, ni ningún otro tipo
  que entre en la bolsa podrá ser removido de esta y las operaciones de reducción se
  convertirán en uniones.


- `@lock`: utilizado en la inicialización de la bolsa de tipos de
  nodos no `AUTO_TYPE`. Este valor indica que la bolsa no puede ser reducida. Esto
  se utiliza para evitar expandir con uniones a los tipos que no son AUTO_TYPE y que
  por tanto no deberían cambiar.


#### El proceso completo
El proceso para inferir tipos y buscar errores semánticos en el código de cool consta de
3 fases, cada una con sus 3 fases propias.

- Primeramente se realiza un checkeo semántico que toma a AUTO_TYPE como un tipo especial
  que conformará a todos los demás tipos. Se usa patrón visitor para recorrer el ast tres veces,
  recogiendo, construyendo y checkeando tipos. Las dos primeras proveerán un contexto mientras
  que la última encontrará posibles errores que no tengan nada que ver con AUTO_TYPE. La segunda 
  fase sólo se realizará si esta primera no tiene errores.

- La segunda fase cuenta también con tres fases propias. Primero se construyen las bolsas de
  tipos de cada variable (atributos, parámetros de funciones, declaraciones de un LetIn o 
  declaraciones de un Case). Todas estas bolsas son almacenadas en una estructura TyBags que
  se ocupa de la inserción, búsqueda y modificación de estas. Esta sub-fase se llama BagsCollector.
  La segunda sub-fase se encargará de reducir lo más posible todas las bolsas. Se visitará
  cada nodo y se tomará decisiones de acuerdo sus características. Esta fase se continuará 
  ejecutando siempre que se realize algún tipo de cambio en las bolsas. Para entender el motivo
  de esto, vea la siguiente situación:

  a : Int ;
  b : AUTO_TYPE ;
  c : AUTO_TYPE ;
  met() : AUTO_TYPE {
    {
      c <- b ;
      b <- a ;
    }
  }
  
  Durante la primera ejecución, _c_ tratará de ser reducido a partir de la bolsa de _b_ que,
  por ser AUTO_TYPE tendrá inicialmente todos los tipos. Por tanto _c_ quedará igual y no será
  reducido. Luego _b_ se reduce a partir de _a_ que es Int, y por tanto se puede inferir que
  _b_ también será Int. Note que si no se realizara otra ejecución, _c_ quedaría sin inferirse
  como Int, a pesar de que esto sería posible pues el único valor que recibe es el de _b_ que
  se infirió también como Int. Al realizar la segunda ejecución _c_ se reducirá a partir de _b_
  que ya en este momento tiene sólo Int en su bolsa.

  Los métodos _visit_ de esta fase cuentan también con un parámetro llamado _restriction_ que 
  se utilizará para restringir ciertas visitas a los nodos. Vea la siguiente situación:

  a : Int ;
  b : AUTO_TYPE ;
  c : AUTO_TYPE ;
  met() : AUTO_TYPE {
    {
      {  
        c <- String ;
        b ;
      } + a 
    }
  }

  En este caso se está sumando una expresión de tipo Block, con _a_ de tipo Int. Note que las 
  expresiones Block tienen el tipo estático de la última de las expresiones que las conforman.
  En este caso esa última expresión es una expresión _id_, _b_. Al estar usando al Block en
  una suma, se puede inferir que su tipo estático, y por tanto el de _b_ debe tener valor Int.
  Para lograr que la bolsa de tipos de _b_ sea reducida a Int se pone en el valor _restriction_
  de la visita al block el conjunto {Int}. El visit de Block verá que el tamaño de su 
  _restriction_ es mayor que 0 y reducirá b (su última expresión) a partir de este.

  La última sub-fase recibe el nombre de BagsReplacer. Esta modificará el ast, cambiando todos
  los tipos AUTO_TYPE por el ancestro común más cercano de sus respectivas bolsas. Este
  ancestro común será el resultado de la inferencia (Note que como en _cool_ todos los tipos
  heredan de Object, en el peor caso éste será el ancestro).

- Finalmente se ejecuta la tercera fase. Esta será similar a la primera, con la diferencia de
  que el ast ya no contará con ningún AUTO_TYPE, todos estos habrán sido ya inferidos y
  sustituidos por sus respectivos tipos. Esta fase es necesaria para encontrar errores que
  se dejaron pasar en la primera por causa de los AUTO_TYPE.