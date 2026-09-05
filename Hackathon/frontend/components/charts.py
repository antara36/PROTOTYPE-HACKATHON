import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from frontend.theme import CHART_COLORS, BG_PAGE, TEXT_PRIMARY, TEXT_MUTED

# Paper / plot background — transparent so the card bg shows through
_PAPER_BG = "rgba(0,0,0,0)"
_PLOT_BG  = "rgba(0,0,0,0)"
_FONT     = dict(family="Inter, Outfit, sans-serif", color=TEXT_PRIMARY, size=12)
_GRID     = dict(color="rgba(0,0,0,0.06)")


def _base_layout(**kwargs) -> dict:
    return dict(
        paper_bgcolor=_PAPER_BG,
        plot_bgcolor=_PLOT_BG,
        font=_FONT,
        margin=dict(t=48, b=24, l=20, r=20),
        xaxis=dict(gridcolor=_GRID["color"], zeroline=False),
        yaxis=dict(gridcolor=_GRID["color"], zeroline=False),
        **kwargs
    )


def plot_allocation_donut(df: pd.DataFrame):
    fig = px.pie(
        df,
        names="Asset",
        values="Amount_INR",
        hole=0.58,
        color_discrete_sequence=CHART_COLORS,
        title="Asset Allocation Breakdown"
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#F7F3EE", width=3))
    )
    fig.update_layout(
        showlegend=True,
        paper_bgcolor=_PAPER_BG,
        plot_bgcolor=_PLOT_BG,
        font=_FONT,
        margin=dict(t=48, b=24, l=20, r=20),
        title_font=dict(size=14, color=TEXT_PRIMARY, family="Inter, sans-serif"),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.25,
            xanchor="center", x=0.5,
            font=dict(size=11, color=TEXT_MUTED)
        )
    )
    return fig


def plot_asset_class_bars(class_breakdown: dict, max_equity_limit: float = 0.40):
    classes = list(class_breakdown.keys())
    weights = [round(w * 100, 1) for w in class_breakdown.values()]
    colors  = [
        "#EF4444" if c == "Equity" and weights[i] > max_equity_limit * 100
        else CHART_COLORS[i % len(CHART_COLORS)]
        for i, c in enumerate(classes)
    ]

    fig = go.Figure(go.Bar(
        x=classes,
        y=weights,
        marker_color=colors,
        marker_line_width=0,
        text=[f"{w:.1f}%" for w in weights],
        textposition="outside",
        textfont=dict(family="Inter, sans-serif", size=11, color=TEXT_PRIMARY)
    ))
    fig.add_hline(
        y=max_equity_limit * 100,
        line_dash="dot",
        line_color="#EF4444",
        line_width=1.5,
        annotation_text=f"Max Equity Cap ({max_equity_limit*100:.0f}%)",
        annotation_position="top right",
        annotation_font_size=11,
        annotation_font_color="#EF4444"
    )
    fig.update_layout(
        title="Asset Class Exposure vs Policy Limits",
        yaxis_title="Allocation (%)",
        yaxis=dict(range=[0, max(weights + [max_equity_limit * 100]) + 15],
                   gridcolor=_GRID["color"], zeroline=False),
        **{k: v for k, v in _base_layout().items() if k not in ("yaxis",)},
        bargap=0.35
    )
    return fig


def plot_stress_impact_bars(asset_breakdown: list):
    df = pd.DataFrame(asset_breakdown)
    df["Impact_Lakhs"] = df["Impact_INR"] / 1e5
    colors = ["#EF4444" if x < 0 else "#10B981" for x in df["Impact_Lakhs"]]

    fig = go.Figure(go.Bar(
        x=df["Asset"],
        y=df["Impact_Lakhs"],
        marker_color=colors,
        marker_line_width=0,
        text=[f"₹{x:,.2f} L" for x in df["Impact_Lakhs"]],
        textposition="outside",
        textfont=dict(family="Inter, sans-serif", size=11, color=TEXT_PRIMARY)
    ))
    fig.update_layout(
        title="Simulated Stress P&L by Asset (in ₹ Lakhs)",
        yaxis_title="Impact (₹ Lakhs)",
        **_base_layout(),
        bargap=0.35
    )
    return fig


def plot_optimization_comparison(options_dict: dict, current_weights: dict):
    assets    = list(current_weights.keys())
    curr_vals = [current_weights[a] * 100 for a in assets]
    opt_a_vals = [options_dict["option_a"]["weights"].get(a, 0.0) * 100 for a in assets]
    opt_b_vals = [options_dict["option_b"]["weights"].get(a, 0.0) * 100 for a in assets]
    opt_c_vals = [options_dict["option_c"]["weights"].get(a, 0.0) * 100 for a in assets]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Current",                    x=assets, y=curr_vals,  marker_color="#9CA3AF", marker_line_width=0))
    fig.add_trace(go.Bar(name="Option A (Conservative)",    x=assets, y=opt_a_vals, marker_color="#C4A8F5", marker_line_width=0))
    fig.add_trace(go.Bar(name="Option B (Least-Disruptive ⭐)", x=assets, y=opt_b_vals, marker_color="#8DD9B3", marker_line_width=0))
    fig.add_trace(go.Bar(name="Option C (Return-Preserving)", x=assets, y=opt_c_vals, marker_color="#8ABFF5", marker_line_width=0))

    fig.update_layout(
        barmode="group",
        title="Asset Allocation Shift Across Optimization Alternatives (%)",
        yaxis_title="Allocation (%)",
        **_base_layout(),
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.28,
            xanchor="center", x=0.5, font=dict(size=11, color=TEXT_MUTED)
        ),
        bargap=0.18, bargroupgap=0.08
    )
    return fig
