import os
import streamlit as st
import pandas as pd
import numpy as np

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from src.ingestion.ingest import DataIngestionEngine
from src.cleaning.clean import DataCleaningPipeline
from src.features.engineer import FeatureEngineeringPipeline
from src.database.connection import create_db_engine
from src.database.loader import StarSchemaETLLoader
from src.analytics.query_engine import SQLAnalyticsEngine
from src.analytics.alert_engine import BusinessAlertEngine
from src.analytics.forecast import SalesForecastingEngine
from src.analytics.rfm import RFMSegmentationEngine
from src.ai.insight_engine import GeminiAIInsightEngine

st.set_page_config(
    page_title="AI-Powered BI & Sales Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Glassmorphism CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0F172A 0%, #090D16 90%);
        color: #F8FAFC;
    }

    /* Glassmorphism Metric Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.55);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.3);
    }
    
    .metric-title {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94A3B8;
        margin-bottom: 8px;
    }

    .metric-number {
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    .metric-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 12px;
        margin-top: 8px;
    }

    .badge-cyan { background: rgba(56, 189, 248, 0.15); color: #38BDF8; }
    .badge-green { background: rgba(16, 185, 129, 0.15); color: #10B981; }
    .badge-amber { background: rgba(245, 158, 11, 0.15); color: #F59E0B; }
    .badge-purple { background: rgba(139, 92, 246, 0.15); color: #C084FC; }
    .badge-pink { background: rgba(236, 72, 153, 0.15); color: #F472B6; }

    /* Alert Boxes */
    .alert-card-high {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 5px solid #EF4444;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .alert-card-med {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-left: 5px solid #F59E0B;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }

    /* AI Insight Container */
    .ai-container {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 28px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
    }

    /* Streamlit Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 14px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* Custom Header Styling */
    .main-header {
        background: linear-gradient(90deg, #F8FAFC 0%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 36px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_analytics_engines():
    engine = create_db_engine()
    sql_engine = SQLAnalyticsEngine(engine=engine)
    alert_engine = BusinessAlertEngine()
    forecast_engine = SalesForecastingEngine(engine=engine)
    rfm_engine = RFMSegmentationEngine(engine=engine)
    ai_engine = GeminiAIInsightEngine()
    return engine, sql_engine, alert_engine, forecast_engine, rfm_engine, ai_engine

db_engine, sql_engine, alert_engine, forecast_engine, rfm_engine, ai_engine = init_analytics_engines()

# SIDEBAR NAVIGATION & CONTROLS
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/combo-chart.png", width=64)
    st.markdown("<h2 style='margin-top:-10px;'>Analytics Studio</h2>", unsafe_allow_html=True)
    st.markdown("<span style='color:#64748B; font-size:12px;'>AI-POWERED BUSINESS INTELLIGENCE</span>", unsafe_allow_html=True)
    st.markdown("---")

    # Data Upload Control
    st.subheader("📤 Data Upload Engine")
    uploaded_file = st.file_uploader("Drop Sales CSV / Excel File", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None:
        with st.spinner("Executing ETL Pipeline..."):
            try:
                temp_path = f"data/raw/temp_{uploaded_file.name}"
                os.makedirs("data/raw", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                ingestor = DataIngestionEngine()
                df_raw, _ = ingestor.ingest(temp_path)
                cleaner = DataCleaningPipeline()
                df_clean, _ = cleaner.clean(df_raw)
                fe = FeatureEngineeringPipeline()
                df_featured = fe.add_features(df_clean)
                loader = StarSchemaETLLoader(engine=db_engine)
                loader.load_star_schema(df_featured)

                st.success(f"[OK] Ingested {len(df_featured):,} transactions!")
            except Exception as e:
                st.error(f"ETL Pipeline Error: {e}")

    st.markdown("---")
    st.subheader("⚙️ Interactive Filters")
    
    # Fetch Base Metrics for Filters
    try:
        raw_regional = sql_engine.get_regional_analytics()
        raw_products = sql_engine.get_product_performance()
        
        region_list = ["All Regions"] + sorted(list(raw_regional["region"].unique())) if not raw_regional.empty else ["All Regions"]
        selected_region = st.selectbox("Filter Region", region_list)

        category_list = ["All Categories"] + sorted(list(raw_products["category"].unique())) if not raw_products.empty else ["All Categories"]
        selected_category = st.selectbox("Filter Category", category_list)

    except Exception:
        selected_region = "All Regions"
        selected_category = "All Categories"

    st.markdown("---")
    st.subheader("🤖 AI Settings")
    gemini_key_input = st.text_input("Google Gemini API Key", type="password", help="Enter key for live Gemini AI generation")
    if gemini_key_input:
        ai_engine = GeminiAIInsightEngine(api_key=gemini_key_input)

# Fetch Current Metrics
try:
    kpi_dict = sql_engine.get_kpi_summary()
    regional_df = sql_engine.get_regional_analytics()
    product_df = sql_engine.get_product_performance()
    mom_df = sql_engine.get_mom_growth()

    # Apply Sidebar Filters
    if selected_region != "All Regions" and not regional_df.empty:
        regional_df = regional_df[regional_df["region"] == selected_region]

    if selected_category != "All Categories" and not product_df.empty:
        product_df = product_df[product_df["category"] == selected_category]

    alerts_list = alert_engine.evaluate_alerts(kpi_dict, regional_df, product_df, mom_df)
except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

# MAIN DASHBOARD TITLE HEADER
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown('<div class="main-header">BI & Sales Analytics Platform</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:#94A3B8; font-size:15px; margin-top:-5px;'>Enterprise Sales Performance, Star-Schema SQL Metrics & Google Gemini AI Insights</p>", unsafe_allow_html=True)

with top_col2:
    st.markdown("<div style='text-align:right; margin-top:10px;'><span style='background:rgba(16,185,129,0.15); color:#10B981; border:1px solid rgba(16,185,129,0.3); padding:8px 16px; border-radius:20px; font-weight:700; font-size:13px;'>🟢 SYSTEM ONLINE</span></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# TOP EXECUTIVE METRIC CARDS (GLASSMORPHISM)
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-title">Total Revenue</div>
        <div class="metric-number" style="color: #38BDF8;">${kpi_dict.get('total_revenue', 0):,.2f}</div>
        <div class="metric-badge badge-cyan">⚡ Gross Volume</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-title">Net Profit</div>
        <div class="metric-number" style="color: #10B981;">${kpi_dict.get('total_profit', 0):,.2f}</div>
        <div class="metric-badge badge-green">▲ Net Earnings</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-title">Profit Margin</div>
        <div class="metric-number" style="color: #F59E0B;">{kpi_dict.get('profit_margin_pct', 0):.2f}%</div>
        <div class="metric-badge badge-amber">★ Margin Yield</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-title">Total Orders</div>
        <div class="metric-number" style="color: #C084FC;">{kpi_dict.get('total_orders', 0):,.0f}</div>
        <div class="metric-badge badge-purple">📦 Transaction Volume</div>
    </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="glass-card">
        <div class="metric-title">Avg Order Line Value</div>
        <div class="metric-number" style="color: #F472B6;">${kpi_dict.get('avg_order_line_value', 0):,.2f}</div>
        <div class="metric-badge badge-pink">🏷️ Line Basket Size</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# NAVIGATION TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Executive Overview",
    "📦 Product & Regional",
    "⚠️ Risk Alerts",
    "🤖 Gemini AI Engine",
    "🔮 Forecasting & RFM"
])

# TAB 1: EXECUTIVE OVERVIEW
with tab1:
    st.markdown("### 📊 Monthly Sales & Profit Performance Trend")
    if not mom_df.empty:
        if HAS_PLOTLY:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=mom_df["year_month"], y=mom_df["revenue"],
                mode="lines+markers", name="Revenue ($)",
                line=dict(color="#38BDF8", width=3.5, shape="spline"),
                fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.08)"
            ))
            fig_trend.add_trace(go.Scatter(
                x=mom_df["year_month"], y=mom_df["profit"],
                mode="lines+markers", name="Net Profit ($)",
                line=dict(color="#10B981", width=3.5, shape="spline"),
                fill="tozeroy", fillcolor="rgba(16, 185, 129, 0.08)"
            ))
            fig_trend.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=420,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_trend, width='stretch')
        else:
            st.line_chart(mom_df.set_index("year_month")[["revenue", "profit"]])

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("### 🌍 Revenue by Region")
        if not regional_df.empty:
            reg_agg = regional_df.groupby("region")["total_revenue"].sum().reset_index()
            if HAS_PLOTLY:
                fig_reg = px.bar(
                    reg_agg, x="region", y="total_revenue", color="region",
                    color_discrete_sequence=["#38BDF8", "#8B5CF6", "#10B981", "#F59E0B"],
                    text_auto=".2s"
                )
                fig_reg.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=360,
                    showlegend=False
                )
                st.plotly_chart(fig_reg, width='stretch')
            else:
                st.bar_chart(reg_agg.set_index("region")["total_revenue"])

    with row1_col2:
        st.markdown("### 🍩 Category Revenue Contribution")
        if not product_df.empty:
            cat_agg = product_df.groupby("category")["total_revenue"].sum().reset_index()
            if HAS_PLOTLY:
                fig_pie = px.pie(
                    cat_agg, values="total_revenue", names="category", hole=0.55,
                    color_discrete_sequence=["#38BDF8", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"]
                )
                fig_pie.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=360
                )
                st.plotly_chart(fig_pie, width='stretch')
            else:
                st.bar_chart(cat_agg.set_index("category")["total_revenue"])

# TAB 2: PRODUCT & REGIONAL ANALYTICS
with tab2:
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("### 🏆 Top 10 Revenue Products")
        if not product_df.empty:
            st.dataframe(
                product_df.head(10)[["product_name", "category", "total_units_sold", "total_revenue", "total_profit", "profit_margin_pct"]],
                width='stretch'
            )

    with p_col2:
        st.markdown("### 🎯 Revenue vs. Margin Matrix")
        if not product_df.empty:
            if HAS_PLOTLY:
                fig_scatter = px.scatter(
                    product_df, x="total_revenue", y="profit_margin_pct",
                    size="total_units_sold", color="category", hover_name="product_name",
                    color_discrete_sequence=["#38BDF8", "#10B981", "#F59E0B", "#EC4899", "#8B5CF6"]
                )
                fig_scatter.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=380
                )
                st.plotly_chart(fig_scatter, width='stretch')
            else:
                st.dataframe(product_df[["product_name", "category", "total_revenue", "profit_margin_pct"]], width='stretch')

    st.markdown("### 🗺️ State Performance Breakdown")
    if not regional_df.empty:
        st.dataframe(regional_df, width='stretch')

# TAB 3: RISK ALERTS
with tab3:
    st.markdown("### 🚨 Active Business Alerts & Operational Risks")
    if len(alerts_list) == 0:
        st.success("[OK] All operational metrics are operating within healthy target thresholds!")
    else:
        for alert in alerts_list:
            card_style = "alert-card-high" if alert["severity"] == "HIGH" else "alert-card-med"
            badge = "🔴 HIGH SEVERITY" if alert["severity"] == "HIGH" else "🟡 MEDIUM WARNING"
            st.markdown(f"""
            <div class="{card_style}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong style="font-size:16px; color:#F8FAFC;">{alert['title']}</strong>
                    <span style="font-size:11px; font-weight:700; padding:4px 10px; border-radius:12px; background:rgba(255,255,255,0.1);">{badge}</span>
                </div>
                <p style="margin-top:8px; color:#CBD5E1; font-size:14px;">{alert['description']}</p>
                <div style="font-size:12px; color:#94A3B8; margin-top:6px;"><strong>Evidence:</strong> {alert['evidence']}</div>
            </div>
            """, unsafe_allow_html=True)

# TAB 4: GEMINI AI ENGINE
with tab4:
    st.markdown("### 🤖 Google Gemini AI Business Insight Engine")
    st.markdown("<p style='color:#94A3B8;'>Generates natural-language executive insights, metric evidence, and strategic recommendations from your Star Schema database.</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✨ Generate Executive AI Report", type="primary"):
        with st.spinner("Connecting to Google Gemini API & analyzing metrics..."):
            insight_text = ai_engine.generate_insights(kpi_dict, regional_df, product_df, mom_df, alerts_list)
            st.markdown("""
            <div class="ai-container">
            """, unsafe_allow_html=True)
            st.markdown(insight_text)
            st.markdown("</div>", unsafe_allow_html=True)

# TAB 5: FORECASTING & RFM
with tab5:
    st.markdown("### 🔮 3-Month Sales Revenue Forecast")
    fc_res = forecast_engine.generate_monthly_forecast(forecast_months=3)

    if fc_res["status"] == "success":
        hist_df = pd.DataFrame(fc_res["historical"])
        fc_df = pd.DataFrame(fc_res["forecast"])

        if HAS_PLOTLY:
            fig_fc = go.Figure()
            fig_fc.add_trace(go.Scatter(
                x=hist_df["year_month"], y=hist_df["actual_revenue"],
                mode="lines+markers", name="Actual Revenue",
                line=dict(color="#38BDF8", width=3.5)
            ))
            fig_fc.add_trace(go.Scatter(
                x=fc_df["year_month"], y=fc_df["forecast_revenue"],
                mode="lines+markers", name="Forecast Projected",
                line=dict(color="#F59E0B", width=3.5, dash="dash")
            ))
            fig_fc.add_trace(go.Scatter(
                x=fc_df["year_month"], y=fc_df["upper_bound"],
                mode="lines", name="Upper Bound (+95%)",
                line=dict(color="#10B981", width=1.5, dash="dot")
            ))
            fig_fc.add_trace(go.Scatter(
                x=fc_df["year_month"], y=fc_df["lower_bound"],
                mode="lines", name="Lower Bound (-95%)",
                line=dict(color="#EF4444", width=1.5, dash="dot")
            ))
            fig_fc.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=400
            )
            st.plotly_chart(fig_fc, width='stretch')
        else:
            st.dataframe(fc_df, width='stretch')

    st.markdown("---")
    st.markdown("### 👥 Customer RFM (Recency, Frequency, Monetary) Segmentation")
    rfm_res = rfm_engine.compute_rfm_segmentation()

    if rfm_res["status"] == "success":
        rfm_c1, rfm_c2 = st.columns(2)
        rfm_seg_df = pd.DataFrame(rfm_res["segment_summary"])

        with rfm_c1:
            st.markdown("#### Segment Customer Distribution")
            if HAS_PLOTLY:
                fig_rfm = px.pie(
                    rfm_seg_df, values="customer_count", names="segment", hole=0.5,
                    color_discrete_sequence=["#10B981", "#38BDF8", "#F59E0B", "#EF4444", "#8B5CF6"]
                )
                fig_rfm.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=350)
                st.plotly_chart(fig_rfm, width='stretch')
            else:
                st.dataframe(rfm_seg_df, width='stretch')

        with rfm_c2:
            st.markdown("#### Segment Revenue & Metric Breakdown")
            st.dataframe(rfm_seg_df, width='stretch')

        st.markdown("#### 🏆 Top Champion Customers")
        champions_df = pd.DataFrame(rfm_res["champions"])
        st.dataframe(champions_df[["customer_id", "customer_name", "recency", "frequency", "monetary"]], width='stretch')
