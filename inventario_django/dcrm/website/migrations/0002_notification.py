from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_or_update_notificacion_table(apps, schema_editor):
    table_name = 'website_notificacion'
    cursor = schema_editor.connection.cursor()

    cursor.execute('SHOW TABLES LIKE %s', [table_name])
    exists = bool(cursor.fetchone())

    if not exists:
        Notificacion = apps.get_model('website', 'Notificacion')
        schema_editor.create_model(Notificacion)

    cursor.execute(f'SHOW COLUMNS FROM `{table_name}`')
    columns = {row[0] for row in cursor.fetchall()}

    if 'leido' in columns and 'leida' not in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` CHANGE COLUMN `leido` `leida` tinyint(1) NOT NULL')
    if 'fecha_creacion' in columns and 'created_at' not in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` CHANGE COLUMN `fecha_creacion` `created_at` datetime(6) NOT NULL')
    if 'usuario_id' in columns and 'receptor_id' not in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` CHANGE COLUMN `usuario_id` `receptor_id` int(11) NULL')

    if 'titulo' in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` MODIFY COLUMN `titulo` varchar(80) NOT NULL')
    if 'receptor_id' in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` MODIFY COLUMN `receptor_id` int(11) NULL')

    if 'tipo' not in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` ADD COLUMN `tipo` varchar(20) NOT NULL DEFAULT \'info\' AFTER `id`')

    if 'creador_id' not in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` ADD COLUMN `creador_id` int(11) NULL AFTER `receptor_id`')

    if 'leida_en' not in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` ADD COLUMN `leida_en` datetime(6) NULL AFTER `leida`')

    if 'updated_at' not in columns:
        schema_editor.execute(f'ALTER TABLE `{table_name}` ADD COLUMN `updated_at` datetime(6) NULL AFTER `created_at`')

    constraints = schema_editor.connection.introspection.get_constraints(cursor, table_name)
    old_fk = 'website_notificacion_usuario_id_3251cf4a_fk_auth_user_id'
    receptor_fk = 'website_notificacion_receptor_id_fk'
    creador_fk = 'website_notificacion_creador_id_fk'
    receptor_index = 'website_notificacion_receptor_id_idx'
    creador_index = 'website_notificacion_creador_id_idx'

    for constraint_name in [old_fk, receptor_fk, creador_fk]:
        if constraint_name in constraints and constraints[constraint_name].get('foreign_key'):
            schema_editor.execute(f'ALTER TABLE `{table_name}` DROP FOREIGN KEY `{constraint_name}`')

    for index_name, definition in constraints.items():
        if definition.get('columns') in (['receptor_id'], ['creador_id']) and definition.get('index'):
            schema_editor.execute(f'ALTER TABLE `{table_name}` DROP INDEX `{index_name}`')

    constraints = schema_editor.connection.introspection.get_constraints(cursor, table_name)
    if receptor_fk not in constraints:
        schema_editor.execute(
            f'ALTER TABLE `{table_name}` ADD CONSTRAINT `{receptor_fk}` '
            f'FOREIGN KEY (`receptor_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE'
        )
    if creador_fk not in constraints:
        schema_editor.execute(
            f'ALTER TABLE `{table_name}` ADD CONSTRAINT `{creador_fk}` '
            f'FOREIGN KEY (`creador_id`) REFERENCES `auth_user` (`id`) ON DELETE SET NULL'
        )

    indexes = schema_editor.connection.introspection.get_constraints(cursor, table_name)
    if receptor_index not in indexes:
        schema_editor.execute(f'ALTER TABLE `{table_name}` ADD INDEX `{receptor_index}` (`receptor_id`)')
    if creador_index not in indexes:
        schema_editor.execute(f'ALTER TABLE `{table_name}` ADD INDEX `{creador_index}` (`creador_id`)')


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(create_or_update_notificacion_table, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.CreateModel(
                    name='Notificacion',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('tipo', models.CharField(choices=[('info', 'Informativa'), ('aviso', 'Aviso'), ('alerta', 'Alerta'), ('recordatorio', 'Recordatorio')], default='info', max_length=20)),
                        ('titulo', models.CharField(max_length=80)),
                        ('mensaje', models.TextField()),
                        ('leida', models.BooleanField(default=False)),
                        ('leida_en', models.DateTimeField(blank=True, null=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('creador', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notificaciones_creadas', to=settings.AUTH_USER_MODEL)),
                        ('receptor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'ordering': ['-created_at'],
                    },
                ),
            ],
        ),
    ]
