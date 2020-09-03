# -*- mode: python; python-indent: 2; python-indent-offset: 2 -*-

import grafanalib.core as G
import grafanalib.weave as W

import common

dashboard = common.Dashboard(
    uid='chunks',
    title="Cortex > Chunks",
    rows=[
        G.Row(
            panels=[
                common.PromGraph(
                    title="Number of chunks (in memory, in ingesters)",
                    expressions=[
                        ('', 'sum(cortex_ingester_memory_chunks{job="cortex/ingester"})'),
                    ],
                ),
                common.PromGraph(
                    title="Chunks per series",
                    expressions=[
                        (
                            '',
                            'sum(cortex_ingester_memory_chunks{job="cortex/ingester"}) / sum(cortex_ingester_memory_series{job="cortex/ingester"})'
                        ),
                    ],
                ),
            ]
        ),
        G.Row(
            panels=[
                common.PromGraph(
                    title="Chunk Size Bytes (on flush)",
                    expressions=[
                        (
                            "99th Percentile",
                            'histogram_quantile(0.99, sum(rate(cortex_ingester_chunk_size_bytes_bucket{job="cortex/ingester"}[2m]))  by (le))'
                        ),
                        (
                            "50th Percentile",
                            'histogram_quantile(0.5, sum(rate(cortex_ingester_chunk_size_bytes_bucket{job="cortex/ingester"}[2m]))  by (le))'
                        ),
                        (
                            "10th Percentile",
                            'histogram_quantile(0.1, sum(rate(cortex_ingester_chunk_size_bytes_bucket{job="cortex/ingester"}[2m]))  by (le))'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_ingester_chunk_size_bytes_sum{job="cortex/ingester"}[2m])) / sum(rate(cortex_ingester_chunk_size_bytes_count{job="cortex/ingester"}[2m]))'
                        ),
                    ],
                    yAxes=[
                        G.YAxis(format=G.BYTES_FORMAT),
                        G.YAxis(format=G.SHORT_FORMAT),
                    ],
                ),
                common.PromGraph(
                    title="Chunk Age (on flush)",
                    expressions=[
                        (
                            "99th Percentile",
                            'histogram_quantile(0.99, sum(rate(cortex_ingester_chunk_age_seconds_bucket{job="cortex/ingester"}[2m])) by (le))'
                        ),
                        (
                            "50th Percentile",
                            'histogram_quantile(0.5, sum(rate(cortex_ingester_chunk_age_seconds_bucket{job="cortex/ingester"}[2m])) by (le))'
                        ),
                        (
                            "10th Percentile",
                            'histogram_quantile(0.1, sum(rate(cortex_ingester_chunk_age_seconds_bucket{job="cortex/ingester"}[2m])) by (le))'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_ingester_chunk_age_seconds_sum{job="cortex/ingester"}[2m])) / sum(rate(cortex_ingester_chunk_age_seconds_count{job="cortex/ingester"}[2m]))'
                        ),
                    ],
                    yAxes=[
                        G.YAxis(format=G.DURATION_FORMAT),
                        G.YAxis(format=G.SHORT_FORMAT),
                    ],
                ),
                common.PromGraph(
                    title="Chunk Length (on flush)",
                    expressions=[
                        (
                            "99th Percentile",
                            'histogram_quantile(0.99, sum(rate(cortex_ingester_chunk_length_bucket{job="cortex/ingester"}[2m])) by (le))'
                        ),
                        (
                            "50th Percentile",
                            'histogram_quantile(0.5, sum(rate(cortex_ingester_chunk_length_bucket{job="cortex/ingester"}[2m])) by (le))'
                        ),
                        (
                            "10th Percentile",
                            'histogram_quantile(0.1, sum(rate(cortex_ingester_chunk_length_bucket{job="cortex/ingester"}[2m])) by (le))'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_ingester_chunk_length_sum{job=\"cortex/ingester\"}[2m])) / sum(rate(cortex_ingester_chunk_length_count{job=\"cortex/ingester\"}[2m]))'
                        ),
                    ],
                ),
            ]
        ),
        G.Row(
            panels=[
                W.stacked(
                    common.PromGraph(
                        title="Series Flush Queue Length",
                        expressions=[
                            ("{{instance}}", 'cortex_ingester_flush_queue_length{job="cortex/ingester"}'),
                        ],
                    )
                ),
                W.stacked(
                    common.PromGraph(
                        title="Chunk Flush Rate (rate[1m])",
                        expressions=[
                            # This is the rate at which chunks are added to the flush queue
                            (
                                "{{reason}}",
                                'sum by (reason)(rate(cortex_ingester_flush_reasons[1m]) or rate(cortex_ingester_series_flushed_total[1m]) or rate(cortex_ingester_flushing_enqueued_series_total[1m]))'
                            ),
                            # This is the rate at which chunks are removed from the flush queue
                            ("Flushed", 'sum(rate(cortex_ingester_chunks_stored_total[1m]))'),
                            # Chunks dropped for being too small
                            ("Dropped", 'sum(rate(cortex_ingester_dropped_chunks_total[1m]))'),
                        ],
                        # Show flush and dropped rates as a line overlayed on enqueue rates, not stacked and not filled
                        seriesOverrides=[
                            {
                                "alias": "Flushed",
                                "fill": 1,
                                "linewidth": 1,
                                "stack": False
                            }, {
                                "alias": "Dropped",
                                "fill": 1,
                                "linewidth": 1,
                                "stack": False
                            }
                        ],
                    )
                ),
            ]
        ),
        G.Row(
            title="DynamoDB",
            collapse=True,
            panels=[
                common.PromGraph(
                    title="DynamoDB write capacity consumed [rate1m]",
                    expressions=[
                        (
                            '{{table}} consumed',
                            'sum(rate(cortex_dynamo_consumed_capacity_total{operation="DynamoDB.BatchWriteItem"}[1m])) by (table) > 0'
                        ),
                        (
                            '{{table}} provisioned',
                            'max(cortex_table_capacity_units{job="cortex/table-manager", op="write"}) by (table) > 0'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
                common.PromGraph(
                    title="DynamoDB write errors",
                    expressions=[
                        (
                            '{{table}} - {{error}}',
                            'sum(rate(cortex_dynamo_failures_total{job=~"cortex/.*", operation=~".*Write.*"}[1m])) by (job, error, table) > 0'
                        ),
                        (
                            '{{table}} - Throttled',
                            'sum(rate(cortex_dynamo_throttled_total{job=~"cortex/.*", operation=~".*Write.*"}[1m])) by (job, error, table) > 0'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
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
        G.Row(
            title="Index and Cache",
            panels=[
                common.PromGraph(
                    title="Index entries per chunk",
                    expressions=[
                        (
                            '',
                            'sum(rate(cortex_chunk_store_index_entries_per_chunk_sum{job="cortex/ingester"}[2m])) / sum(rate(cortex_chunk_store_index_entries_per_chunk_count{job="cortex/ingester"}[2m]))'
                        ),
                    ],
                ),
                common.PromGraph(
                    title="Ingester hit rate",
                    expressions=[
                        (
                            '{{name}}',
                            'sum(rate(cortex_cache_hits{job="cortex/ingester"}[2m])) by (name) / sum(rate(cortex_cache_fetched_keys{job="cortex/ingester"}[2m])) by (name)'
                        ),
                    ],
                    yAxes=common.PercentageAxes(),
                ),
            ]
        ),
    ]
)
