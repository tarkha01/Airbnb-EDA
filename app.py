import dash
from dash import html
import dash_bootstrap_components as dbc

from utils.data import AIRBNB_RED, AIRBNB_DARK, AIRBNB_LIGHT

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
)
app.title = "Airbnb User Analytics"
server = app.server  # expose for gunicorn

# ── Navbar ────────────────────────────────────────────────────────────────────
navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand(
            [
                html.I(className="fa fa-home fa-lg me-2", style={"color": AIRBNB_RED}),
                html.Span("Airbnb User Analytics", className="fw-bold fs-5",
                          style={"color": AIRBNB_DARK}),
            ],
            href="/",
            style={"textDecoration": "none"},
        ),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink("Overview",     href="/",              active="exact")),
                dbc.NavItem(dbc.NavLink("Demographics", href="/demographics",  active="exact")),
                dbc.NavItem(dbc.NavLink("Trends",       href="/trends",        active="exact")),
            ],
            navbar=True, className="ms-auto",
        ),
    ]),
    color="white", dark=False, className="shadow-sm mb-0",
    style={"borderBottom": f"3px solid {AIRBNB_RED}"},
)

# ── Root layout ───────────────────────────────────────────────────────────────
app.layout = html.Div(
    [navbar, dash.page_container],
    style={
        "backgroundColor": AIRBNB_LIGHT,
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', sans-serif",
    },
)

if __name__ == "__main__":
    app.run(debug=True, port=8050)
