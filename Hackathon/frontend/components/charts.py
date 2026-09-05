import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

COLOR_PALETTE = ["#3B82F6", "#F59E0B", "#10B981", "#8B5CF6", "#EC4899", "#06B6D4"]

def plot_allocation_donut(df: pd.DataFrame):
    fig = px.pie(
        df,
        names="Asset",
        values="Amount_INR",
        hole=0.55,
        color_discrete_sequence=COLOR_PALETTE,
        title="Asset Allocation Breakdown"
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color="#0F172A", width=2))
    )
    fig.update_layout(
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def plot_asset_class_bars(class_breakdown: dict, max_equity_limit: float = 0.40):
    classes = list(class_breakdown.keys())
    weights = [round(w * 100, 1) for w in class_breakdown.values()]
    colors = ["#EF4444" if c == "Equity" and weights[i] > max_equity_limit*100 else "#3B82F6" for i, c in enumerate(classes)]

    fig = go.Figure(go.Bar(
        x=classes,
        y=weights,
        marker_color=colors,
        text=[f"{w:.1f}%" for w in weights],
        textposition="outside"
    ))
    # Threshold line for equity
    fig.add_hline(
        y=max_equity_limit * 100,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text=f"Max Equity Cap ({max_equity_limit*100:.0f}%)",
        annotation_position="top right"
    )
    fig.update_layout(
        title="Asset Class Exposure vs Policy Limits",
        yaxis_title="Allocation (%)",
        yaxis=dict(range=[0, max(weights + [max_equity_limit*100]) + 15]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        margin=dict(t=40, b=20, l=20, r=20)
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
        text=[f"₹{x:,.2f} L" for x in df["Impact_Lakhs"]],
        textposition="outside"
    ))
    fig.update_layout(
        title="Simulated Stress P&L by Asset (in ₹ Lakhs)",
        yaxis_title="Impact (₹ Lakhs)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        margin=dict(t=40, b=20, l=20, r=20)
    )
    return fig

def plot_optimization_comparison(options_dict: dict, current_weights: dict):
    assets = list(current_weights.keys())
    curr_vals = [current_weights[a] * 100 for a in assets]
    opt_a_vals = [options_dict["option_a"]["weights"].get(a, 0.0) * 100 for a in assets]
    opt_b_vals = [options_dict["option_b"]["weights"].get(a, 0.0) * 100 for a in assets]
    opt_c_vals = [options_dict["option_c"]["weights"].get(a, 0.0) * 100 for a in assets]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Current", x=assets, y=curr_vals, marker_color="#94A3B8"))
    fig.add_trace(go.Bar(name="Option A (Conservative)", x=assets, y=opt_a_vals, marker_color="#64748B"))
    fig.add_trace(go.Bar(name="Option B (Least-Disruptive ⭐)", x=assets, y=opt_b_vals, marker_color="#10B981"))
    fig.add_trace(go.Bar(name="Option C (Return-Preserving)", x=assets, y=opt_c_vals, marker_color="#38BDF8"))

    fig.update_layout(
        barmode="group",
        title="Asset Allocation Shift Across Optimization Alternatives (%)",
        yaxis_title="Allocation (%)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E2E8F0"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=40, b=30, l=20, r=20)
    )
    return fig
