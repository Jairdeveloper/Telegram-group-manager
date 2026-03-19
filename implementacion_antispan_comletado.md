Fecha: 2026-03-19
version: v1.0
referencia: implementacion_antispan.md

Fase: 1
Objetivo fase: Modelo y storage.
Implementacion fase:
- app/manager_bot/_config/group_config.py
  - Se agregaron campos antispan para acciones, eliminacion, duraciones y excepciones:
    - Telegram: action, delete, mute/ban duration, toggles de usernames/bots, exceptions.
    - Reenvio: actions por origen, delete, mute/ban duration, exceptions.
    - Citas: actions por origen, delete, mute/ban duration, exceptions.
    - Internet: action, delete, mute/ban duration, exceptions.
  - Se ajusto from_dict para normalizar listas de excepciones cuando vienen en None.

Fase: 2
Objetivo fase: Menus y callbacks.
Implementacion fase:
- app/manager_bot/_menus/antispan_menu.py
  - Se creo el menu principal Antispan y submenus para Telegram, Reenvio, Citas e Internet.
  - Se agregaron submenus por origen (canales/grupos/usuarios/bots) y menus de duracion y excepciones.
- app/manager_bot/_menus/__init__.py
  - Se registraron los menus Antispan y submenus.
- app/manager_bot/_menus/main_menu.py
  - Se agrego acceso directo al menu Antispan (antispan:show).
- app/manager_bot/_features/antispan/__init__.py
  - Se implementaron callbacks para mostrar menus y actualizar acciones, eliminacion, toggles y duraciones.
- app/manager_bot/_menu_service.py
  - Se registro AntispanFeature en el servicio de menus.

Fase: 3
Objetivo fase: Conversacion y tests.
Implementacion fase:
- app/manager_bot/_menu_service.py
  - Se agregaron estados de conversacion para duraciones y excepciones de Antispan.
- app/manager_bot/_features/antispan/__init__.py
  - Se actualizo para setear estados al abrir menus de duracion y excepciones.
  - Se limpia estado al volver al menu principal Antispan.
- app/webhook/handlers.py
  - Se agrego manejo de mensajes para guardar duraciones y excepciones Antispan.
  - Se valida minimo 30 segundos y maximo 365 dias.
- tests/manager_bot/test_antispan_conversation.py
  - Tests de actualizacion de duraciones y excepciones.

Notas:
- No se ejecutaron tests en esta fase.
