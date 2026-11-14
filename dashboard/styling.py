"""Tema dan CSS untuk dashboard Commodex: tiga logam di atas latar navy."""

import streamlit as st

THEME = {
    "bg": "#0d1219",
    "panel": "#131a26",
    "border": "#232d3f",
    "text": "#F2EFE8",
    "muted": "#8A94A6",
    "bronze": "#E9AE74",
    "silver": "#DDE3EC",
    "gold": "#FFD866",
    "up": "#3DDC97",
    "down": "#FF6B6B",
}

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp {
    background: radial-gradient(circle at 12% 0%, #18233a 0%, var(--bg) 45%);
    color: var(--text);
}
#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1200px; }

/* hero */
.hero-title { font-size: 2.8rem !important; font-weight: 700; letter-spacing: -1px; line-height: 1.1; margin: 0; color: var(--text); }
.hero-sub { color: var(--muted); font-size: 0.95rem; margin: 0.2rem 0 1rem 0; }
.medals { display: inline-flex; gap: 6px; margin-right: 12px; vertical-align: middle; }
.medal { width: 14px; height: 14px; border-radius: 50%; display: inline-block; }
.pill {
    display: inline-flex; align-items: center; gap: 8px;
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--silver);
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 999px; padding: 5px 14px; margin-bottom: 1.4rem;
}
.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--up); box-shadow: 0 0 8px var(--up); animation: pulse 2.4s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .35; } }

/* kartu KPI */
div[data-testid="stMetric"] {
    background: var(--panel); border: 1px solid var(--border);
    border-top: 3px solid var(--gold); border-radius: 12px;
    padding: 1rem 1.2rem; transition: transform .2s ease, border-color .2s ease;
}
div[data-testid="stMetric"]:hover { transform: translateY(-3px); border-color: var(--gold); }
div[data-testid="stMetric"] label, div[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.78rem; }
div[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace; font-weight: 600; font-size: 1.45rem; }
div[data-testid="stMetricValue"] > div { overflow: visible !important; text-overflow: clip !important; white-space: nowrap; }

/* tab, sidebar, tabel */
.stTabs [data-baseweb="tab-list"] { gap: 22px; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { color: var(--muted); }
.stTabs [aria-selected="true"] { color: var(--gold) !important; }
[data-testid="stSidebar"] { background: #0a0f17; border-right: 1px solid var(--border); }
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.stButton > button { border: 1px solid var(--gold); background: transparent; color: var(--gold); border-radius: 8px; }
.stButton > button:hover { background: var(--gold); color: #0d1219; }
"""


def inject_css() -> None:
    root = ":root{" + "".join(f"--{k}:{v};" for k, v in THEME.items()) + "}"
    st.markdown(f"<style>{root}{_CSS}</style>", unsafe_allow_html=True)


def hero(title: str, subtitle: str, status: str | None = None) -> None:
    medals = "".join(
        f'<span class="medal" style="background:{THEME[k]}"></span>' for k in ("bronze", "silver", "gold")
    )
    pill = f'<div class="pill"><span class="dot"></span>{status}</div>' if status else ""
    st.markdown(
        f'<div class="hero-title"><span class="medals">{medals}</span>{title}</div>'
        f'<p class="hero-sub">{subtitle}</p>{pill}',
        unsafe_allow_html=True,
    )


def style_fig(fig, height: int = 420):
    """Samakan tampilan grafik Plotly dengan tema."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=THEME["muted"], family="Sora"),
        margin=dict(l=0, r=0, t=40, b=40),
        hovermode="x unified",
        title=dict(font=dict(size=15, color=THEME["text"])),
    )
    fig.update_xaxes(showgrid=False, linecolor=THEME["border"])
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)", zeroline=False)
    return fig