import os
import numpy as np
import pandas as pd
import warnings

from dash import dcc, html
import dash_bootstrap_components as dbc

warnings.filterwarnings("ignore")

# ── Paths ────────────────────────────────────────────────────────────────────
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TRAIN_PATH = os.path.join(_BASE, "train_users_2.csv")
_TEST_PATH  = os.path.join(_BASE, "test_users.csv")

# ── Raw load ─────────────────────────────────────────────────────────────────
df_train = pd.read_csv(_TRAIN_PATH)
df_test  = pd.read_csv(_TEST_PATH)

df_train["date_account_created"]  = pd.to_datetime(df_train["date_account_created"])
df_train["timestamp_first_active"] = pd.to_datetime(
    df_train["timestamp_first_active"].astype(str), format="mixed"
)

df_all = pd.concat((df_train, df_test), axis=0, ignore_index=True)
df_all["date_account_created"]   = pd.to_datetime(df_all["date_account_created"])
df_all["timestamp_first_active"] = pd.to_datetime(
    df_all["timestamp_first_active"].astype(str), format="mixed"
)

# ── Clean age ────────────────────────────────────────────────────────────────
df_all.loc[df_all["age"] < 15,   "age"] = np.nan
df_all.loc[df_all["age"] >= 100, "age"] = np.nan
df_train.loc[df_train["age"] < 15,   "age"] = np.nan
df_train.loc[df_train["age"] >= 100, "age"] = np.nan

# ── Year column ──────────────────────────────────────────────────────────────
df_all["acc_year"]   = df_all["date_account_created"].dt.year
df_train["acc_year"] = df_train["date_account_created"].dt.year

# ── Age bins ─────────────────────────────────────────────────────────────────
def age_bin(x):
    if   18 < x <= 20: return "18-20"
    elif 20 < x <= 30: return "20-30"
    elif 30 < x <= 40: return "30-40"
    elif 40 < x <= 50: return "40-50"
    elif 50 < x <= 60: return "50-60"
    elif 60 < x <= 70: return "60-70"
    elif 70 < x <= 100: return "70+"
    return np.nan

df_all["member_age_bins"] = df_all["age"].apply(
    lambda x: age_bin(x) if pd.notna(x) else np.nan
)

# ── Brand colours ────────────────────────────────────────────────────────────
AIRBNB_RED   = "#FF5A5F"
AIRBNB_TEAL  = "#00A699"
AIRBNB_DARK  = "#484848"
AIRBNB_LIGHT = "#F7F7F7"

YEARS = sorted(df_all["acc_year"].dropna().unique().astype(int).tolist())

# ── Reusable layout helpers ──────────────────────────────────────────────────
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
