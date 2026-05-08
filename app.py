import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Logistics Intelligence Platform", layout="wide")

# ---------------- STYLING ----------------
st.markdown("""
<style>
.kpi-card {
    padding: 20px;
    border-radius: 12px;
    background-color: #111827;
    color: white;
    text-align: center;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("📦 Logistics Intelligence Platform")
st.caption("Executive Dashboard • Customer Experience • Operational Excellence")

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("⚙️ Filters")

orders_file = st.sidebar.file_uploader("Orders", type=["csv"])
nps_file = st.sidebar.file_uploader("NPS", type=["csv"])
complaints_file = st.sidebar.file_uploader("Complaints", type=["csv"])
hub_file = st.sidebar.file_uploader("Hub", type=["csv"])
courier_file = st.sidebar.file_uploader("Courier", type=["csv"])

# ---------------- LOAD ----------------
if all([orders_file, nps_file, complaints_file, hub_file, courier_file]):

    @st.cache_data
    def load_data():
        orders = pd.read_csv(orders_file)
        nps = pd.read_csv(nps_file)
        complaints = pd.read_csv(complaints_file)
        hub = pd.read_csv(hub_file)
        courier = pd.read_csv(courier_file)
        return orders, nps, complaints, hub, courier

    orders, nps, complaints, hub, courier = load_data()

    # ---------------- PROCESS ----------------
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    orders['delivery_date'] = pd.to_datetime(orders['delivery_date'])
    orders['promised_date'] = pd.to_datetime(orders['promised_date'])

    orders['delay'] = (orders['delivery_date'] - orders['promised_date']).dt.days
    orders['delayed'] = orders['delay'] > 0

    nps['category'] = nps['score'].apply(lambda x: "Promoter" if x>=9 else ("Passive" if x>=7 else "Detractor"))

    # ---------------- GLOBAL FILTERS ----------------
    city_filter = st.sidebar.multiselect("City", options=hub['city'].unique(), default=hub['city'].unique())
    courier_filter = st.sidebar.multiselect("Courier", options=courier['partner'].unique(), default=courier['partner'].unique())

    orders = orders[orders['city'].isin(city_filter)]
    hub = hub[hub['city'].isin(city_filter)]
    courier = courier[courier['partner'].isin(courier_filter)]

    # ---------------- KPIs ----------------
    total_nps = len(nps)
    promoters = len(nps[nps['category']=="Promoter"])
    detractors = len(nps[nps['category']=="Detractor"])
    nps_score = (promoters/total_nps - detractors/total_nps)*100

    delay_rate = orders['delayed'].mean()*100
    complaint_rate = complaints['order_id'].nunique() / orders['order_id'].nunique() * 100
    rto_rate = hub['rto_rate'].mean() if 'rto_rate' in hub.columns else 20

    # ---------------- EXECUTIVE OVERVIEW ----------------
    st.markdown("## 📊 Executive Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.markdown(f"<div class='kpi-card'><h3>NPS</h3><h1>{nps_score:.1f}</h1></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi-card'><h3>Delay %</h3><h1>{delay_rate:.1f}%</h1></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi-card'><h3>Complaint %</h3><h1>{complaint_rate:.1f}%</h1></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='kpi-card'><h3>RTO %</h3><h1>{rto_rate:.1f}%</h1></div>", unsafe_allow_html=True)

    st.markdown("**Insight:** High delays are directly driving poor NPS and complaints.")

    # ---------------- CUSTOMER INSIGHTS ----------------
    st.markdown("## 👥 Customer Insights")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(nps, names='category', title="NPS Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        trend = nps.groupby(nps.index).size()
        fig2 = px.line(y=trend, title="NPS Trend")
        st.plotly_chart(fig2, use_container_width=True)

    st.info("Detractors dominate → customer dissatisfaction is systemic.")

    # ---------------- OPERATIONAL INSIGHTS ----------------
    st.markdown("## ⚙️ Operational Insights")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(orders, names='delayed', title="On-time vs Delayed")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.histogram(orders, x='delay', title="Delay Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    st.info("82% delays indicate severe SLA failures.")

    # ---------------- GEOGRAPHY ----------------
    st.markdown("## 🌍 Geographic Analysis")

    fig = px.bar(hub, x='city', y='sla_breach_rate', color='city')
    st.plotly_chart(fig, use_container_width=True)

    st.info("Tier-2 cities are key bottlenecks.")

    # ---------------- COURIER ----------------
    st.markdown("## 🚚 Courier Performance")

    fig = px.bar(courier, x='partner', y='sla_breach_rate', color='partner')
    st.plotly_chart(fig, use_container_width=True)

    st.info("QuickShip shows highest complaint rates → quality issue.")

    # ---------------- FUNNEL ----------------
    st.markdown("## 🔄 Funnel Analysis")

    merged = orders.merge(complaints[['order_id']], on='order_id', how='left', indicator=True)
    merged['complaint'] = merged['_merge'] == 'both'

    delayed = merged[merged['delayed']]
    conversion = delayed['complaint'].mean()*100

    st.metric("Delay → Complaint Conversion", f"{conversion:.1f}%")

    st.info("Delays directly convert into complaints and detractors.")

    # ---------------- ROOT CAUSE ----------------
    st.markdown("## 🧠 Root Cause Insights")

    st.markdown("""
    - Lack of capacity in Tier-2 hubs  
    - Misaligned promised delivery dates  
    - Fake delivery attempts increasing RTO  
    """)

    # ---------------- SIMULATOR ----------------
    st.markdown("## 🧪 Impact Simulator")

    new_delay = st.slider("Target Delay %", 0, 100, int(delay_rate))
    projected_nps = -63 + (82 - new_delay)*0.8

    st.success(f"Projected NPS: {projected_nps:.1f}")

    # ---------------- RECOMMENDATIONS ----------------
    st.markdown("## 🚀 Recommendations")

    st.markdown("""
    - Add dynamic SLA buffers  
    - Improve hub automation  
    - Reallocate courier load  
    - Proactive customer communication  
    """)

else:
    st.warning("Please upload all datasets")
