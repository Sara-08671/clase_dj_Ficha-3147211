# Django CRM - Sistema de Gestión de Inventario

## Descripción
Sistema CRM desarrollado en Django con módulo de notificaciones, roles de usuario, CRUD de registros y recursos locales de Bootstrap.

## Roles y acceso
- **Administrador**: usuario con `is_superuser=True`. Accede a crear, editar y eliminar usuarios; gestiona todas las notificaciones; ve todos los registros.
- **Organizador**: usuario con `is_staff=True` o perteneciente al grupo `Organizador`. Tiene permisos de gestión equivalentes al administrador en el módulo actual.
- **Residente**: usuario normal. Solo ve y gestiona sus propios registros; no puede crear, editar ni eliminar usuarios ni notificaciones globales.

## Características
- Login con control de acceso por roles.
- CRUD completo de usuarios/registros.
- CRUD de notificaciones para administrador y organizador.
- Navegación SPA parcial en el módulo de notificaciones con secciones ocultas por JavaScript.
- Alertas visuales con mensajes de Django y Bootstrap.
- Validaciones con expresiones regulares en login y formularios.
- Campos críticos con caracteres restringidos para usuario/correo y contraseña.
- Bootstrap local instalado en `website/templates/static/css/bootstrap.min.css` y `website/templates/static/js/bootstrap.bundle.min.js`.
- Recursos externos CDN eliminados para Bootstrap/HTMX; el proyecto no depende de CDNs para Bootstrap.

## 4 capas de seguridad implementadas
1. **Autenticación obligatoria**: vistas protegidas con `login_required`.
2. **Control de roles**: decorador `admin_required` para administrador/organizador.
3. **Validaciones de entrada**: expresiones regulares en `views.py` y `forms.py`.
4. **Protección web y sesión**: CSRF tokens, métodos HTTP restringidos con `require_GET`/`require_POST`, ORM de Django, cookies de sesión y expiración al cerrar navegador.

## Instalación
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py crear_roles_demo
python manage.py runserver
```

Después de ejecutar `crear_roles_demo`, use estas cuentas para demostrar los roles:
- Administrador: `admin_demo` / `Admin12345`
- Organizador: `organizador_demo` / `Organizador12345`
- Residente: `residente_demo` / `Residente12345`

## Dependencias principales
- Django>=5.0,<5.1
- mysqlclient>=2.2.4
- reportlab>=4.0.0
- weasyprint>=61.0
- python-dotenv>=1.0.0
- django-validators>=0.0.1

## Arquitectura y modelado
- Diagrama C4: `diagrams/c4_model.puml`
- Diagrama UML de notificaciones: `diagrams/notificaciones_uml.puml`

## Patrones y prácticas documentadas
- **ModelForm/Formularios basados en modelo**: `RegistroForm`, `AddRecordForm` y `NotificacionForm` reutilizan validación y renderizado desde modelos, aplicando DRY.
- **Decorator**: `admin_required` centraliza validación de roles para vistas protegidas.
- **Manager/Repository**: `NotificacionManager.para_usuario()` encapsula la consulta de notificaciones por usuario.
- **Adapter/Admin**: `admin.py` adapta modelos al panel administrativo de Django con listas, filtros y acciones.
