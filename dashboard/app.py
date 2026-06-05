import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ── CONFIG ────────────────────────────────────
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Healthcare Claims Analytics",
    page_icon="🏥",
    layout="wide"
)

# ── HELPER ────────────────────────────────────
def fetch(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        return r.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# ── HEADER ────────────────────────────────────
st.title("🏥 Healthcare Claims Analytics Dashboard")
st.markdown("**Medicare Claims Anomaly Detection & Billing Analysis**")
st.markdown("---")

# ── SUMMARY CARDS ─────────────────────────────
summary = fetch("/analytics/summary")

if summary:
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Claims",
        f"{summary['total_claims']:,}"
    )
    col2.metric(
        "Anomalies Detected",
        f"{summary['total_anomalies']:,}",
        delta="Flagged ⚠️"
    )
    col3.metric(
        "Avg Submitted Charge",
        f"${summary['avg_submitted_charge']:,.2f}"
    )
    col4.metric(
        "Medicare Payment Gap",
        f"${summary['payment_gap']:,.2f}",
        delta="per claim",
        delta_color="inverse"
    )

st.markdown("---")

# ── ROW 1: TOP CHARGING PROVIDERS + ANOMALIES ─
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💰 Top Charging Provider Types")
    data = fetch("/analytics/top-charging-providers?limit=10")
    if data:
        df = pd.DataFrame(data['data'])
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = sns.color_palette("Reds_r", len(df))
        bars = ax.barh(df['provider_type'], df['avg_charge'], color=colors)
        ax.set_xlabel("Avg Submitted Charge ($)")
        ax.invert_yaxis()
        for bar, val in zip(bars, df['avg_charge']):
            ax.text(bar.get_width() + 20,
                    bar.get_y() + bar.get_height()/2,
                    f"${val:,.0f}", va='center', fontsize=8)
        plt.tight_layout()
        st.pyplot(fig)

with col_right:
    st.subheader("🚨 Top Billing Anomalies")
    data = fetch("/analytics/anomalies?limit=10&min_ratio=3")
    if data and data['data']:
        df_anom = pd.DataFrame(data['data'])
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        colors2 = sns.color_palette("OrRd", len(df_anom))
        ax2.barh(
            df_anom['provider_name'] + " (" + df_anom['state'] + ")",
            df_anom['charge_ratio'],
            color=colors2
        )
        ax2.set_xlabel("Charge Ratio (vs Specialty Average)")
        ax2.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig2)

st.markdown("---")

# ── ROW 2: STATE BREAKDOWN ─────────────────────
st.subheader("🗺️ State-Level Billing Analysis")
state_data = fetch("/analytics/state-breakdown")
if state_data:
    df_state = pd.DataFrame(state_data['data'])
    df_state = df_state[~df_state['state'].isin(['ZZ', 'AE', 'AS'])]

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        sns.barplot(
            data=df_state.head(12),
            x='state', y='avg_charge',
            palette='Blues_r', ax=ax3
        )
        ax3.set_title("Avg Submitted Charge by State")
        ax3.set_xlabel("State")
        ax3.set_ylabel("Avg Charge ($)")
        plt.tight_layout()
        st.pyplot(fig3)

    with col_s2:
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        df_state_top = df_state.head(10)
        x = range(len(df_state_top))
        w = 0.35
        ax4.bar([i - w/2 for i in x], df_state_top['avg_charge'],
                w, label='Avg Charge', color='#e74c3c', alpha=0.8)
        ax4.bar([i + w/2 for i in x], df_state_top['avg_payment'],
                w, label='Avg Medicare Paid', color='#2ecc71', alpha=0.8)
        ax4.set_xticks(x)
        ax4.set_xticklabels(df_state_top['state'])
        ax4.set_title("Charged vs Medicare Paid by State")
        ax4.legend()
        plt.tight_layout()
        st.pyplot(fig4)

st.markdown("---")

# ── ROW 3: CLAIMS EXPLORER ─────────────────────
st.subheader("🔍 Claims Explorer")

col_f1, col_f2 = st.columns(2)

with col_f1:
    states_data = fetch("/claims/states")
    state_options = ["All"] + (states_data['states'] if states_data else [])
    selected_state = st.selectbox("Filter by State", state_options)

with col_f2:
    types_data = fetch("/claims/provider-types")
    type_options = ["All"] + (types_data['provider_types'] if types_data else [])
    selected_type = st.selectbox("Filter by Provider Type", type_options)

# Build query
params = "?limit=50"
if selected_state != "All":
    params += f"&state={selected_state}"
if selected_type != "All":
    params += f"&provider_type={selected_type}"

claims_data = fetch(f"/claims{params}")
if claims_data and claims_data['data']:
    df_claims = pd.DataFrame(claims_data['data'])
    st.dataframe(
        df_claims[[
            'name', 'provider_type', 'state',
            'avg_submitted_charge', 'avg_medicare_payment', 'total_services'
        ]].rename(columns={
            'name'                  : 'Provider',
            'provider_type'         : 'Specialty',
            'state'                 : 'State',
            'avg_submitted_charge'  : 'Avg Charge ($)',
            'avg_medicare_payment'  : 'Medicare Paid ($)',
            'total_services'        : 'Total Services'
        }),
        use_container_width=True
    )
    st.caption(f"Showing {len(df_claims)} of {claims_data['total']:,} total records")

# ── FOOTER ────────────────────────────────────
st.markdown("---")
st.markdown(
    "Built by **Bhanu Mudireddy** | "
    "Technical BA | "
    "[GitHub](https://github.com/bhanusravani267) | "
    "[LinkedIn](https://linkedin.com/in/bhanu-mudireddy)"
)