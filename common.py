"""Common configuration across dashboards.

   Copyright 2019 Weaveworks Inc

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import grafanalib.core as G
import grafanalib.weave as W
from grafanalib import prometheus
"""A single Y axis of milliseconds. Use for latency graphs."""
LATENCY_AXES = G.single_y_axis(format=G.MILLISECONDS_FORMAT)
"""A single Y axis counting operations. Use for requests per second, etc."""
OPS_AXIS = G.single_y_axis(format=G.OPS_FORMAT)
"""The name of the data source for our Prometheus service."""
PROMETHEUS = "$datasource"

QPS_SERIES_OVERRIDES = [
    {
        "alias": "/^1../",
        "color": W.YELLOW
    },
    {
        "alias": "/^2../",
        "color": W.GREEN
    },
    {
        "alias": "/^3../",
        "color": W.BLUE
    },
    {
        "alias": "/^4../",
        "color": W.ORANGE
    },
    {
        "alias": "/^5../",
        "color": W.RED
    },
    {
        "alias": "success",
        "color": W.GREEN
    },
    {
        "alias": "error",
        "color": W.RED
    },
]


def PromGraph(*args, **kwargs):
    """A graph of data from our Prometheus."""

    kwargs_with_defaults = dict(
        tooltip=G.Tooltip(sort=G.SORT_DESC),
        nullPointMode=G.NULL_AS_NULL,
    )
    kwargs_with_defaults.update(kwargs)

    return prometheus.PromGraph(data_source=PROMETHEUS, *args, **kwargs_with_defaults)


def Dashboard(**kwargs):
    """Standard Weave Cloud dashboard.

    Automatically sets panel ids and applies events from Weave Cloud as annotations.
    """

    defaultTemplates = [G.Template(
        label="Datasource",
        name="datasource",
        type="datasource",
        query="prometheus",
    )]

    if "templating" in kwargs:
        extraTemplates = kwargs["templating"].list
    else:
        extraTemplates = []

    kwargs["templating"] = G.Templating(list=defaultTemplates + extraTemplates)

    return G.Dashboard(
        refresh='1m',  # Override the default of 10s
        **kwargs
    ).auto_panel_ids()


def PercentageAxes(label=None, max=1):
    """Y axes that show a percentage based on a unit value."""
    return G.single_y_axis(
        format=G.PERCENT_UNIT_FORMAT,
        label=label,
        logBase=1,
        max=max,
        min=0,
    )


def QPSGraph(namespace, graphName, job, metric_root="request", extra_conditions=""):
    expr_template = 'rate({ns}_{mroot}_duration_seconds_count{{job="{job}"{extra}}}[1m])'
    return StatusQPSGraph(
        data_source=PROMETHEUS,
        title='{name} QPS'.format(name=graphName),
        expression=expr_template.format(ns=namespace, mroot=metric_root, job=job, extra=extra_conditions)
    )


def StatusQPSGraph(data_source, title, expression, **kwargs):
    """Create a graph of QPS, coloured by status code.

    :param title: Title of the graph.
    :param expression: Format and PromQL expression; must sum by label
                       which is http code like 404 or "success" and "error"
    :param kwargs: Passed on to Graph.
    """
    return W.stacked(
        prometheus.PromGraph(
            data_source=data_source,
            title=title,
            expressions=[('{{status_code}}', 'sum by (status_code)(%s)' % (expression))],
            seriesOverrides=QPS_SERIES_OVERRIDES,
            legend=G.Legend(hideZero=True),
            yAxes=[
                G.YAxis(format=G.OPS_FORMAT),
                G.YAxis(format=G.SHORT_FORMAT),
            ],
            **kwargs
        )
    )


def LatencyGraph(namespace, graphName, job, rule_root="job:", metric_root="request", extra_conditions=""):
    return PromGraph(
        title='{name} Latency'.format(name=graphName),
        expressions=[
            (
                '99th centile', '{rroot}{ns}_{mroot}_duration_seconds:99quantile{{job="{job}"{extra}}} * 1e3'
                .format(rroot=rule_root, ns=namespace, mroot=metric_root, job=job, extra=extra_conditions)
            ),
            (
                '50th centile', '{rroot}{ns}_{mroot}_duration_seconds:50quantile{{job="{job}"{extra}}} * 1e3'
                .format(rroot=rule_root, ns=namespace, mroot=metric_root, job=job, extra=extra_conditions)
            ),
            (
                'Mean',
                'sum(rate({ns}_{mroot}_duration_seconds_sum{{ws="false",job="{job}"{extra}}}[5m])) * 1e3 / sum(rate({ns}_{mroot}_duration_seconds_count{{ws="false",job="{job}"{extra}}}[5m]))'
                .format(ns=namespace, mroot=metric_root, job=job, extra=extra_conditions)
            ),
        ],
        yAxes=LATENCY_AXES,
    )


def REDRow(namespace, graphName, job, rule_root="job:", metric_root="request", extra_conditions="", collapse=False):
    return G.Row(
        title='%s QPS & Latency' % (graphName, ),
        collapse=collapse,
        panels=[
            QPSGraph(namespace, graphName, job, metric_root, extra_conditions),
            LatencyGraph(namespace, graphName, job, rule_root, metric_root, extra_conditions),
        ]
    )

