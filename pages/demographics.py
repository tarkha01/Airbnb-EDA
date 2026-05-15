import dash
import plotly.express as px
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

from utils.data import (
    df_all,
    AIRBNB_TEAL,
    YEARS,
    section_header,
)

dash.register_page(__name__, path="/demographics", name="Demographics", order=1)

# ── Layout ────────────────────────────────────────────────────────────────────
layout = html.Div([
    dbc.Container([
        html.Br(),
        section_header(
            "User Demographics",
            "Explore gender, age and device profiles — filter interactively",
        ),
        dbc.Card([
            dbc.CardHeader("Filters", className="fw-semibold"),
            dbc.CardBody(dbc.Row([
                dbc.Col([
                    html.Label("Age Range", className="fw-semibold small"),
                    dcc.RangeSlider(
                        id="age-slider", min=18, max=100, step=1,
                        value=[18, 70],
                        marks={18: "18", 30: "30", 50: "50", 70: "70", 100: "100"},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ], md=6),
                dbc.Col([
                    html.Label("Gender", className="fw-semibold small"),
                    dcc.Dropdown(
                        id="gender-filter",
                        options=[{"label": g, "value": g}
                                 for g in df_all["gender"].dropna().unique()],
                        multi=True, placeholder="All genders…",
                    ),
                ], md=3),
                dbc.Col([
                    html.Label("Year", className="fw-semibold small"),
                    dcc.Dropdown(
                        id="year-filter-demo",
                        options=[{"label": str(y), "value": y} for y in YEARS],
                        multi=True, placeholder="All years…",
                    ),
                ], md=3),
            ])),
        ], className="shadow-sm border-0 mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Gender Distribution"),
                dbc.CardBody(dcc.Graph(id="gender-bar", style={"height": "380px"})),
            ], className="shadow-sm border-0 mb-4"), md=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Age Distribution"),
                dbc.CardBody(dcc.Graph(id="age-hist", style={"height": "380px"})),
            ], className="shadow-sm border-0 mb-4"), md=6),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Age vs Gender (Box Plot)"),
                dbc.CardBody(dcc.Graph(id="gender-age-box", style={"height": "380px"})),
            ], className="shadow-sm border-0 mb-4"), md=6),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Signup Method Distribution"),
                dbc.CardBody(dcc.Graph(id="signup-bar", style={"height": "380px"})),
            ], className="shadow-sm border-0 mb-4"), md=6),
        ]),
    ], fluid=True),
])


# ── Callbacks ─────────────────────────────────────────────────────────────────
@callback(
    Output("gender-bar",      "figure"),
    Output("age-hist",        "figure"),
    Output("gender-age-box",  "figure"),
    Output("signup-bar",      "figure"),
    Input("age-slider",       "value"),
    Input("gender-filter",    "value"),
    Input("year-filter-demo", "value"),
)
def update_demographics(age_range, genders, years_sel):
    dff = df_all.copy()
    dff = dff[
        (dff["age"].isna()) |
        ((dff["age"] >= age_range[0]) & (dff["age"] <= age_range[1]))
    ]
    if genders:
        dff = dff[dff["gender"].isin(genders)]
    if years_sel:
        dff = dff[dff["acc_year"].isin(years_sel)]

    g_counts = dff["gender"].value_counts().reset_index()
    g_counts.columns = ["Gender", "Count"]
    fg = px.bar(
        g_counts, x="Gender", y="Count", text="Count",
        color="Gender", color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_white",
    )
    fg.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fg.update_layout(showlegend=False, margin=dict(t=10, b=10))

    fa = px.histogram(
        dff.dropna(subset=["age"]), x="age", nbins=40,
        color_discrete_sequence=[AIRBNB_TEAL],
        template="plotly_white",
        labels={"age": "User Age"},
    )
    fa.update_layout(yaxis_title="Count", margin=dict(t=10, b=10))

    fb = px.box(
        dff.dropna(subset=["age", "gender"]), x="gender", y="age",
        color="gender", color_discrete_sequence=px.colors.qualitative.Safe,
        template="plotly_white",
        labels={"gender": "Gender", "age": "Age"},
    )
    fb.update_layout(showlegend=False, margin=dict(t=10, b=10))

    sm = dff["signup_method"].value_counts().reset_index()
    sm.columns = ["Method", "Count"]
    fs = px.bar(
        sm, x="Method", y="Count", text="Count",
        color="Method", color_discrete_sequence=px.colors.qualitative.Set2,
        template="plotly_white",
    )
    fs.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fs.update_layout(showlegend=False, margin=dict(t=10, b=10))

    return fg, fa, fb, fs
