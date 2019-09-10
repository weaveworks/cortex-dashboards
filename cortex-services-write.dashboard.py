# -*- mode: python; python-indent-offset: 2 -*-

import grafanalib.core as G

import common

dashboard = common.Dashboard(
    uid='writes',
    title="Cortex > Services (Writes)",
    rows=[
        G.Row(
            title="Retrieval Stats",
            collapse=True,
            panels=[
                common.PromGraph(
                    title="Retrieval sent batches",
                    expressions=[
                        (
                            '{{queue}}',
                            'sum(rate(prometheus_remote_storage_sent_batch_duration_seconds_count[1m])) by (queue)'
                        ),
                    ],
                ),
                common.PromGraph(
                    title="Retrieval batch latency",
                    expressions=[
                        (
                            '{{queue}} 99th',
                            'histogram_quantile(0.99, sum(rate(prometheus_remote_storage_sent_batch_duration_seconds_bucket[2m])) by (queue, le)) * 1e3'
                        ),
                        (
                            '{{queue}} 50th',
                            'histogram_quantile(0.50, sum(rate(prometheus_remote_storage_sent_batch_duration_seconds_bucket[2m])) by (queue, le)) * 1e3'
                        ),
                        (
                            '{{queue}} mean',
                            '(sum(rate(prometheus_remote_storage_sent_batch_duration_seconds_sum[2m])) by (queue) /  sum(rate(prometheus_remote_storage_sent_batch_duration_seconds_count[2m])) by (queue)) * 1e3'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
                common.PromGraph(
                    title="Retrieval sent samples",
                    expressions=[
                        (
                            '{{queue}} success',
                            'sum(rate(prometheus_remote_storage_succeeded_samples_total[1m])) by (queue)'
                        ),
                        (
                            '{{queue}} dropped',
                            'sum(rate(prometheus_remote_storage_dropped_samples_total[1m])) by (queue)'
                        ),
                        (
                            '{{queue}} retried',
                            'sum(rate(prometheus_remote_storage_retried_samples_total[1m])) by (queue)'
                        ),
                        (
                            '{{queue}} failure',
                            'sum(rate(prometheus_remote_storage_failed_samples_total[1m])) by (queue)'
                        ),
                    ],
                ),
                common.PromGraph(
                    title="Queue",
                    expressions=[
                        ('{{queue}}: queue length', 'sum(prometheus_remote_storage_pending_samples) by (queue)'),
                        (
                            '{{queue}}: lag',
                            'max(time()-prometheus_remote_storage_queue_highest_sent_timestamp_seconds) by (queue)'
                        ),
                        ('{{queue}}: shards', 'max(prometheus_remote_storage_shards) by (queue)'),
                    ],
                ),
            ],
        ),
        G.Row(
            title="Distributor",
            panels=[
                common.StatusQPSGraph(
                    common.PROMETHEUS, "Distributor write QPS",
                    'rate(cortex_request_duration_seconds_count{job="cortex/distributor"}[1m])'
                ),
                common.LatencyGraph("cortex", "Distributor Write", "cortex/distributor"),
            ],
        ),
        G.Row(
            title="Distributor breakdown",
            collapse=True,
            panels=[
                common.PromGraph(
                    title="Distributor Error Rate",
                    expressions=[
                        (
                            '{{instance}}',
                            'sum by (instance)(rate(cortex_request_duration_seconds_count{job="cortex/distributor", status_code =~ "5.."}[1m]))'
                        ),
                    ],
                ),
                common.PromGraph(
                    title="Distributor write latency",
                    expressions=[
                        (
                            '99th centile {{instance}}',
                            'histogram_quantile(0.99, sum(rate(cortex_request_duration_seconds_bucket{job="cortex/distributor"}[2m])) by (instance,le)) * 1e3'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ],
        ),
        G.Row(
            title="Distributor sends",
            collapse=True,
            panels=[
                common.StatusQPSGraph(
                    common.PROMETHEUS, "Distributor send QPS",
                    'rate(cortex_ingester_client_request_duration_seconds_count{job="cortex/distributor",operation="/cortex.Ingester/Push"}[1m])'
                ),
                common.PromGraph(
                    title="Distributor send latency",
                    expressions=[
                        (
                            '99th centile',
                            'histogram_quantile(0.99, sum(rate(cortex_ingester_client_request_duration_seconds_bucket{job="cortex/distributor",operation="/cortex.Ingester/Push"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            '50th centile',
                            'histogram_quantile(0.50, sum(rate(cortex_ingester_client_request_duration_seconds_bucket{job="cortex/distributor",operation="/cortex.Ingester/Push"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            'Mean',
                            'sum(rate(cortex_ingester_client_request_duration_seconds_sum{job="cortex/distributor",operation="/cortex.Ingester/Push"}[2m])) * 1e3 / sum(rate(cortex_ingester_client_request_duration_seconds_count{job="cortex/distributor",operation="/cortex.Ingester/Push"}[2m]))'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ],
        ),
        G.Row(
            title="Samples",
            collapse=True,
            panels=[
                common.PromGraph(
                    title="Push sample ingest rate by instance (>1%)",
                    expressions=[
                        (
                            '{{user}}',
                            'sum by (user)(rate(cortex_distributor_received_samples_total{job="cortex/distributor"}[1m])) > ignoring(user) group_left() (sum(rate(cortex_distributor_received_samples_total{job="cortex/distributor"}[1m]))/100)'
                        ),
                    ],
                    legend=G.Legend(show=False),
                    yAxes=common.OPS_AXIS,
                ),
                common.PromGraph(
                    title="Rule sample ingest rate by instance",
                    expressions=[
                        (
                            '{{user}}',
                            # '> 1' is to exclude instances which are not connected and simply alerting on absent metrics
                            'sum by (user)(rate(cortex_distributor_received_samples_total{job="cortex/ruler"}[1m])) > 1'
                        ),
                    ],
                    legend=G.Legend(show=False),
                    yAxes=common.OPS_AXIS,
                ),
                common.PromGraph(
                    title="Sample discard rate by instance ID & reason",
                    expressions=[
                        (
                            '{{user}} - {{reason}} ',
                            'sum by (user, reason) (rate(cortex_discarded_samples_total{reason!="duplicate-sample"}[1m])) > 0'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
            ],
        ),
        G.Row(
            title="Ingester",
            panels=[
                common.StatusQPSGraph(
                    common.PROMETHEUS, "Ingester write QPS",
                    'rate(cortex_request_duration_seconds_count{job="cortex/ingester"}[1m])'
                ),
                common.PromGraph(
                    title="Ingester write latency",
                    expressions=[
                        (
                            '99th centile',
                            'job_route:cortex_request_duration_seconds:99quantile{job="cortex/ingester", route="/cortex.Ingester/Push"} * 1e3'
                        ),
                        (
                            '50th centile',
                            'job_route:cortex_request_duration_seconds:50quantile{job="cortex/ingester", route="/cortex.Ingester/Push"} * 1e3'
                        ),
                        (
                            'Mean',
                            'sum(rate(cortex_request_duration_seconds_sum{job="cortex/ingester", route="/cortex.Ingester/Push"}[2m])) * 1e3 / sum(rate(cortex_request_duration_seconds_count{job="cortex/ingester", route="/cortex.Ingester/Push"}[2m]))'
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
                    title="DynamoDB write QPS",
                    expressions=[
                        (
                            'BatchWriteItem {{job}}: {{status_code}}',
                            'sum(rate(cortex_dynamo_request_duration_seconds_count{job=~"cortex/.*", operation="DynamoDB.BatchWriteItem"}[1m])) by (job, status_code)'
                        ),
                    ],
                ),
                common.PromGraph(
                    title="DynamoDB write latency",
                    expressions=[
                        (
                            'BatchWriteItem: 99th',
                            'histogram_quantile(0.99, sum(rate(cortex_dynamo_request_duration_seconds_bucket{job=~"cortex/.*", operation="DynamoDB.BatchWriteItem"}[2m])) by (le)) * 1e3'
                        ), (
                            'BatchWriteItem: 50th',
                            'histogram_quantile(0.5, sum(rate(cortex_dynamo_request_duration_seconds_bucket{job=~"cortex/.*", operation="DynamoDB.BatchWriteItem"}[2m])) by (le)) * 1e3'
                        ), (
                            'BatchWriteItem: Mean',
                            'sum(rate(cortex_dynamo_request_duration_seconds_sum{job=~"cortex/.*", operation="DynamoDB.BatchWriteItem"}[2m])) * 1e3 / sum(rate(cortex_dynamo_request_duration_seconds_count{job=~"cortex/.*", operation="DynamoDB.BatchWriteItem"}[2m]))'
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
                    title="DynamoDB write capacity consumed [rate1m]",
                    expressions=[
                        (
                            '{{table}} consumed',
                            'sum(rate(cortex_dynamo_consumed_capacity_total{job=~"cortex/.*", operation="DynamoDB.BatchWriteItem"}[1m])) by (table) > 0'
                        ),
                        (
                            '{{table}} provisioned',
                            'max(cortex_dynamo_table_capacity_units{job="cortex/table-manager", op="write"}) by (table)  and (sum(rate(cortex_dynamo_consumed_capacity_total{job=~"cortex/.*", operation="DynamoDB.BatchWriteItem"}[1m])) by (table) > 0)'
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
                    ],
                    yAxes=common.OPS_AXIS,
                ),
            ],
        ),
        G.Row(
            title="Memcache",
            panels=[
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
                common.PromGraph(
                    title="Memcache QPS",
                    expressions=[
                        (
                            '{{method}} {{status_code}}',
                            'sum(rate(cortex_memcache_request_duration_seconds_count{job="cortex/ingester"}[1m])) by (method,status_code)'
                        ),
                        (
                            '{{table}} - Throttled',
                            'sum(rate(cortex_dynamo_throttled_total{job=~"cortex/.*", operation=~".*Write.*"}[1m])) by (job, error, table) > 0'
                        ),
                    ],
                ),
                common.PromGraph(
                    title="Memcache latency",
                    expressions=[
                        (
                            '{{method}} 99th centile',
                            'histogram_quantile(0.99, sum(rate(cortex_memcache_request_duration_seconds_bucket{job="cortex/ingester"}[2m])) by (le,method)) * 1e3'
                        ),
                        (
                            '{{method}} 50th centile',
                            'histogram_quantile(0.5, sum(rate(cortex_memcache_request_duration_seconds_bucket{job="cortex/ingester"}[2m])) by (le,method)) * 1e3'
                        ),
                        (
                            '{{method}} Mean',
                            'sum by (method)(rate(cortex_memcache_request_duration_seconds_sum{job="cortex/ingester"}[2m])) * 1e3 / sum by (method)(rate(cortex_memcache_request_duration_seconds_count{job="cortex/ingester"}[2m]))'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ],
        ),
    ],
)
