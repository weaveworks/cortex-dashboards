# -*- mode: python; python-indent-offset: 2 -*-

import grafanalib.core as G

import sys, os
sys.path.append(os.path.dirname(__file__))
import common

dashboard = common.Dashboard(
    uid='ruler',
    title="Cortex > Recording Rules",
    rows=[
        G.Row(
            title="Configs",
            collapse=True,
            panels=[
                common.PromGraph(
                    title="Known Configurations",
                    expressions=[
                        ("Configurations", 'max(cortex_configs{job="cortex/ruler"})'),
                        ("{{status}}", 'max by(status)(cortex_alertmanager_configs{job="cortex/alertmanager"})'),
                    ],
                ),
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
                        ), (
                            "Groups per second",
                            'sum(rate(cortex_prometheus_rule_group_duration_seconds_count{job="cortex/ruler"}[1m]))'
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
                        ("Mean", 'avg(cortex_prometheus_rule_group_last_duration_seconds)*1e3'),
                        (
                            "{{rule_group}}",
                            'max by (rule_group)(cortex_prometheus_rule_group_last_duration_seconds)*1e3 > 500'
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
                        ("Mean", 'avg(time()-(cortex_prometheus_rule_group_last_evaluation_timestamp_seconds>0))*1000'),
                        ("Max", 'max(time()-(cortex_prometheus_rule_group_last_evaluation_timestamp_seconds>0))*1e3'),
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
                        ("Rules/sec", 'sum(rate(cortex_prometheus_rule_evaluations_total{job="cortex/ruler"}[1m]))'),
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
            title="Memcache",
            panels=[
                common.StatusQPSGraph(
                    common.PROMETHEUS, "Memcache read QPS",
                    'sum by (job,status_code)(rate(cortex_memcache_request_duration_seconds_count{method="Memcache.GetMulti", job="cortex/ruler"}[1m]))'
                ),
                common.PromGraph(
                    title="Memcache read latency",
                    expressions=[
                        (
                            '99th centile',
                            'histogram_quantile(0.99, sum(rate(cortex_memcache_request_duration_seconds_bucket{job="cortex/ruler",method="Memcache.GetMulti"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            '50th centile',
                            'histogram_quantile(0.5, sum(rate(cortex_memcache_request_duration_seconds_bucket{job="cortex/ruler",method="Memcache.GetMulti"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            'Mean',
                            'sum(rate(cortex_memcache_request_duration_seconds_sum{job="cortex/ruler",method="Memcache.GetMulti"}[2m])) * 1e3 / sum(rate(cortex_memcache_request_duration_seconds_count{job="cortex/ruler",method="Memcache.GetMulti"}[2m]))'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ],
        ),
    ],
)
