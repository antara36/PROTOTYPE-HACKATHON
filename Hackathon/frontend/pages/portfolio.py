import streamlit as st
import pandas as pd
from backend.utils.calculations import format_currency_inr

def show_portfolio(system, state):
    st.title("💼 Portfolio Holdings & Capital Management")
    st.caption("Inspect and manage asset allocations, revaluation schedules, and liquidity ratings.")

    summary = state["portfolio_summary"]
    holdings = summary["holdings"]
    df = pd.DataFrame(holdings)

    # Format display table
    display_df = df.copy()
    display_df["Formatted_Amount"] = display_df["Amount_INR"].apply(format_currency_inr)
    display_df["Allocation_%"] = (display_df["Allocation_Pct"] * 100).round(1).astype(str) + "%"

    col_tbl, col_meta = st.columns([3, 2])
    with col_tbl:
        st.subheader("Current Holdings")
        st.dataframe(
            display_df[["Asset", "Asset_Class", "Formatted_Amount", "Allocation_%"]],
            use_container_width=True,
            hide_index=True
        )

    with col_meta:
        st.subheader("Holdings Overview")
        st.metric("Total Portfolio Capital", summary["formatted_capital"])
        st.metric("Active Asset Classes", len(summary["asset_class_breakdown"]))
        st.metric("Total Holdings Count", summary["num_assets"])

    st.markdown("---")
    st.subheader("✏️ Edit Holdings / Adjust Capital")
    
    with st.form("portfolio_edit_form"):
        st.write("Modify capital amounts (INR) per asset:")
        new_amounts = {}
        cols = st.columns(2)
        for i, row in df.iterrows():
            with cols[i % 2]:
                new_amounts[row["Asset"]] = st.number_input(
                    f"{row['Asset']} ({row['Asset_Class']})",
                    min_value=0.0,
                    value=float(row["Amount_INR"]),
                    step=100000.0,
                    format="%.0f"
                )

        btn_save = st.form_submit_button("💾 Update Holdings & Recompute Risk", use_container_width=True)
        if btn_save:
            updated_data = [{"Asset": k, "Amount_INR": v} for k, v in new_amounts.items()]
            new_port_df = pd.DataFrame(updated_data)
            system.portfolio_service.update_portfolio(new_port_df)
            st.success("Portfolio successfully updated! Recalculating controls...")
            st.rerun()

    st.markdown("---")
    # Quick reset button
    if st.button("🔄 Reset to Default Test Portfolio (₹1 Cr with 48% Equity Breach)"):
        default_data = [
            {"Asset": "NIFTY 50", "Amount_INR": 4800000.0},
            {"Asset": "Gold", "Amount_INR": 1500000.0},
            {"Asset": "Govt Bonds", "Amount_INR": 2200000.0},
            {"Asset": "Cash", "Amount_INR": 1500000.0},
        ]
        system.portfolio_service.update_portfolio(pd.DataFrame(default_data))
        st.success("Portfolio reset to default state.")
        st.rerun()
