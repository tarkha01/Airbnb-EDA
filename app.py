import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Data Loading & Preprocessing ──────────────────────────────────────────────
df_train = pd.read_csv(r"c:\Users\rozii\Desktop\Airnb\train_users_2.csv")
df_test  = pd.read_csv(r"c:\Users\rozii\Desktop\Airnb\test_users.csv")

df_train["date_account_created"]  = pd.to_datetime(df_train["date_account_created"])
df_train["timestamp_first_active"] = pd.to_datetime(
    df_train["timestamp_first_active"].astype(str), format="mixed"
)

df_all = pd.concat((df_train, df_test), axis=0, ignore_index=True)
df_all["date_account_created"]   = pd.to_datetime(df_all["date_account_created"])
df_all["timestamp_first_active"] = pd.to_datetime(
    df_all["timestamp_first_active"].astype(str), format="mixed"
)

# clean age
df_all.loc[df_all["age"] < 15,  "age"] = np.nan
df_all.loc[df_all["age"] >= 100,"age"] = np.nan
df_train.loc[df_train["age"] < 15,  "age"] = np.nan
df_train.loc[df_train["age"] >= 100,"age"] = np.nan

# year column
df_all["acc_year"]   = df_all["date_account_created"].dt.year
df_train["acc_year"] = df_train["date_account_created"].dt.year

# age bins
def age_bin(x):
    if   18 < x <= 20: return "18-20"
    elif 20 < x <= 30: return "20-30"
    elif 30 < x <= 40: return "30-40"
    elif 40 < x <= 50: return "40-50"
    elif 50 < x <= 60: return "50-60"
    elif 60 < x <= 70: return "60-70"
    elif 70 < x <= 100:return "70+"
    return np.nan

df_all["member_age_bins"] = df_all["age"].apply(
    lambda x: age_bin(x) if pd.notna(x) else np.nan
)

AIRBNB_RED   = "#FF5A5F"
AIRBNB_TEAL  = "#00A699"
AIRBNB_DARK  = "#484848"
AIRBNB_LIGHT = "#F7F7F7"

YEARS = sorted(df_all["acc_year"].dropna().unique().astype(int).tolist())

# ── App Initialisation ─────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    use_pages=False,
    suppress_callback_exceptions=True,
)
app.title = "Airbnb User Analytics"

# ── Reusable helpers ───────────────────────────────────────────────────────────
def kpi_card(icon, value, label, color=AIRBNB_RED):
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.I(className=f"fa {icon} fa-2x me-3", style={"color": color}),
                html.Div([
                    html.H4(value, className="mb-0 fw-bold"),
                    html.P(label, className="mb-0 text-muted small"),
                ]),
            ], className="d-flex align-items-center"),
        ]),
        className="shadow-sm border-0 h-100",
    )


def section_header(title, subtitle=""):
    return html.Div([
        html.H5(title, className="fw-bold mb-0", style={"color": AIRBNB_DARK}),
        html.P(subtitle, className="text-muted small mb-0") if subtitle else None,
        html.Hr(className="mt-2"),
    ])


def plot_card(fig, title="", height=400):
    return dbc.Card([
        dbc.CardHeader(html.Span(title, className="fw-semibold")) if title else None,
        dbc.CardBody(dcc.Graph(figure=fig, style={"height": f"{height}px"})),
    ], className="shadow-sm border-0 mb-4")


# ── NAV BAR ────────────────────────────────────────────────────────────────────
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
                dbc.Col(html.I(className="fa fa-home fa-lg me-2",
                               style={"color": AIRBNB_RED})),
                dbc.Col(dbc.NavbarBrand("Airbnb User Analytics",
                                        className="fw-bold fs-5",
                                        style={"color": AIRBNB_DARK})),
            ], align="center"),
            href="#", style={"textDecoration": "none"},
        ),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Overview",    id="nav-overview",    n_clicks=0,
                                    className="nav-link-custom")),
            dbc.NavItem(dbc.NavLink("Demographics",id="nav-demographics",n_clicks=0,
                                    className="nav-link-custom")),
            dbc.NavItem(dbc.NavLink("Trends",      id="nav-trends",      n_clicks=0,
                                    className="nav-link-custom")),
        ], navbar=True, className="ms-auto"),
    ]),
    color="white", dark=False, className="shadow-sm mb-0",
    style={"borderBottom": f"3px solid {AIRBNB_RED}"},
)

# ── PAGE 1 : OVERVIEW ─────────────────────────────────────────────────────────
total_users       = len(df_train)
converted         = (df_train["country_destination"] != "NDF").sum()
conversion_rate   = f"{100 * converted / total_users:.1f}%"
top_dest          = df_train[df_train["country_destination"] != "NDF"]["country_destination"].value_counts().index[0]
median_age        = f'{df_train["age"].median():.0f} yrs'

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

page_overview = html.Div([
    dbc.Container([
        html.Br(),
        section_header("Platform Overview",
                        "High-level KPIs and key patterns across all Airbnb users"),
        dbc.Row([
            dbc.Col(kpi_card("fa-users",      f"{total_users:,}",    "Total Training Users"),    md=3),
            dbc.Col(kpi_card("fa-check-circle",converted_str := f"{converted:,}",
                             "Users Who Booked",  AIRBNB_TEAL), md=3),
            dbc.Col(kpi_card("fa-percent",    conversion_rate,       "Conversion Rate",  "#FC642D"), md=3),
            dbc.Col(kpi_card("fa-globe",      top_dest,              "Top Destination",  "#767676"), md=3),
        ], className="mb-4 g-3"),

        dbc.Row([
            dbc.Col(plot_card(fig_dest,   "Booking Destination Distribution", 420), md=8),
            dbc.Col(plot_card(fig_device, "Device Type Breakdown",            420), md=4),
        ]),
        dbc.Row([
            dbc.Col(plot_card(fig_growth, "Monthly Account Growth", 360), md=12),
        ]),

        # Insight card
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

# ── PAGE 2 : DEMOGRAPHICS ─────────────────────────────────────────────────────
page_demographics = html.Div([
    dbc.Container([
        html.Br(),
        section_header("User Demographics",
                        "Explore gender, age and device profiles — filter interactively"),
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

# ── PAGE 3 : TRENDS ───────────────────────────────────────────────────────────
page_trends = html.Div([
    dbc.Container([
        html.Br(),
        section_header("Booking & Signup Trends",
                        "Analyse how user acquisition and booking behaviour changed over time"),
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
                            {"label": "Age Group",  "value": "member_age_bins"},
                            {"label": "Gender",     "value": "gender"},
                            {"label": "Signup Method", "value": "signup_method"},
                            {"label": "Device Type","value": "first_device_type"},
                        ],
                        value="member_age_bins", clearable=False,
                    ),
                ], md=4),
                dbc.Col([
                    html.Label("Search Destination", className="fw-semibold small"),
                    dbc.Input(id="dest-search", placeholder="e.g. US, FR, DE …",
                              type="text", debounce=True),
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

# ── Main Layout ────────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="active-page", data="overview"),
    navbar,
    html.Div(id="page-content"),
], style={"backgroundColor": AIRBNB_LIGHT, "minHeight": "100vh",
          "fontFamily": "'Segoe UI', sans-serif"})


# ── CALLBACKS ─────────────────────────────────────────────────────────────────

# Page routing
@app.callback(
    Output("page-content", "children"),
    Output("active-page", "data"),
    Input("nav-overview",    "n_clicks"),
    Input("nav-demographics","n_clicks"),
    Input("nav-trends",      "n_clicks"),
    State("active-page", "data"),
    prevent_initial_call=False,
)
def render_page(n_ov, n_dem, n_tr, current):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]["prop_id"] == ".":
        return page_overview, "overview"
    btn = ctx.triggered[0]["prop_id"].split(".")[0]
    if btn == "nav-overview":
        return page_overview, "overview"
    if btn == "nav-demographics":
        return page_demographics, "demographics"
    return page_trends, "trends"


# Demographics callbacks
@app.callback(
    Output("gender-bar",     "figure"),
    Output("age-hist",       "figure"),
    Output("gender-age-box", "figure"),
    Output("signup-bar",     "figure"),
    Input("age-slider",      "value"),
    Input("gender-filter",   "value"),
    Input("year-filter-demo","value"),
)
def update_demographics(age_range, genders, years_sel):
    dff = df_all.copy()
    dff = dff[(dff["age"].isna()) | ((dff["age"] >= age_range[0]) & (dff["age"] <= age_range[1]))]
    if genders:
        dff = dff[dff["gender"].isin(genders)]
    if years_sel:
        dff = dff[dff["acc_year"].isin(years_sel)]

    # Gender bar
    g_counts = dff["gender"].value_counts().reset_index()
    g_counts.columns = ["Gender", "Count"]
    fg = px.bar(g_counts, x="Gender", y="Count", text="Count",
                color="Gender", color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_white")
    fg.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fg.update_layout(showlegend=False, margin=dict(t=10, b=10))

    # Age histogram
    fa = px.histogram(dff.dropna(subset=["age"]), x="age", nbins=40,
                      color_discrete_sequence=[AIRBNB_TEAL],
                      template="plotly_white",
                      labels={"age": "User Age"})
    fa.update_layout(yaxis_title="Count", margin=dict(t=10, b=10))

    # Box gender-age
    fb = px.box(dff.dropna(subset=["age","gender"]), x="gender", y="age",
                color="gender", color_discrete_sequence=px.colors.qualitative.Safe,
                template="plotly_white",
                labels={"gender": "Gender", "age": "Age"})
    fb.update_layout(showlegend=False, margin=dict(t=10, b=10))

    # Signup method
    sm = dff["signup_method"].value_counts().reset_index()
    sm.columns = ["Method", "Count"]
    fs = px.bar(sm, x="Method", y="Count", text="Count",
                color="Method", color_discrete_sequence=px.colors.qualitative.Set2,
                template="plotly_white")
    fs.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fs.update_layout(showlegend=False, margin=dict(t=10, b=10))

    return fg, fa, fb, fs


# Trends callbacks
@app.callback(
    Output("monthly-bar",       "figure"),
    Output("monthly-line",      "figure"),
    Output("dest-filter-chart", "figure"),
    Output("country-age-box",   "figure"),
    Input("year-dropdown-trends","value"),
    Input("breakdown-dropdown",  "value"),
    Input("dest-search",         "value"),
)
def update_trends(year_sel, breakdown, dest_query):
    dfy = df_all[df_all["acc_year"] == year_sel].copy()
    dfy["monthYear"] = dfy["date_account_created"].dt.strftime("%m-%Y")

    # Monthly bar
    monthly = dfy.groupby("monthYear").size().reset_index(name="Count")
    monthly = monthly.sort_values("monthYear")
    fm = px.bar(monthly, x="monthYear", y="Count", text="Count",
                color_discrete_sequence=[AIRBNB_RED],
                labels={"monthYear": "Month", "Count": "Signups"},
                template="plotly_white")
    fm.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fm.update_layout(margin=dict(t=10, b=10), xaxis_tickangle=-45)

    # Monthly line by breakdown
    valid = dfy.dropna(subset=[breakdown, "monthYear"])
    grp = valid.groupby(["monthYear", breakdown]).size().reset_index(name="Count")
    grp = grp.sort_values("monthYear")
    fl = px.line(grp, x="monthYear", y="Count", color=breakdown, markers=True,
                 labels={"monthYear": "Month"},
                 color_discrete_sequence=px.colors.qualitative.Plotly,
                 template="plotly_white")
    fl.update_layout(margin=dict(t=10, b=10), xaxis_tickangle=-45,
                     legend=dict(orientation="h", yanchor="bottom", y=1.02))

    # Destination filter
    train_y = df_train[df_train["acc_year"] == year_sel].copy()
    if dest_query:
        q = dest_query.strip().upper()
        train_y = train_y[train_y["country_destination"].str.upper().str.contains(q, na=False)]
    dc = train_y["country_destination"].value_counts().reset_index()
    dc.columns = ["Destination", "Count"]
    fd = px.bar(dc, x="Destination", y="Count", text="Count",
                color_discrete_sequence=[AIRBNB_TEAL],
                template="plotly_white")
    fd.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fd.update_layout(showlegend=False, margin=dict(t=10, b=10))

    # Country-age box (all years, training data)
    fc = px.box(df_train.dropna(subset=["age","country_destination"]),
                x="country_destination", y="age",
                color="country_destination",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                labels={"country_destination": "Country", "age": "Age"},
                template="plotly_white")
    fc.update_layout(showlegend=False, margin=dict(t=10, b=10),
                     yaxis=dict(range=[15, 100]))

    return fm, fl, fd, fc


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
