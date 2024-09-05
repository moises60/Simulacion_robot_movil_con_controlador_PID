Algoritmos y Técnicas Implementadas
Modelo Cinemático de un Robot Móvil Diferencial
El robot simulado utiliza un modelo cinemático diferencial, que es típico de robots con dos ruedas motrices independientes. 
Este modelo define cómo se mueven los robots en función de la velocidad angular de cada rueda y la orientación del robot en el espacio. 
A partir de las velocidades de las ruedas, el robot puede avanzar en línea recta o girar para corregir su orientación hacia un objetivo.

Control PID para la Orientación del Robot
El movimiento del robot se controla mediante un Controlador PID, que ajusta la orientación del robot hacia el objetivo. 
El controlador PID toma el error angular y lo utiliza para calcular una corrección de la velocidad angular. 
Esto permite que el robot ajuste su dirección de manera suave, evitando giros bruscos y oscilaciones.

Planificación de Ruta con el Algoritmo A*
Para que el robot pueda moverse hacia el objetivo de manera eficiente, se implementa el algoritmo A* para la planificación de rutas.
Este algoritmo utiliza una heurística para evaluar qué nodos son los más prometedores y encontrar la ruta óptima. 
A* garantiza que el robot elija el camino más corto hacia su destino.


