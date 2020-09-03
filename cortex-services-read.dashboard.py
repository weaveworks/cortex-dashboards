# -*- mode: python; python-indent-offset: 2 -*-

import grafanalib.core as G

import common

dashboard = common.Dashboard(
    uid='reads',
    title="Cortex > Services (Reads)",
    rows=[
        common.REDRow(
            'cortex',
            'Query Frontend read',
            'cortex/query-frontend',
            rule_root="job_route:",
            extra_conditions=",route=\"api_prom\""
        ),
        common.REDRow('cortex', 'Querier read', 'cortex/querier'),
        G.Row(
            title="Ingester",
            panels=[
                common.PromGraph(
                    title="Ingester read QPS",
                    expressions=[
                        (
                            '{{route}}: {{status_code}}',
                            'sum(rate(cortex_request_duration_seconds_count{job="cortex/ingester", route!="/cortex.Ingester/Push"}[1m])) by (route, status_code)'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
                common.PromGraph(
                    title="Ingester read latency",
                    expressions=[
                        (
                            '{{route}}: 99th centile',
                            'job_route:cortex_request_duration_seconds:99quantile{job="cortex/ingester", route!="/cortex.Ingester/Push"} * 1e3'
                        ),
                        (
                            '{{route}}: 50th centile',
                            'job_route:cortex_request_duration_seconds:50quantile{job="cortex/ingester", route!="/cortex.Ingester/Push"} * 1e3'
                        ),
                        (
                            '{{route}}: Mean',
                            'sum(rate(cortex_request_duration_seconds_sum{job="cortex/ingester", route!="/cortex.Ingester/Push"}[2m])) by (route) * 1e3 / sum(rate(cortex_request_duration_seconds_count{job="cortex/ingester", route!="/cortex.Ingester/Push"}[2m])) by (route)'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ],
        ),
        G.Row(
            title="DynamoDB",
            panels=[
                common.PromGraph(
                    title="DynamoDB read QPS",
                    expressions=[
                        (
                            'QueryPages {{job}}: {{status_code}}',
                            'sum(rate(cortex_dynamo_request_duration_seconds_count{job=~"cortex/.*", operation="DynamoDB.QueryPages"}[1m])) by (job, status_code)'
                        ),
                    ],
                ),
                common.PromGraph(
                    title="DynamoDB read latency",
                    expressions=[
                        (
                            'QueryPages: 99th',
                            'histogram_quantile(0.99, sum(rate(cortex_dynamo_request_duration_seconds_bucket{job=~"cortex/.*", operation="DynamoDB.QueryPages"}[2m])) by (le)) * 1e3'
                        ), (
                            'QueryPages: 50th',
                            'histogram_quantile(0.5, sum(rate(cortex_dynamo_request_duration_seconds_bucket{job=~"cortex/.*", operation="DynamoDB.QueryPages"}[2m])) by (le)) * 1e3'
                        ), (
                            'QueryPages: Mean',
                            'sum(rate(cortex_dynamo_request_duration_seconds_sum{job=~"cortex/.*", operation="DynamoDB.QueryPages"}[2m])) * 1e3 / sum(rate(cortex_dynamo_request_duration_seconds_count{job=~"cortex/.*", operation="DynamoDB.QueryPages"}[2m]))'
                        )
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ],
        ),
        G.Row(
            title="DynamoDB",
            panels=[
                common.PromGraph(
                    title="DynamoDB read capacity consumed [rate1m]",
                    expressions=[
                        (
                            '{{table}} consumed',
                            'sum(rate(cortex_dynamo_consumed_capacity_total{job=~"cortex/.*",operation!~".*Write.*"}[1m])) by (table) > 0'
                        ),
                        (
                            '{{table}} provisioned',
                            'max(cortex_dynamo_table_capacity_units{job="cortex/table-manager", op="read"}) by (table) > 0'
                        ),
                        (
                            '{{table}} provisioned',
                            'max(cortex_table_capacity_units{job="cortex/table-manager", op="read"}) by (table) > 0'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
                common.PromGraph(
                    title="DynamoDB read errors",
                    expressions=[
                        (
                            '{{job}} - {{table}} - {{error}}',
                            'sum(rate(cortex_dynamo_failures_total{job=~"cortex/.*", operation!~".*Write.*"}[1m])) by (job, error, table) > 0'
                        ),
                        (
                            '{{job}} - {{table}} - Throttled',
                            'sum(rate(cortex_dynamo_throttled_total{job=~"cortex/.*", operation!~".*Write.*"}[1m])) by (job, error, table) > 0'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
            ],
        ),
        G.Row(
            title="Memcache",
            panels=[
                common.StatusQPSGraph(
                    common.PROMETHEUS, "Memcache read QPS",
                    'rate(cortex_memcache_request_duration_seconds_count{method="Memcache.Get", job=~"cortex/.*"}[1m])'
                ),
                common.PromGraph(
                    title="Memcache read latency",
                    expressions=[
                        (
                            '99th centile',
                            'histogram_quantile(0.99, sum(rate(cortex_memcache_request_duration_seconds_bucket{job=~"cortex/.*",method="Memcache.Get"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            '50th centile',
                            'histogram_quantile(0.5, sum(rate(cortex_memcache_request_duration_seconds_bucket{job=~"cortex/.*",method="Memcache.Get"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            'Mean',
                            'sum(rate(cortex_memcache_request_duration_seconds_sum{job=~"cortex/.*",method="Memcache.Get"}[2m])) * 1e3 / sum(rate(cortex_memcache_request_duration_seconds_count{job=~"cortex/.*",method="Memcache.Get"}[2m]))'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ],
        ),
        G.Row(
            title="Cache",
            panels=[
                common.PromGraph(
                    title="Querier Cache hit rate",
                    expressions=[
                        (
                            '{{name}}',
                            'sum(rate(cortex_cache_hits{job="cortex/querier"}[2m])) by (name) / sum(rate(cortex_cache_fetched_keys{job="cortex/querier"}[2m])) by (name)'
                        ),
                    ],
                    yAxes=common.PercentageAxes(),
                ),
                common.PromGraph(
                    title="Query-frontend cache hit rate",
                    expressions=[
                        (
                            '{{name}}',
                            'sum(rate(cortex_cache_hits{job="cortex/query-frontend"}[2m])) by (name) / sum(rate(cortex_cache_fetched_keys{job="cortex/query-frontend"}[2m])) by (name)'
                        ),
                    ],
                    yAxes=common.PercentageAxes(),
                ),
            ],
        ),
        G.Row(
            title="S3",
            collapse=True,
            panels=[
                common.StatusQPSGraph(
                    common.PROMETHEUS, "S3 read QPS",
                    'rate(cortex_s3_request_duration_seconds_count{operation="S3.GetObject", job=~"cortex/.*"}[1m])'
                ),
                common.PromGraph(
                    title="S3 read latency",
                    expressions=[
                        (
                            '99th centile',
                            'histogram_quantile(0.99, sum(rate(cortex_s3_request_duration_seconds_bucket{job=~"cortex/.*", operation="S3.GetObject"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            '50th centile',
                            'histogram_quantile(0.5, sum(rate(cortex_s3_request_duration_seconds_bucket{job=~"cortex/.*", operation="S3.GetObject"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            'Mean',
                            'sum(rate(cortex_s3_request_duration_seconds_sum{job=~"cortex/.*", operation="S3.PutObject"}[2m])) * 1e3/ sum(rate(cortex_s3_request_duration_seconds_count{job=~"cortex/.*", operation="S3.GetObject"}[2m]))'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ],
        ),
    ],
)
