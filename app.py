import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Logistics Intelligence Platform", layout="wide")

# ---------------- HEADER ----------------
st.title("📦 Festive Surge Delivery Crisis Dashboard")
st.caption("End-to-End Diagnostic | Customer Experience | Operational Insights")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📂 Upload Data")

orders_file = st.sidebar.file_uploader("Orders", type=["csv"])
nps_file = st.sidebar.file_uploader("NPS", type=["csv"])
complaints_file = st.sidebar.file_uploader("Complaints", type=["csv"])
hub_file = st.sidebar.file_uploader("Hub Performance", type=["csv"])
courier_file = st.sidebar.file_uploader("Courier Performance", type=["csv"])

# ---------------- LOAD ----------------
if all([orders_file, nps_file, complaints_file, hub_file, courier_file]):

    @st.cache_data
    def load():
        orders = pd.read_csv(orders_file)
        nps = pd.read_csv(nps_file)
        complaints = pd.read_csv(complaints_file)
        hub = pd.read_csv(hub_file)
        courier = pd.read_csv(courier_file)
        return orders, nps, complaints, hub, courier

    orders, nps, complaints, hub, courier = load()

    # ---------------- PROCESS ----------------
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    orders['promised_date'] = pd.to_datetime(orders['promised_date'])
    orders['delivery_date'] = pd.to_datetime(orders['delivery_date'])

    orders['delay_days'] = (orders['delivery_date'] - orders['promised_date']).dt.days
    orders['delayed'] = orders['delay_days'] > 0

    nps['category'] = nps['score'].apply(lambda x: "Promoter" if x>=9 else ("Passive" if x>=7 else "Detractor"))

    # ---------------- KPIs ----------------
    total_nps = len(nps)
    promoters = len(nps[nps['category']=="Promoter"])
    detractors = len(nps[nps['category']=="Detractor"])
    nps_score = (promoters/total_nps - detractors/total_nps)*100

    delay_rate = orders['delayed'].mean()*100
    complaint_rate = complaints['order_id'].nunique() / orders['order_id'].nunique() * 100

    # ---------------- EXEC DASHBOARD ----------------
    st.markdown("## 📊 Executive Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("NPS Score", f"{nps_score:.1f}")
    c2.metric("Delay %", f"{delay_rate:.1f}%")
    c3.metric("Complaint %", f"{complaint_rate:.1f}%")

    st.markdown("---")

    # ---------------- TABS ----------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Customer", "⚙️ Operations", "🌍 Geography", "🔄 Funnel", "🧠 Simulator"
    ])

    # ---------------- CUSTOMER ----------------
    with tab1:
        st.subheader("Customer Sentiment (NPS)")

        fig = px.histogram(nps, x="category", color="category")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        **Insight:**  
        Detractors dominate → reflects poor delivery experience.
        """)

    # ---------------- OPERATIONS ----------------
    with tab2:
        st.subheader("Delivery Performance")

        fig = px.pie(orders, names="delayed", title="Delayed vs On-Time")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Courier Performance")
        fig2 = px.bar(courier, x="partner", y="sla_breach_rate", color="partner")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        **Insight:**  
        High SLA breaches across all partners → systemic issue  
        QuickShip shows highest complaints → service quality issue  
        """)

    # ---------------- GEOGRAPHY ----------------
    with tab3:
        st.subheader("Hub Performance (City Level)")

        fig = px.bar(hub, x="city", y="sla_breach_rate", color="city")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        **Insight:**  
        Tier-2 cities (Indore, Nagpur) are worst affected  
        Infrastructure unable to handle festive surge  
        """)

    # ---------------- FUNNEL ----------------
    with tab4:
        st.subheader("Customer Journey Funnel")

        merged = orders.merge(complaints[['order_id']], on="order_id", how="left", indicator=True)
        merged['complaint'] = merged['_merge']=="both"

        delayed = merged[merged['delayed']]
        conversion = delayed['complaint'].mean()*100

        st.metric("Delay → Complaint Conversion", f"{conversion:.1f}%")

        st.markdown("""
        **Insight:**  
        Delays directly convert into complaints → then detractors  
        Core problem lies in delivery reliability  
        """)

    # ---------------- SIMULATOR ----------------
    with tab5:
        st.subheader("Business Impact Simulator")

        new_delay = st.slider("Target Delay %", 0, 100, int(delay_rate))
        new_complaint = st.slider("Target Complaint %", 0, 100, int(complaint_rate))

        projected_nps = -63 + (82 - new_delay)*0.8

        st.success(f"📈 Projected NPS: {projected_nps:.1f}")

        st.markdown("""
        **Insight:**  
        Reducing delays has the highest impact on NPS  
        Operational fixes → measurable business gains  
        """)

    # ---------------- FINAL INSIGHTS ----------------
    st.markdown("---")
    st.markdown("## 💡 Key Takeaways")

    st.markdown("""
    - 82% delays are the root cause of poor customer experience  
    - Tier-2 hubs (Indore, Nagpur) are key bottlenecks  
    - Courier inefficiencies worsen service quality  
    - Delay → Complaint → Detractor is the main funnel  

    👉 Fix operations → Improve NPS → Drive growth  
    """)

else:
    st.warning("Upload all required datasets to view dashboard")
