import dash
import plotly.express as px
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from utils.data import (
    df_all, df_train,
    AIRBNB_RED, AIRBNB_TEAL,
    YEARS,
    section_header,
)

dash.register_page(__name__, path="/trends", name="Trends", order=2)

# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div([
    dbc.Container([
        html.Br(),
        section_header(
            "Booking & Signup Trends",
            "Analyse how user acquisition and booking behaviour changed over time",
        ),
        dbc.Card([
            dbc.CardHeader("Controls", className="fw-semibold"),
            dbc.CardBody(dbc.Row([
                dbc.Col([
                    html.Label("Select Year", className="fw-semibold small"),
                    dcc.Dropdown(
                        id="year-dropdown-trends",
                        options=[{"label": str(y), "value": y} for y in YEARS],
                        value=2014, clearable=False,
                    ),
                ], md=4),
                dbc.Col([
                    html.Label("Breakdown By", className="fw-semibold small"),
                    dcc.Dropdown(
                        id="breakdown-dropdown",
                        options=[
                            {"label": "Age Group",     "value": "member_age_bins"},
                            {"label": "Gender",        "value": "gender"},
                            {"label": "Signup Method", "value": "signup_method"},
                            {"label": "Device Type",   "value": "first_device_type"},
                        ],
                        value="member_age_bins", clearable=False,
                    ),
                ], md=4),
                dbc.Col([
                    html.Label("Search Destination", className="fw-semibold small"),
                    dbc.Input(
                        id="dest-search",
                        placeholder="e.g. US, FR, DE …",
                        type="text", debounce=True,
                    ),
                ], md=4),
            ])),
        ], className="shadow-sm border-0 mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Monthly Signups (selected year)"),
                dbc.CardBody(dcc.Graph(id="monthly-bar", style={"height": "380px"})),
            ], className="shadow-sm border-0 mb-4"), md=12),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Monthly Signups by Breakdown Group"),
                dbc.CardBody(dcc.Graph(id="monthly-line", style={"height": "400px"})),
            ], className="shadow-sm border-0 mb-4"), md=8),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Destination Filter Results"),
                dbc.CardBody(dcc.Graph(id="dest-filter-chart", style={"height": "400px"})),
            ], className="shadow-sm border-0 mb-4"), md=4),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Country vs Age Distribution (Box)"),
                dbc.CardBody(dcc.Graph(id="country-age-box", style={"height": "400px"})),
            ], className="shadow-sm border-0 mb-4"), md=12),
        ]),
    ], fluid=True),
])


# ── Callbacks ─────────────────────────────────────────────────────────────────
@callback(
    Output("monthly-bar",        "figure"),
    Output("monthly-line",       "figure"),
    Output("dest-filter-chart",  "figure"),
    Output("country-age-box",    "figure"),
    Input("year-dropdown-trends", "value"),
    Input("breakdown-dropdown",   "value"),
    Input("dest-search",          "value"),
)
def update_trends(year_sel, breakdown, dest_query):
    dfy = df_all[df_all["acc_year"] == year_sel].copy()
    dfy["monthYear"] = dfy["date_account_created"].dt.strftime("%m-%Y")

    monthly = dfy.groupby("monthYear").size().reset_index(name="Count")
    monthly = monthly.sort_values("monthYear")
    fm = px.bar(
        monthly, x="monthYear", y="Count", text="Count",
        color_discrete_sequence=[AIRBNB_RED],
        labels={"monthYear": "Month", "Count": "Signups"},
        template="plotly_white",
    )
    fm.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fm.update_layout(margin=dict(t=10, b=10), xaxis_tickangle=-45)

    valid = dfy.dropna(subset=[breakdown, "monthYear"])
    grp   = valid.groupby(["monthYear", breakdown]).size().reset_index(name="Count")
    grp   = grp.sort_values("monthYear")
    fl = px.line(
        grp, x="monthYear", y="Count", color=breakdown, markers=True,
        labels={"monthYear": "Month"},
        color_discrete_sequence=px.colors.qualitative.Plotly,
        template="plotly_white",
    )
    fl.update_layout(
        margin=dict(t=10, b=10), xaxis_tickangle=-45,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )

    train_y = df_train[df_train["acc_year"] == year_sel].copy()
    if dest_query:
        q = dest_query.strip().upper()
        train_y = train_y[
            train_y["country_destination"].str.upper().str.contains(q, na=False)
        ]
    dc = train_y["country_destination"].value_counts().reset_index()
    dc.columns = ["Destination", "Count"]
    fd = px.bar(
        dc, x="Destination", y="Count", text="Count",
        color_discrete_sequence=[AIRBNB_TEAL],
        template="plotly_white",
    )
    fd.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fd.update_layout(showlegend=False, margin=dict(t=10, b=10))

    fc = px.box(
        df_train.dropna(subset=["age", "country_destination"]),
        x="country_destination", y="age",
        color="country_destination",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"country_destination": "Country", "age": "Age"},
        template="plotly_white",
    )
    fc.update_layout(
        showlegend=False, margin=dict(t=10, b=10),
        yaxis=dict(range=[15, 100]),
    )

    return fm, fl, fd, fc
