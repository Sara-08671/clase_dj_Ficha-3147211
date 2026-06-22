# VISTAS DE NOTIFICACIONES SEGÚN ROL

## Administrador ({% extends "administrador/base.html" %})
- CRUD completo de notificaciones
- Envío con selector de usuario/destinatario
- Filtros por tipo y usuario
- Tabla de notificaciones enviadas

## Organizador ({% extends "organizador/base.html" %})
- Ver notificaciones sin acciones de edición/eliminación
- Filtros por estado (todas/no leídas/leídas)
- Bandeja de entrada solo lectura

## Residente ({% extends "residente/base.html" %})
- Ver solo notificaciones propias
- Filtrado simple
- Acción marcar como leída/no leída

# NOTA: Los templates comparten la lógica de negocio en views.py
# pero presentan UI diferente según el rol.