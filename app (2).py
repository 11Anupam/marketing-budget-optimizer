import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pickle

# --- Page Config ---
st.set_page_config(page_title="Marketing Mix Model", page_icon="🎯", layout="wide")

# --- Load ---
with open("mmm_model.pkl", "rb") as f:
    model = pickle.load(f)

df          = pd.read_csv("mmm_data.csv")
channel_roi = pd.read_csv("channel_roi.csv")

spend_cols = ["Social_Spend", "Search_Spend", "Influencer_Spend", "Media_Spend"]

channel_labels = {
    "Social_Spend":     "📱 Social Media",
    "Search_Spend":     "🔍 Google Search",
    "Influencer_Spend": "🎯 Influencer",
    "Media_Spend":      "📺 Media / Banner"
}

colors = {
    "Social_Spend":     "#9b59b6",
    "Search_Spend":     "#3498db",
    "Influencer_Spend": "#2ecc71",
    "Media_Spend":      "#e74c3c"
}

roi_insights = {
    "Social_Spend":     "⚠️ Low ROI — ₹1 spent returns only ₹0.31. Consider reducing budget and reallocating.",
    "Search_Spend":     "✅ Moderate ROI — ₹1 spent returns ₹1.13. Maintain current spend.",
    "Influencer_Spend": "🏆 High ROI — ₹1 spent returns ₹2.37. Scale this channel aggressively.",
    "Media_Spend":      "💛 Strong ROI — ₹1 spent returns ₹2.77. Best performing channel per rupee."
}

# --- Header ---
st.title("🎯 Marketing Mix Model Dashboard")
st.markdown("#### Channel ROI Analysis + Budget Optimizer | Anupam Gajbhiye · SIIB MBA-IB")
st.markdown("---")

# --- Model Score Banner ---
st.markdown(
    """
    <div style='background:#2ecc7122; border-left:5px solid #2ecc71;
    padding:14px 20px; border-radius:0 10px 10px 0; margin-bottom:20px;'>
    <h4 style='color:#2ecc71; margin:0 0 4px 0'>✅ Model Performance</h4>
    <p style='margin:0; font-size:15px'>
    R² Score: <b>0.923</b> — the model explains <b>92.3%</b> of revenue variance across all channels.
    This is a strong, reliable model for budget decisions.
    </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ============================================================
# SECTION 1 — Key Insight Cards
# ============================================================
st.markdown("### 💡 Channel ROI at a Glance")

c1, c2, c3, c4 = st.columns(4)
roi_map = dict(zip(channel_roi["Channel"], channel_roi["ROI_per_₹1"]))
pct_map = dict(zip(channel_roi["Channel"], channel_roi["ROI_%"]))

metrics = [
    ("📱 Social Media",  "Social_Spend",     "₹0.31 per ₹1", "-69% loss",   "inverse"),
    ("🔍 Google Search", "Search_Spend",     "₹1.13 per ₹1", "+13% gain",   "normal"),
    ("🎯 Influencer",    "Influencer_Spend", "₹2.37 per ₹1", "+137% gain",  "normal"),
    ("📺 Media/Banner",  "Media_Spend",      "₹2.77 per ₹1", "+177% gain",  "normal"),
]

for col, (label, ch, val, delta, delta_color) in zip([c1, c2, c3, c4], metrics):
    col.metric(label, val, delta)

st.markdown("---")

# ============================================================
# SECTION 2 — Budget Optimizer
# ============================================================
st.markdown("### 💰 Budget Optimizer")
st.markdown("Enter your total marketing budget — get the optimal spend per channel instantly")

total_budget = st.number_input(
    "Enter Total Marketing Budget (₹)",
    min_value=100000,
    max_value=500000000,
    value=10000000,
    step=500000,
    format="%d"
)

# Optimize using positive coefficients only
coefs   = model.coef_.copy()
coefs   = np.maximum(coefs, 0)
weights = coefs / coefs.sum()

allocation = {
    ch: round(w * total_budget, 0)
    for ch, w in zip(spend_cols, weights)
}

# Predicted revenue
predicted_revenue = float(model.predict([list(allocation.values())])[0])
predicted_revenue = max(predicted_revenue, 0)
overall_roi       = ((predicted_revenue - total_budget) / total_budget * 100)

# Summary metrics
st.markdown("#### 📊 Projected Outcome")
m1, m2, m3 = st.columns(3)
m1.metric("💰 Total Budget",       f"₹{total_budget:,.0f}")
m2.metric("📈 Predicted Revenue",  f"₹{predicted_revenue:,.0f}")
m3.metric("🎯 Expected ROI",       f"{overall_roi:.1f}%",
          delta="profit" if overall_roi > 0 else "loss")

st.markdown("---")

# Allocation cards
st.markdown("#### 📋 Recommended Spend per Channel")
cols = st.columns(4)
for col, (ch, amt) in zip(cols, allocation.items()):
    pct = (amt / total_budget * 100)
    col.metric(
        channel_labels[ch],
        f"₹{amt:,.0f}",
        f"{pct:.1f}% of budget"
    )

# Allocation bar chart
alloc_df = pd.DataFrame({
    "Channel": [channel_labels[ch] for ch in allocation],
    "Amount":  list(allocation.values()),
    "Color":   [colors[ch] for ch in allocation]
})

fig1 = px.bar(
    alloc_df,
    x="Channel",
    y="Amount",
    color="Channel",
    color_discrete_sequence=alloc_df["Color"].tolist(),
    text=alloc_df["Amount"].apply(lambda x: f"₹{x:,.0f}"),
    title=f"💰 Optimal Budget Allocation — ₹{total_budget:,.0f} Total"
)
fig1.update_traces(textposition="outside")
fig1.update_layout(
    height=420,
    showlegend=False,
    yaxis_title="Spend (₹)",
    margin=dict(t=60, b=20)
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 3 — Channel ROI Analysis
# ============================================================
st.markdown("### 📊 Channel ROI Analysis")

col_left, col_right = st.columns(2)

with col_left:
    roi_sorted = channel_roi.sort_values("ROI_%", ascending=True).copy()
    roi_sorted["Label"] = roi_sorted["Channel"].map(channel_labels)

    fig2 = px.bar(
        roi_sorted,
        x="ROI_%",
        y="Label",
        orientation="h",
        color="ROI_%",
        color_continuous_scale="RdYlGn",
        text=roi_sorted["ROI_%"].apply(lambda x: f"{x}%"),
        title="Revenue Contribution by Channel"
    )
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        height=380,
        showlegend=False,
        xaxis_title="Revenue Contribution (%)",
        yaxis_title="",
        margin=dict(t=60, b=20),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    roi_pie = channel_roi.copy()
    roi_pie["Label"] = roi_pie["Channel"].map(channel_labels)

    fig3 = px.pie(
        roi_pie,
        values="ROI_%",
        names="Label",
        hole=0.5,
        color="Channel",
        color_discrete_map=colors,
        title="Revenue Share by Channel"
    )
    fig3.update_traces(textinfo="label+percent", textposition="outside")
    fig3.update_layout(height=380, margin=dict(t=60, b=20), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 4 — Channel Deep Dive
# ============================================================
st.markdown("### 🔍 Channel Deep Dive")

channel_select = st.selectbox(
    "Select a channel to analyze",
    options=spend_cols,
    format_func=lambda x: channel_labels[x]
)

# Insight banner per channel
c = colors[channel_select]
st.markdown(
    f"""<div style='background:{c}22; border-left:5px solid {c};
    padding:12px 20px; border-radius:0 10px 10px 0; margin-bottom:16px;'>
    <p style='margin:0; font-size:15px'>{roi_insights[channel_select]}</p>
    </div>""",
    unsafe_allow_html=True
)

fig4 = px.scatter(
    df,
    x=channel_select,
    y="Revenue",
    trendline="ols",
    color_discrete_sequence=[colors[channel_select]],
    labels={
        channel_select: f"{channel_labels[channel_select]} Spend (₹)",
        "Revenue": "Revenue (₹)"
    },
    title=f"Spend vs Revenue — {channel_labels[channel_select]}"
)
fig4.update_layout(height=420, margin=dict(t=60, b=20))
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 5 — Revenue Trend
# ============================================================
st.markdown("### 📈 Revenue Trend Over Time")

df["c_date"] = pd.to_datetime(df["c_date"])
df_sorted    = df.sort_values("c_date")

fig5 = px.line(
    df_sorted,
    x="c_date",
    y="Revenue",
    title="Total Revenue Over Time",
    color_discrete_sequence=["#2ecc71"]
)
fig5.update_traces(line_width=2.5)
fig5.update_layout(
    height=400,
    xaxis_title="Date",
    yaxis_title="Revenue (₹)",
    margin=dict(t=60, b=20)
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")
st.caption("Built with Python · scikit-learn · Streamlit · Plotly | Anupam Gajbhiye · SIIB MBA-IB")
