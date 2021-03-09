# -*- mode: python; python-indent-offset: 2 -*-

import grafanalib.core as G
import grafanalib.weave as W

import common

dashboard = common.Dashboard(
    uid='cortex-blocks',
    title="Cortex > Blocks",
    rows=[
        G.Row(
            title="Data",
            panels=[
                common.PromGraph(
                    title="Number of series in memory, in ingesters",
                    expressions=[
                        ('', 'sum(cortex_ingester_memory_series{job="cortex/ingester"})'),
                    ],
                ),
                common.PromGraph(
                    title="Head chunks",
                    expressions=[
                        ('{{instance}}', 'cortex_ingester_tsdb_head_chunks'),
                    ],
                ),
            ]
        ),
        G.Row(
            title="Resources",
            panels=[
                common.PromGraph(
                    title="Memory Usage",
                    expressions=[
                        (
                            '{{pod}}',
                            'sum by(pod)(container_memory_usage_bytes{namespace="cortex",container!="POD",container!=""})'
                        ),
                    ],
                    yAxes=[
                        G.YAxis(format=G.BYTES_FORMAT),
                        G.YAxis(format=G.SHORT_FORMAT),
                    ],
                ),
                common.PromGraph(
                    title="Disk space usage",
                    expressions=[
                        (
                            '{{persistentvolumeclaim}}',
                            'kubelet_volume_stats_used_bytes{namespace="cortex"} / kubelet_volume_stats_capacity_bytes{namespace="cortex"}'
                        ),
                    ],
                    yAxes=common.PercentageAxes(),
                ),
            ],
        ),
        G.Row(
            title="Last runs",
            panels=[
                G.SingleStat(
                    dataSource=common.PROMETHEUS,
                    title="Last Successful Compactor Run",
                    targets=[
                        G.Target(
                            '(time()-cortex_compactor_last_successful_run_timestamp_seconds) / 60',
                            refId='A',
                        ),
                    ],
                    format='m',  # TODO: Add 'MINUTES_FORMAT' to grafanalib
                ),
                G.SingleStat(
                    dataSource=common.PROMETHEUS,
                    title="Last Successful Bucket Index Update",
                    targets=[
                        G.Target(
                            '(time()-max(cortex_bucket_index_last_successful_update_timestamp_seconds)) / 60',
                            refId='A',
                        ),
                    ],
                    format='m',  # TODO: Add 'MINUTES_FORMAT' to grafanalib
                ),
            ],
        ),
        G.Row(
            title="Block Operations",
            panels=[
                common.PromGraph(
                    title="Rates",
                    expressions=[
                        ('{{component}} loads', 'sum by(component)(rate(cortex_bucket_store_block_loads_total{}[1m]))'),
                        (
                            '{{component}} errors',
                            'sum by(component)(rate(cortex_bucket_store_block_load_failures_total{}[1m])) > 0'
                        ),
                        ('Uploads', 'sum(rate(cortex_ingester_shipper_uploads_total[5m]))'),
                        ('Upload errors', 'sum(rate(cortex_ingester_shipper_upload_failures_total[5m]))'),
                        ('Dir syncs', 'sum(rate(cortex_ingester_shipper_dir_syncs_total[5m]))'),
                        ('Dir sync errors', 'sum(rate(cortex_ingester_shipper_dir_sync_failures_total[5m]))'),
                    ],
                    yAxes=[
                        G.YAxis(format=G.OPS_FORMAT),
                        G.YAxis(format=G.SHORT_FORMAT),
                    ],
                ),
                common.PromGraph(
                    title="Latency",
                    expressions=[
                        (
                            '99th centile',
                            'histogram_quantile(0.99, sum(rate(thanos_objstore_bucket_operation_duration_seconds_bucket{operation="upload"}[5m])) by (le))'
                        ),
                        (
                            '50th centile',
                            'histogram_quantile(0.5, sum(rate(thanos_objstore_bucket_operation_duration_seconds_bucket{operation="upload"}[5m])) by (le))'
                        ),
                        (
                            'Mean',
                            'sum(rate(thanos_objstore_bucket_operation_duration_seconds_sum{operation="upload"}[5m])) / sum(rate(thanos_objstore_bucket_operation_duration_seconds_count{operation="upload"}[5m]))'
                        ),
                    ],
                    yAxes=G.single_y_axis(format=G.SECONDS_FORMAT),
                ),
            ],
        ),
        G.Row(
            title="Compactions",
            panels=[
                common.PromGraph(
                    title="Operations",
                    expressions=[
                        ('Compactions', 'sum(rate(cortex_ingester_tsdb_compactions_total[5m]))'),
                        ('errors', 'sum(rate(cortex_ingester_tsdb_compactions_failed_total[5m]))'),
                    ],
                ),
                common.PromGraph(
                    title="Latency",
                    expressions=[
                        (
                            '99th centile',
                            'histogram_quantile(0.99, sum(rate(cortex_ingester_tsdb_compaction_duration_seconds_bucket{}[5m])) by (le))'
                        ),
                        (
                            '50th centile',
                            'histogram_quantile(0.5, sum(rate(cortex_ingester_tsdb_compaction_duration_seconds_bucket{}[5m])) by (le))'
                        ),
                        (
                            'Mean',
                            'sum(rate(cortex_ingester_tsdb_compaction_duration_seconds_sum{}[5m])) / sum(rate(cortex_ingester_tsdb_compaction_duration_seconds_count{}[5m]))'
                        ),
                    ],
                    yAxes=G.single_y_axis(format=G.SECONDS_FORMAT),
                ),
            ],
        ),
        G.Row(
            title="WAL",
            panels=[
                common.PromGraph(
                    title="Operations",
                    expressions=[
                        ('Truncations', 'sum(rate(cortex_ingester_tsdb_wal_truncations_total[5m]))'),
                        ('Truncation errors', 'sum(rate(cortex_ingester_tsdb_wal_truncations_failed_total[5m]))'),
                        ('Checkpoint', 'sum(rate(cortex_ingester_tsdb_checkpoint_creations_total[5m]))'),
                        ('Checkpoint errors', 'sum(rate(cortex_ingester_tsdb_checkpoint_creations_failed_total[5m]))'),
                        ('WAL corruptions', 'sum(rate(cortex_ingester_wal_corruptions_total[5m]))'),
                        ('mmap corruptions', 'sum(rate(cortex_ingester_tsdb_mmap_chunk_corruptions_total[5m]))'),
                    ],
                ),
                common.PromGraph(
                    title="Latency",
                    expressions=[
                        (
                            '99th centile',
                            'histogram_quantile(0.99, sum(rate(cortex_ingester_tsdb_wal_truncate_duration_seconds_bucket{}[5m])) by (le))'
                        ),
                        (
                            '50th centile',
                            'histogram_quantile(0.5, sum(rate(cortex_ingester_tsdb_wal_truncate_duration_seconds_bucket{}[5m])) by (le))'
                        ),
                        (
                            'Mean',
                            'sum(rate(cortex_ingester_tsdb_wal_truncate_duration_seconds_sum{}[5m])) / sum(rate(cortex_ingester_tsdb_wal_truncate_duration_seconds_count{}[5m]))'
                        ),
                    ],
                    yAxes=G.single_y_axis(format=G.SECONDS_FORMAT),
                ),
            ],
        ),
        G.Row(
            title="Bucket Operations",
            panels=[
                common.PromGraph(
                    title="Operations",
                    expressions=[
                        (
                            '{{component}}-{{operation}}',
                            'sum by(component,operation) (rate(thanos_objstore_bucket_operations_total[5m]))'
                        ),
                        (
                            'errors {{component}}-{{operation}}',
                            'sum by(component,operation) (rate(thanos_objstore_bucket_operation_failures_total[5m]))'
                        ),
                    ],
                ),
                common.PromGraph(
                    title="99% Latency",
                    expressions=[
                        (
                            '{{component}}-{{operation}}',
                            'histogram_quantile(0.99, sum(rate(thanos_objstore_bucket_operation_duration_seconds_bucket[5m])) by (le, component, operation)) > 0'
                        ),
                    ],
                    yAxes=G.single_y_axis(format=G.SECONDS_FORMAT),
                ),
            ],
        ),
        G.Row(
            title="Ring",
            collapse=True,
            panels=[
                W.stacked(
                    common.PromGraph(
                        title="Ingester Ring Ownership",
                        expressions=[
                            (
                                '{{ingester}}',
                                'max(cortex_ring_ingester_ownership_percent{job="cortex/distributor"}) by (ingester) or label_replace(max(cortex_ring_member_ownership_percent{job="cortex/distributor"}) by (member), "ingester", "$1", "member", "(.*)")'
                            ),
                        ],
                        # Show y-axis slightly above 100% in case series overlap
                        yAxes=common.PercentageAxes(max=1.2),
                    )
                ),
                W.stacked(
                    common.PromGraph(
                        title="Ingesters In Ring",
                        expressions=[
                            (
                                '{{state}}',
                                'max(cortex_ring_ingesters{job="cortex/distributor"}) by (state) or max(cortex_ring_members{job="cortex/distributor"}) by (state)'
                            ),
                        ],
                        yAxes=[
                            G.YAxis(format=G.NO_FORMAT),
                            G.YAxis(format=G.SHORT_FORMAT),
                        ],
                    )
                ),
            ]
        ),
    ],
)
