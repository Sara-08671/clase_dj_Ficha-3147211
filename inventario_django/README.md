# Django CRM - Sistema de Gestión de Inventario

## Descripción
Sistema CRM con módulo de notificaciones, roles de usuario y gestión de inventario.

## Características
- Login con roles diferenciados
- CRUD completo de usuarios
- Navegación SPA con menú sidebar
- Notificaciones con alertas visuales
- Validaciones con expresiones regulares
- 4 capas de seguridad implementadas

## Instalación

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Dependencias (requirements.txt)
- Django>=5.0,<5.1
- mysqlclient>=2.2.4
- reportlab>=4.0.0
- weasyprint>=61.0
- python-dotenv>=1.0.0
- django-validators>=0.0.1