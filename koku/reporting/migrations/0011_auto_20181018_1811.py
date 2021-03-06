# Generated by Django 2.1.2 on 2018-10-18 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0010_auto_20181017_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='OCPUsageLineItemDailySummary',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('cluster_id', models.CharField(max_length=50, null=True)),
                ('namespace', models.CharField(max_length=253)),
                ('pod', models.CharField(max_length=253)),
                ('node', models.CharField(max_length=253)),
                ('usage_start', models.DateTimeField()),
                ('usage_end', models.DateTimeField()),
                ('pod_usage_cpu_core_hours', models.DecimalField(decimal_places=6, max_digits=24, null=True)),
                ('pod_request_cpu_core_hours', models.DecimalField(decimal_places=6, max_digits=24, null=True)),
                ('pod_limit_cpu_cores', models.DecimalField(decimal_places=6, max_digits=24, null=True)),
                ('pod_usage_memory_gigabytes', models.DecimalField(decimal_places=6, max_digits=24, null=True)),
                ('pod_request_memory_gigabytes', models.DecimalField(decimal_places=6, max_digits=24, null=True)),
                ('pod_limit_memory_gigabytes', models.DecimalField(decimal_places=6, max_digits=24, null=True)),
            ],
            options={
                'db_table': 'reporting_ocpusagelineitem_daily_summary',
            },
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemaggregates',
            old_name='pod_limit_memory_bytes',
            new_name='pod_limit_memory_gigabytes',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemaggregates',
            old_name='pod_request_cpu_core_seconds',
            new_name='pod_request_cpu_core_hours',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemaggregates',
            old_name='pod_request_memory_byte_seconds',
            new_name='pod_request_memory_gigabytes',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemaggregates',
            old_name='pod_usage_cpu_core_seconds',
            new_name='pod_usage_cpu_core_hours',
        ),
        migrations.RenameField(
            model_name='ocpusagelineitemaggregates',
            old_name='pod_usage_memory_byte_seconds',
            new_name='pod_usage_memory_gigabytes',
        ),
        migrations.AddField(
            model_name='ocpusagelineitemdaily',
            name='total_seconds',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='ocpusagelineitemdailysummary',
            index=models.Index(fields=['usage_start'], name='summary_ocp_usage_idx'),
        ),
        migrations.AddIndex(
            model_name='ocpusagelineitemdailysummary',
            index=models.Index(fields=['namespace'], name='summary_namespace_idx'),
        ),
        migrations.AddIndex(
            model_name='ocpusagelineitemdailysummary',
            index=models.Index(fields=['pod'], name='summary_pod_idx'),
        ),
        migrations.AddIndex(
            model_name='ocpusagelineitemdailysummary',
            index=models.Index(fields=['node'], name='summary_node_idx'),
        ),
    ]
