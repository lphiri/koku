#
# Copyright 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Test the OCPReportQueryHandler base class."""
import hashlib
import random
from decimal import Decimal
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from django.db.models import DecimalField, ExpressionWrapper, F, Max, Sum
from faker import Faker
from tenant_schemas.utils import tenant_context

from api.utils import DateHelper
from reporting.models import (OCPUsageLineItem,
                              OCPUsageLineItemAggregates,
                              OCPUsageLineItemDaily,
                              OCPUsageLineItemDailySummary,
                              OCPUsageReport,
                              OCPUsageReportPeriod)
from reporting_common.models import CostUsageReportManifest, CostUsageReportStatus


class OCPReportDataGenerator:
    """Populate the database with OCP report data."""

    def __init__(self, tenant, current_month_only=False, dated_tags=None):
        """Set up the class."""
        self.tenant = tenant
        self.fake = Faker()
        self.dh = DateHelper()
        self.dated_tags = True if dated_tags is None or dated_tags is True else False

        self.today = self.dh.today
        self.one_month_ago = self.today - relativedelta(months=1)

        self.last_month = self.dh.last_month_start

        if current_month_only:
            report_days = 10
            first_of_month = self.today.replace(microsecond=0, second=0, minute=0, day=1)
            diff_from_first = self.today - first_of_month
            if diff_from_first.days < 10:
                report_days = 1 + diff_from_first.days
            self.period_ranges = [
                (self.dh.this_month_start, self.dh.this_month_end),
            ]
            self.report_ranges = [
                (self.today - relativedelta(days=i) for i in range(report_days)),
            ]

        else:
            self.period_ranges = [
                (self.dh.last_month_start, self.dh.last_month_end),
                (self.dh.this_month_start, self.dh.this_month_end),
            ]

            self.report_ranges = [
                (self.one_month_ago - relativedelta(days=i) for i in range(10)),
                (self.today - relativedelta(days=i) for i in range(10)),
            ]

    def create_manifest_entry(self, billing_period_start, provider_id):
        """Populate a report manifest entry."""
        manifest_creation_datetime = billing_period_start + relativedelta(days=random.randint(1, 27))
        manifest_updated_datetime = manifest_creation_datetime + relativedelta(days=random.randint(1, 2))
        data = {
            'assembly_id': uuid4(),
            'manifest_creation_datetime': manifest_creation_datetime,
            'manifest_updated_datetime': manifest_updated_datetime,
            'billing_period_start_datetime': billing_period_start,
            'num_processed_files': 1,
            'num_total_files': 1,
            'provider_id': provider_id
        }
        manifest_entry = CostUsageReportManifest(**data)
        manifest_entry.save()
        return manifest_entry

    def create_report_status_entry(self, billing_period_start, manifest_id):
        """Populate a report status entry."""
        etag_hasher = hashlib.new('ripemd160')
        etag_hasher.update(bytes(str(billing_period_start), 'utf-8'))
        ocp_etag = etag_hasher.hexdigest()

        last_started_datetime = billing_period_start + relativedelta(days=random.randint(1, 3))
        last_completed_datetime = last_started_datetime + relativedelta(days=1)
        data = {
            'report_name': uuid4(),
            'last_completed_datetime': last_completed_datetime,
            'last_started_datetime': last_started_datetime,
            'etag': ocp_etag,
            'manifest_id': manifest_id,
        }
        status_entry = CostUsageReportStatus(**data)
        status_entry.save()
        return status_entry

    def add_data_to_tenant(self, provider_id=None):
        """Populate tenant with data."""
        self.cluster_id = self.fake.word()
        self.namespaces = [self.fake.word() for _ in range(2)]
        self.nodes = [self.fake.word() for _ in range(2)]
        self.line_items = [
            {
                'namespace': random.choice(self.namespaces),
                'node': node,
                'pod': self.fake.word()
            }
            for node in self.nodes
        ]
        with tenant_context(self.tenant):
            for i, period in enumerate(self.period_ranges):
                report_period = self.create_ocp_report_period(period, provider_id)
                if provider_id:
                    manifest_entry = self.create_manifest_entry(report_period.report_period_start, provider_id)
                    self.create_report_status_entry(manifest_entry.billing_period_start_datetime, manifest_entry.id)
                for report_date in self.report_ranges[i]:
                    report = self.create_ocp_report(
                        report_period,
                        report_date
                    )
                    self.create_line_items(report_period, report)

            self._populate_daily_table()
            self._populate_daily_summary_table()
            self._populate_charge_info()

    def remove_data_from_tenant(self):
        """Remove the added data."""
        with tenant_context(self.tenant):
            for table in (OCPUsageLineItem,
                          OCPUsageLineItemAggregates,
                          OCPUsageLineItemDaily,
                          OCPUsageLineItemDailySummary,
                          OCPUsageReport,
                          OCPUsageReportPeriod):
                table.objects.all().delete()

    def remove_data_from_reporting_common(self):
        """Remove the public report statistics."""
        for table in (CostUsageReportManifest,
                      CostUsageReportStatus):
            table.objects.all().delete()

    def create_ocp_report_period(self, period, provider_id=1):
        """Create the OCP report period DB rows."""
        data = {
            'cluster_id': self.cluster_id,
            'report_period_start': period[0],
            'report_period_end': period[1],
            'summary_data_creation_datetime': self.dh._now,
            'summary_data_updated_datetime': self.dh._now,
            'provider_id': provider_id
        }
        report_period = OCPUsageReportPeriod(**data)
        report_period.save()
        return report_period

    def create_ocp_report(self, period, interval_start):
        """Create the OCP report DB rows."""
        data = {
            'interval_start': interval_start,
            'interval_end': interval_start,
            'report_period': period
        }

        report = OCPUsageReport(**data)
        report.save()
        return report

    def _gen_pod_labels(self, report):
        """Create pod labels for output data."""
        apps = [self.fake.word(), self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                self.fake.word(), self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        organizations = [self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                         self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        markets = [self.fake.word(), self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                   self.fake.word(), self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        versions = [self.fake.word(), self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                    self.fake.word(), self.fake.word(), self.fake.word()]  # pylint: disable=no-member

        seeded_labels = {'environment': ['dev', 'ci', 'qa', 'stage', 'prod'],
                         'app': apps,
                         'organization': organizations,
                         'market': markets,
                         'version': versions
                         }
        gen_label_keys = [self.fake.word(), self.fake.word(), self.fake.word(),  # pylint: disable=no-member
                          self.fake.word(), self.fake.word(), self.fake.word()]  # pylint: disable=no-member
        all_label_keys = list(seeded_labels.keys()) + gen_label_keys
        num_labels = random.randint(2, len(all_label_keys))
        chosen_label_keys = random.choices(all_label_keys, k=num_labels)

        labels = {}
        for label_key in chosen_label_keys:
            label_value = self.fake.word()  # pylint: disable=no-member
            if label_key in seeded_labels:
                label_value = random.choice(seeded_labels[label_key])
            if self.dated_tags:
                labels['{}-{}-{}*{}_label'.format(report.interval_start.month,
                                                  report.interval_start.day,
                                                  report.interval_start.year,
                                                  label_key)] = label_value
            else:
                labels['{}_label'.format(label_key)] = label_value

        return labels

    def create_line_items(self, report_period, report):
        """Create OCP hourly usage line items."""
        node_cpu_cores = random.randint(1, 8)
        node_memory_gb = random.randint(4, 32)
        for row in self.line_items:
            data = {
                'report_period': report_period,
                'report': report,
                'namespace': row.get('namespace'),
                'pod': row.get('pod'),
                'node': row.get('node'),
                'pod_usage_cpu_core_seconds': Decimal(random.uniform(0, 3600)),
                'pod_request_cpu_core_seconds': Decimal(random.uniform(0, 3600)),
                'pod_limit_cpu_core_seconds': Decimal(random.uniform(0, 3600)),
                'pod_usage_memory_byte_seconds': Decimal(random.uniform(0, 3600) * 1e9),
                'pod_request_memory_byte_seconds': Decimal(random.uniform(0, 3600) * 1e9),
                'pod_limit_memory_byte_seconds': Decimal(random.uniform(0, 3600) * 1e9),
                'node_capacity_cpu_cores': Decimal(node_cpu_cores),
                'node_capacity_cpu_core_seconds': Decimal(node_cpu_cores * 3600),
                'node_capacity_memory_bytes': Decimal(node_memory_gb * 1e9),
                'node_capacity_memory_byte_seconds': Decimal(node_memory_gb * 1e9 * 3600),
                'pod_labels': self._gen_pod_labels(report)
            }
            line_item = OCPUsageLineItem(**data)
            line_item.save()

    def _populate_daily_table(self):
        """Populate the daily table."""
        included_fields = [
            'namespace',
            'pod',
            'node',
            'pod_labels',
        ]
        annotations = {
            'usage_start': F('report__interval_start'),
            'usage_end': F('report__interval_start'),
            'pod_usage_cpu_core_seconds': Sum('pod_usage_cpu_core_seconds'),
            'pod_request_cpu_core_seconds': Sum('pod_request_cpu_core_seconds'),
            'pod_limit_cpu_core_seconds': Sum('pod_limit_cpu_core_seconds'),
            'pod_usage_memory_byte_seconds': Sum('pod_usage_memory_byte_seconds'),
            'pod_request_memory_byte_seconds': Sum('pod_request_memory_byte_seconds'),
            'pod_limit_memory_byte_seconds': Sum('pod_limit_memory_byte_seconds'),
            'cluster_id': F('report_period__cluster_id'),
            'node_capacity_cpu_cores': Max('node_capacity_cpu_cores'),
            'node_capacity_cpu_core_seconds': Max('node_capacity_cpu_core_seconds'),
            'node_capacity_memory_bytes': Max('node_capacity_memory_bytes'),
            'node_capacity_memory_byte_seconds': Max('node_capacity_memory_byte_seconds')
        }
        entries = OCPUsageLineItem.objects\
            .values(*included_fields)\
            .annotate(**annotations)

        cluster_capacity_cpu_core_seconds = Decimal(0)
        cluster_capacity_memory_byte_seconds = Decimal(0)

        cluster_cap = OCPUsageLineItem.objects\
            .values(*['node'])\
            .annotate(
                **{
                    'node_capacity_cpu_core_seconds': Max('node_capacity_cpu_core_seconds'),
                    'node_capacity_memory_byte_seconds': Sum('node_capacity_memory_byte_seconds')
                }
            )

        for node in cluster_cap:
            cluster_capacity_cpu_core_seconds += node.get('node_capacity_cpu_core_seconds')
            cluster_capacity_memory_byte_seconds += node.get('node_capacity_memory_byte_seconds')

        for entry in entries:
            entry['total_seconds'] = 3600
            entry['cluster_capacity_cpu_core_seconds'] = cluster_capacity_cpu_core_seconds
            entry['cluster_capacity_memory_byte_seconds'] = cluster_capacity_memory_byte_seconds
            daily = OCPUsageLineItemDaily(**entry)
            daily.save()

    def _populate_daily_summary_table(self):
        """Populate the daily summary table."""
        included_fields = [
            'usage_start',
            'usage_end',
            'namespace',
            'pod',
            'node',
            'cluster_id',
            'node_capacity_cpu_cores',
            'pod_labels',
        ]
        annotations = {
            'pod_usage_cpu_core_hours': F('pod_usage_cpu_core_seconds') / 3600,
            'pod_request_cpu_core_hours': Sum(
                ExpressionWrapper(
                    F('pod_request_cpu_core_seconds') / 3600,
                    output_field=DecimalField()
                )
            ),
            'pod_limit_cpu_core_hours': Sum(
                ExpressionWrapper(
                    F('pod_limit_cpu_core_seconds') / 3600,
                    output_field=DecimalField()
                )
            ),
            'pod_usage_memory_gigabyte_hours': Sum(
                ExpressionWrapper(
                    F('pod_usage_memory_byte_seconds') / 3600,
                    output_field=DecimalField()
                )
            ) * 1e-9,
            'pod_request_memory_gigabyte_hours': Sum(
                ExpressionWrapper(
                    F('pod_request_memory_byte_seconds') / 3600,
                    output_field=DecimalField()
                )
            ) * 1e-9,
            'pod_limit_memory_gigabyte_hours': ExpressionWrapper(
                F('pod_limit_memory_byte_seconds') / 3600,
                output_field=DecimalField()
            ) * 1e-9,
            'node_capacity_cpu_core_hours': F('node_capacity_cpu_core_seconds') / 3600,
            'node_capacity_memory_gigabytes': F('node_capacity_memory_bytes') * 1e-9,
            'node_capacity_memory_gigabyte_hours': ExpressionWrapper(
                F('node_capacity_memory_byte_seconds') / 3600,
                output_field=DecimalField()
            ) * 1e-9,
            'cluster_capacity_cpu_core_hours': F('cluster_capacity_cpu_core_seconds') / 3600,
            'cluster_capacity_memory_gigabyte_hours': ExpressionWrapper(
                F('cluster_capacity_memory_byte_seconds') / 3600,
                output_field=DecimalField()
            ) * 1e-9,
        }

        entries = OCPUsageLineItemDaily.objects.values(*included_fields).annotate(**annotations)

        for entry in entries:
            summary = OCPUsageLineItemDailySummary(**entry)
            summary.save()

    def _populate_charge_info(self):
        """Populate the charge information in summary table."""
        entries = OCPUsageLineItemDailySummary.objects.all()
        for entry in entries:
            mem_usage = entry.pod_usage_memory_gigabyte_hours
            mem_request = entry.pod_request_memory_gigabyte_hours
            mem_charge = max(float(mem_usage), float(mem_request)) * 0.25

            entry.pod_charge_memory_gigabyte_hours = mem_charge

            cpu_usage = entry.pod_usage_cpu_core_hours
            cpu_request = entry.pod_request_cpu_core_hours
            cpu_charge = max(float(cpu_usage), float(cpu_request)) * 0.50

            entry.pod_charge_cpu_core_hours = cpu_charge

            entry.save()
