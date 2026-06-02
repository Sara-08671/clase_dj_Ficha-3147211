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

# --- Inline para ver/editar el Record dentro del User ---
class RecordInline(admin.StackedInline):
    model = Record
    can_delete = False
    verbose_name_plural = 'Informacion del usuario'
    readonly_fields = ('created_at',)
    fields = ('first_name', 'last_name', 'email', 'phone', 'Address', 'city', 'state', 'zipcode')
    extra = 0

# --- Admin personalizado para User con el Record embebido ---
class CustomUserAdmin(UserAdmin):
    inlines = (RecordInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    actions = ['create_record_action']

    def create_record_action(self, request, queryset):
        for user in queryset:
            Record.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                }
            )
        self.message_user(request, 'Records creados para usuarios seleccionados.')
    create_record_action.short_description = 'Crear Record para usuarios seleccionados'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)