from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Record

# --- Admin para Record ---
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'city', 'state', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'city')
    list_filter = ('state', 'city', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

# --- Inline para ver el Record dentro del User ---
class RecordInline(admin.StackedInline):
    model = Record
    can_delete = False
    verbose_name_plural = 'Perfil del registro'
    readonly_fields = ('created_at',)

# --- Admin personalizado para User con el Record embebido ---
class CustomUserAdmin(UserAdmin):
    inlines = (RecordInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)