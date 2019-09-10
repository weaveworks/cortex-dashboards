# -*- mode: python; python-indent-offset: 2 -*-

import grafanalib.core as G

import common

dashboard = common.Dashboard(
    uid='ruler',
    title="Cortex > Recording Rules",
    rows=[
        G.Row(
            title="Configs",
            collapse=True,
            panels=[
                common.QPSGraph('cortex_configs', 'Configs', 'cortex/ruler'),
                common.PromGraph(
                    title="Configs Latency",
                    expressions=[
                        (
                            "99th centile",
                            'histogram_quantile(0.99, sum(rate(cortex_configs_request_duration_seconds_bucket{job="cortex/ruler"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "50th centile",
                            'histogram_quantile(0.50, sum(rate(cortex_configs_request_duration_seconds_bucket{job="cortex/ruler"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_configs_request_duration_seconds_sum{job="cortex/ruler"}[2m])) / sum(rate(cortex_configs_request_duration_seconds_count{job="cortex/ruler"}[2m])) * 1e3'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ]
        ),
        common.REDRow('cortex', 'Ruler service', 'cortex/ruler', collapse=True),
        G.Row(
            [
                common.PromGraph(
                    title="Group Evaluations per Second",
                    expressions=[
                        (
                            "Groups per second",
                            'sum(rate(cortex_group_evaluation_duration_seconds_count{job="cortex/ruler"}[1m]))'
                        )
                    ],
                    yAxes=common.OPS_AXIS,
                ),
                common.PromGraph(
                    title="Group Evaluation Durations",
                    expressions=[
                        (
                            "99th centile",
                            'histogram_quantile(0.99, sum(rate(cortex_group_evaluation_duration_seconds_bucket{job="cortex/ruler"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "50th centile",
                            'histogram_quantile(0.50, sum(rate(cortex_group_evaluation_duration_seconds_bucket{job="cortex/ruler"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_group_evaluation_duration_seconds_sum{job="cortex/ruler"}[2m])) / sum(rate(cortex_group_evaluation_duration_seconds_count{job="cortex/ruler"}[2m])) * 1e3'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
                common.PromGraph(
                    title="Group Evaluation Latency",
                    expressions=[
                        (
                            "99th centile",
                            'histogram_quantile(0.99, sum(rate(cortex_group_evaluation_latency_seconds_bucket[2m])) by (le)) * 1e3'
                        ),
                        (
                            "50th centile",
                            'histogram_quantile(0.50, sum(rate(cortex_group_evaluation_latency_seconds_bucket[2m])) by (le)) * 1e3'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_group_evaluation_latency_seconds_sum[2m])) / sum(rate(cortex_group_evaluation_latency_seconds_count[2m])) * 1e3'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ]
        ),
        G.Row(
            title="Ingester Queries",
            panels=[
                common.QPSGraph('cortex_distributor', 'Ingester Query', 'cortex/ruler', metric_root="query"),
                common.PromGraph(
                    title="Ingester Query Latency",
                    expressions=[
                        (
                            "99th centile",
                            'histogram_quantile(0.99, sum(rate(cortex_distributor_query_duration_seconds_bucket{job="cortex/ruler"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "50th centile",
                            'histogram_quantile(0.50, sum(rate(cortex_distributor_query_duration_seconds_bucket{job="cortex/ruler"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_distributor_query_duration_seconds_sum{job="cortex/ruler"}[2m])) / sum(rate(cortex_distributor_query_duration_seconds_count{job="cortex/ruler"}[2m])) * 1e3'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ]
        ),
        G.Row(
            title="Ingester Push",
            panels=[
                common.StatusQPSGraph(
                    common.PROMETHEUS, "Ingester Push",
                    'rate(cortex_ingester_client_request_duration_seconds_count{job="cortex/ruler",operation="/cortex.Ingester/Push"}[1m])'
                ),
                common.PromGraph(
                    title="Ingester Push Latency",
                    expressions=[
                        (
                            "99.7th centile",
                            'histogram_quantile(0.997, sum(rate(cortex_ingester_client_request_duration_seconds_bucket{job="cortex/ruler",operation="/cortex.Ingester/Push"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "50th centile",
                            'histogram_quantile(0.50, sum(rate(cortex_ingester_client_request_duration_seconds_bucket{job="cortex/ruler",operation="/cortex.Ingester/Push"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_ingester_client_request_duration_seconds_sum{job="cortex/ruler",operation="/cortex.Ingester/Push"}[2m])) / sum(rate(cortex_ingester_client_request_duration_seconds_count{job="cortex/ruler",operation="/cortex.Ingester/Push"}[2m])) * 1e3'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ]
        ),
        G.Row(
            [
                common.PromGraph(
                    title="Rules per Second",
                    expressions=[
                        ("Rules", 'sum(rate(cortex_rules_processed_total{job="cortex/ruler"}[1m]))'),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
                common.PromGraph(
                    title="Ruler DynamoDB errors",
                    expressions=[
                        (
                            '{{table}} - {{error}}',
                            'sum(rate(cortex_dynamo_failures_total{job="cortex/ruler"}[1m])) by (error, table) > 0'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
            ]
        ),
        G.Row(
            [
                common.PromGraph(
                    title="Known Configurations",
                    expressions=[
                        ("Configurations", 'max(cortex_configs{job="cortex/ruler"})'),
                    ],
                ),
                common.PromGraph(
                    title="Rules Queue Length",
                    expressions=[
                        ("Groups", 'sum(cortex_rules_queue_length{job="cortex/ruler"})'),
                    ],
                ),
                common.PromGraph(
                    title="Idle workers",
                    expressions=[
                        ("Workers", 'sum(rate(cortex_worker_idle_seconds_total[1m]))'),
                    ],
                ),
            ]
        ),
    ],
)
