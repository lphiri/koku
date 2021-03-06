# Generated by Django 2.1.2 on 2018-11-21 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0016_delete_rate'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ocpusagelineitem',
            old_name='pod_limit_cpu_cores',
            new_name='pod_limit_cpu_core_seconds',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitem',
            old_name='pod_limit_memory_bytes',
            new_name='pod_limit_memory_byte_seconds',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemaggregates',
            old_name='pod_limit_cpu_cores',
            new_name='pod_limit_cpu_core_hours',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemdaily',
            old_name='pod_limit_cpu_cores',
            new_name='pod_limit_cpu_core_seconds',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemdaily',
            old_name='pod_limit_memory_bytes',
            new_name='pod_limit_memory_byte_seconds',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemdailysummary',
            old_name='pod_limit_cpu_cores',
            new_name='pod_limit_cpu_core_hours',
        ),
    ]
