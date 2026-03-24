Seleccionar acciones que limitar por la noche.

Estado: 📸 Eliminar multimedia
 ├ Activo entre las horas 23 a 9
 └ Anuncios de inicio y fin: ✔️

Hora actual: 24 mar 2026, 11:39

- Menus: 

- Apagado/encendido : Menu para establecer el estado del menu.
- Eliminar multimedia: Menu para establecer el estado del menu modo eliminar multimedia.
- Silencio Global: Menu para establecer el estado del menu en modo silencio global.
- Establecer franja horaria : Menu para establecer el horario en el se apagara/encendera El modo nocturno. Con submenu para:
    - Matriz de 5 x 4 de numero del 0 al 23 que representa una hora cada dia del dia.

- Descripcion de funcionalidad del menu:

- El encabezado debe tener forma de tree en la cual tiene dos opciones.
    - El estado : nodo padre que representa el estado global del modo nocturno. con descripcion dinamica establecida de acuerdo al modo que este establecido: "Eliminacion multimedia" o "Silencio global"
    - activo entre las horas : nodo hijo que representa el estado de la configuracion establecida en el menu "Establecer franja horaria". el estado/descripcion que representa el horario que represenhta la franja horaria que estara activo el modo nocturno debe ser dinamico.

- Descripcion de funcionalidad de retorno esperada. 
    - Se espera que el nodo padre actualice el estado del modo nocturo (On/off)
    - Los nodos hijos Eliminar multimedia y Silencio global actualice el estado en modo "Eliminar multimedia" o "Silencio global", 
    - los  submenu "Hora de inicio" y "Hora de fin" en el menu "franja horaria" retornar la matriz horas para setear el horario de inicio/fin, se espera que setee el horario de inicio/fin, Actualmente retornar "falta de datos".