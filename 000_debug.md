Mirando el código de nuevo:
- El menú genera "antispam:toggle" 
- El handler registrado es con `register_callback("antispam:toggle", handle_toggle)`
- Esto genera el patrón `^antispam:toggle(:.*)?$`
- El callback_data "antispam:toggle" debería hacer match porque `(:.*)?` es opcional
Entonces el pattern matching debería funcionar, pero hay un problema: el handler espera un valor "on" o "off" pero el callback_data no lo incluye.