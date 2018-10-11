# Generated by Django 2.1 on 2018-09-26 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OCPUsageLineItem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('namespace', models.CharField(max_length=253)),
                ('pod', models.CharField(max_length=253)),
                ('node', models.CharField(max_length=253)),
                ('usage_start', models.DateTimeField()),
                ('usage_end', models.DateTimeField()),
                ('pod_usage_cpu_core_seconds', models.DecimalField(decimal_places=5, max_digits=17, null=True)),
                ('pod_usage_memory_seconds', models.DecimalField(decimal_places=5, max_digits=17, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OCPUsageLineItemDaily',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('namespace', models.CharField(max_length=253)),
                ('pod', models.CharField(max_length=253)),
                ('node', models.CharField(max_length=253)),
                ('usage_start', models.DateTimeField()),
                ('usage_end', models.DateTimeField()),
                ('pod_usage_cpu_core_seconds', models.DecimalField(decimal_places=5, max_digits=17, null=True)),
                ('pod_usage_memory_seconds', models.DecimalField(decimal_places=5, max_digits=17, null=True)),
            ],
            options={
                'db_table': 'reporting_ocpusagelineitem_daily',
            },
        ),
        migrations.CreateModel(
            name='OCPUsageLineItemDailySummary',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('namespace', models.CharField(max_length=253)),
                ('pod', models.CharField(max_length=253)),
                ('node', models.CharField(max_length=253)),
                ('usage_start', models.DateTimeField()),
                ('usage_end', models.DateTimeField()),
                ('pod_usage_cpu_core_seconds', models.DecimalField(decimal_places=5, max_digits=17, null=True)),
                ('pod_usage_memory_seconds', models.DecimalField(decimal_places=5, max_digits=17, null=True)),
            ],
            options={
                'db_table': 'reporting_ocpusagelineitem_daily_summary',
            },
        ),
        migrations.CreateModel(
            name='OCPUsageReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interval_start', models.DateTimeField()),
                ('interval_end', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='OCPUsageReportPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cluster_id', models.CharField(max_length=50)),
                ('report_period_start', models.DateTimeField()),
                ('report_period_end', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='ocpusagereport',
            name='report_period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reporting.OCPUsageReportPeriod'),
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
        migrations.AddIndex(
            model_name='ocpusagelineitemdaily',
            index=models.Index(fields=['usage_start'], name='ocp_usage_idx'),
        ),
        migrations.AddIndex(
            model_name='ocpusagelineitemdaily',
            index=models.Index(fields=['namespace'], name='namespace_idx'),
        ),
        migrations.AddIndex(
            model_name='ocpusagelineitemdaily',
            index=models.Index(fields=['pod'], name='pod_idx'),
        ),
        migrations.AddIndex(
            model_name='ocpusagelineitemdaily',
            index=models.Index(fields=['node'], name='node_idx'),
        ),
        migrations.AddField(
            model_name='ocpusagelineitem',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reporting.OCPUsageReport'),
        ),
        migrations.AddField(
            model_name='ocpusagelineitem',
            name='report_period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reporting.OCPUsageReportPeriod'),
        ),
        migrations.AddIndex(
            model_name='ocpusagereport',
            index=models.Index(fields=['interval_start'], name='ocp_interval_start_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='ocpusagelineitem',
            unique_together={('report', 'namespace', 'pod', 'node')},
        ),
    ]