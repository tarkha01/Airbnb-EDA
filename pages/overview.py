import dash
import plotly.express as px
from dash import dcc, html
import dash_bootstrap_components as dbc

from utils.data import (
    df_train,
    AIRBNB_RED, AIRBNB_TEAL, AIRBNB_DARK,
    kpi_card, section_header, plot_card,
)

dash.register_page(__name__, path="/", name="Overview", order=0)

# ── Static figures ────────────────────────────────────────────────────────────
_total_users     = len(df_train)
_converted       = (df_train["country_destination"] != "NDF").sum()
_conversion_rate = f"{100 * _converted / _total_users:.1f}%"
_top_dest        = (
    df_train[df_train["country_destination"] != "NDF"]["country_destination"]
    .value_counts().index[0]
)
_median_age = f'{df_train["age"].median():.0f} yrs'
_converted_str = f"{_converted:,}"

dest_counts = df_train["country_destination"].value_counts().reset_index()
dest_counts.columns = ["Destination", "Count"]

fig_dest = px.bar(
    dest_counts, x="Destination", y="Count", text="Count",
    color="Destination",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    title="Booking Destination Distribution",
    template="plotly_white",
)
fig_dest.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
fig_dest.update_layout(showlegend=False, margin=dict(t=40, b=10))

growth_df = (
    df_train.groupby(df_train["date_account_created"].dt.to_period("M").astype(str))
    .size().reset_index(name="New Accounts")
)
fig_growth = px.line(
    growth_df, x="date_account_created", y="New Accounts", markers=True,
    title="Platform Adoption: Monthly Account Growth (2010–2014)",
    labels={"date_account_created": "Month"},
    template="plotly_white",
)
fig_growth.update_traces(line_color=AIRBNB_RED, line_width=2)
fig_growth.update_layout(margin=dict(t=40, b=10))

device_counts = df_train["first_device_type"].value_counts().reset_index()
device_counts.columns = ["Device Type", "Count"]
fig_device = px.pie(
    device_counts, names="Device Type", values="Count", hole=0.4,
    title="Device Type Distribution",
    color_discrete_sequence=px.colors.qualitative.Set3,
    template="plotly_white",
)
fig_device.update_traces(textposition="inside", textinfo="percent+label")
fig_device.update_layout(margin=dict(t=40, b=10))

# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div([
    dbc.Container([
        html.Br(),
        section_header(
            "Platform Overview",
            "High-level KPIs and key patterns across all Airbnb users",
        ),
        dbc.Row([
            dbc.Col(kpi_card("fa-users",       f"{_total_users:,}", "Total Training Users"),          md=3),
            dbc.Col(kpi_card("fa-check-circle", _converted_str,     "Users Who Booked", AIRBNB_TEAL), md=3),
            dbc.Col(kpi_card("fa-percent",      _conversion_rate,   "Conversion Rate",  "#FC642D"),   md=3),
            dbc.Col(kpi_card("fa-globe",        _top_dest,          "Top Destination",  "#767676"),   md=3),
        ], className="mb-4 g-3"),

        dbc.Row([
            dbc.Col(plot_card(fig_dest,   "Booking Destination Distribution", 420), md=8),
            dbc.Col(plot_card(fig_device, "Device Type Breakdown",            420), md=4),
        ]),
        dbc.Row([
            dbc.Col(plot_card(fig_growth, "Monthly Account Growth", 360), md=12),
        ]),

        dbc.Card([
            dbc.CardHeader(html.Span("Key Insight", className="fw-bold")),
            dbc.CardBody(
                html.P(
                    "The majority of users never complete a booking (NDF — No Destination Found). "
                    "Among users who do book, the United States is overwhelmingly the top destination. "
                    "Mac / Apple devices dominate the user base, reflecting a tech-savvy, "
                    "affluent demographic. Signups grew exponentially from 2010 to mid-2014.",
                    className="mb-0",
                )
            ),
        ], className="shadow-sm border-0 mb-4",
           style={"borderLeft": f"4px solid {AIRBNB_RED}"}),
    ], fluid=True),
])
