import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Logistics Intelligence Platform", layout="wide")

# ------------------ THEME ------------------
st.markdown("""
<style>
.metric-card {padding: 15px; border-radius: 10px; background-color: #111827; color: white;}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.title("📦 Logistics Intelligence Platform")
st.caption("Advanced Analytics • Storytelling • Decision Intelligence")

# ------------------ SIDEBAR ------------------
st.sidebar.title("⚙️ Control Panel")
orders_file = st.sidebar.file_uploader("Orders", type=["csv"])
customers_file = st.sidebar.file_uploader("Customers", type=["csv"])
nps_file = st.sidebar.file_uploader("NPS", type=["csv"])
complaints_file = st.sidebar.file_uploader("Complaints", type=["csv"])
hub_file = st.sidebar.file_uploader("Hub Performance", type=["csv"])
courier_file = st.sidebar.file_uploader("Courier Performance", type=["csv"])

# ------------------ LOAD ------------------
if all([orders_file, customers_file, nps_file, complaints_file, hub_file, courier_file]):

    @st.cache_data
    def load_data():
        return (
            pd.read_csv(orders_file),
            pd.read_csv(customers_file),
            pd.read_csv(nps_file),
            pd.read_csv(complaints_file),
            pd.read_csv(hub_file),
            pd.read_csv(courier_file)
        )

    orders, customers, nps, complaints, hub, courier = load_data()

    # ------------------ PROCESS ------------------
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    orders['promised_date'] = pd.to_datetime(orders['promised_date'])
    orders['delivery_date'] = pd.to_datetime(orders['delivery_date'])
    orders['delay'] = (orders['delivery_date'] - orders['promised_date']).dt.days
    orders['sla_breach'] = orders['delay'] > 0

    nps['response_date'] = pd.to_datetime(nps['response_date'])
    nps['category'] = nps['score'].apply(lambda x: 'Promoter' if x>=9 else ('Passive' if x>=7 else 'Detractor'))

    # ------------------ KPI ------------------
    total_nps = len(nps)
    promoters = len(nps[nps['category']=='Promoter'])
    detractors = len(nps[nps['category']=='Detractor'])
    nps_score = (promoters/total_nps - detractors/total_nps)*100
    delay_rate = orders['sla_breach'].mean()
    complaint_rate = complaints['order_id'].nunique()/orders['order_id'].nunique()

    st.markdown("## 📊 Executive Dashboard")
    k1, k2, k3 = st.columns(3)
    k1.metric("NPS", f"{nps_score:.1f}")
    k2.metric("Delay %", f"{delay_rate*100:.1f}%")
    k3.metric("Complaint %", f"{complaint_rate*100:.1f}%")

    # ------------------ TABS ------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Customer", "Operations", "Funnel", "Simulator", "Reports"])

    # ------------------ CUSTOMER ------------------
    with tab1:
        st.subheader("Customer Experience")
        fig = px.histogram(nps, x="category", color="category")
        st.plotly_chart(fig, use_container_width=True)

        # NPS Trend
        nps_trend = nps.groupby(nps['response_date'].dt.to_period('M')).size()
        fig_trend = px.line(x=nps_trend.index.astype(str), y=nps_trend.values, title="NPS Responses Trend")
        st.plotly_chart(fig_trend, use_container_width=True)

    # ------------------ OPERATIONS ------------------
    with tab2:
        st.subheader("Operations Overview")
        colA, colB = st.columns(2)

        with colA:
            fig_delay = px.pie(orders, names='sla_breach', title="Delivery Performance")
            st.plotly_chart(fig_delay, use_container_width=True)

        with colB:
            fig_courier = px.bar(courier, x='courier_partner', y='sla_breach_rate', color='courier_partner')
            st.plotly_chart(fig_courier, use_container_width=True)

        hub['on_time_rate'] = hub['on_time_delivery']/hub['total_orders']
        fig_hub = px.bar(hub, x='city', y='on_time_rate', color='city')
        st.plotly_chart(fig_hub, use_container_width=True)

    # ------------------ FUNNEL ------------------
    with tab3:
        st.subheader("Funnel Breakdown")
        orders_with_complaints = orders.merge(complaints[['order_id']], on='order_id', how='left', indicator=True)
        orders_with_complaints['has_complaint'] = orders_with_complaints['_merge'] == 'both'

        delayed_orders = orders_with_complaints[orders_with_complaints['sla_breach']]
        delay_to_complaint = delayed_orders['has_complaint'].mean()

        st.metric("Delay → Complaint %", f"{delay_to_complaint*100:.1f}%")

    # ------------------ SIMULATOR ------------------
    with tab4:
        st.subheader("Business Impact Simulator")
        new_delay = st.slider("Target Delay %", 0, 100, 45)
        new_complaint = st.slider("Target Complaint %", 0, 100, 10)

        projected_nps = -63 + (82-new_delay)*0.8
        st.success(f"Projected NPS: {projected_nps:.1f}")

    # ------------------ REPORTS ------------------
    with tab5:
        st.subheader("Download Reports")

        report = pd.DataFrame({
            'Metric': ['NPS', 'Delay %', 'Complaint %'],
            'Value': [nps_score, delay_rate*100, complaint_rate*100]
        })

        csv = report.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download KPI Report", csv, "kpi_report.csv", "text/csv")

    # ------------------ FOOTER ------------------
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    st.warning("Upload all 6 datasets to unlock full platform")
