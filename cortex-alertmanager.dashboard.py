# -*- mode: python; python-indent-offset: 2 -*-

import grafanalib.core as G

import sys, os
sys.path.append(os.path.dirname(__file__))
import common

dashboard = common.Dashboard(
    uid='am',
    title="Cortex > Alertmanager",
    rows=[
        G.Row(
            title='Operations',
            panels=[
                common.PromGraph(
                    title="Alerts",
                    expressions=[
                        (
                            "{{instance}} {{status}}",
                            'sum by (instance, status)(rate(alertmanager_alerts_received_total{job="cortex/alertmanager"}[2m]))'
                        ),
                        (
                            "{{instance}} invalid",
                            'sum by (instance, status)(rate(alertmanager_alerts_invalid_total{job="cortex/alertmanager"}[2m]))'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
                common.PromGraph(
                    title="Notifications",
                    expressions=[
                        (
                            "{{integration}}",
                            'sum by (integration)(rate(alertmanager_notifications_total{job="cortex/alertmanager"}[2m]))'
                        ),
                    ],
                    yAxes=common.OPS_AXIS,
                ),
            ]
        ),
        G.Row(
            title='Alertmanager fetching configs',
            collapse=True,
            panels=[
                common.QPSGraph('cortex_configs', 'Configs', 'cortex/alertmanager'),
                common.PromGraph(
                    title="Configs Latency",
                    expressions=[
                        (
                            "99th centile",
                            'histogram_quantile(0.99, sum(rate(cortex_configs_request_duration_seconds_bucket{job="cortex/alertmanager"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "50th centile",
                            'histogram_quantile(0.50, sum(rate(cortex_configs_request_duration_seconds_bucket{job="cortex/alertmanager"}[2m])) by (le)) * 1e3'
                        ),
                        (
                            "Mean",
                            'sum(rate(cortex_configs_request_duration_seconds_sum{job="cortex/alertmanager"}[2m])) / sum(rate(cortex_configs_request_duration_seconds_count{job="cortex/alertmanager"}[2m])) * 1e3'
                        ),
                    ],
                    yAxes=common.LATENCY_AXES,
                ),
            ]
        ),
        common.REDRow('cortex', 'Alertmanager', 'cortex/alertmanager'),
        G.Row(
            [
                common.PromGraph(
                    title="Known Configurations",
                    expressions=[
                        ("{{instance}}", 'cortex_alertmanager_configs_total{job="cortex/alertmanager"}'),
                    ],
                ),
                common.PromGraph(
                    title="Cluster Members",
                    expressions=[
                        ("{{instance}}", 'sum(alertmanager_cluster_members{job="cortex/alertmanager"}) by (instance)'),
                    ],
                ),
            ]
        ),
    ],
)
