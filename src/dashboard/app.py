import matplotlib
matplotlib.use('Agg')
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Lending Portfolio Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CUSTOM CSS (DARK LUXURY THEME) ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* MAIN BACKGROUND */
    .stApp {
        background: #0b0e14;
        background-image: radial-gradient(ellipse at 20% 50%, #141b2b 0%, transparent 70%),
                          radial-gradient(ellipse at 80% 50%, #141b2b 0%, transparent 70%);
    }
    
    /* SIDEBAR */
    .css-1d391kg, .css-12oz5g7, .stSidebar {
        background: #0f131a !important;
        border-right: 1px solid rgba(212, 175, 55, 0.15);
    }
    .stSidebar .sidebar-content {
        background: #0f131a !important;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #d4af37 !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .stSidebar .stSelectbox label, .stSidebar .stMultiSelect label {
        color: #8892a8 !important;
        font-weight: 500;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .stSidebar .stSelectbox div, .stSidebar .stMultiSelect div {
        background-color: #1a2332 !important;
        border: 1px solid #2a3a55 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    .stSidebar .stMultiSelect [data-baseweb="tag"] {
        background-color: #d4af37 !important;
        color: #0b0e14 !important;
        font-weight: 600;
    }
    
    /* HEADER GLASS CARD */
    .main-header {
        background: linear-gradient(135deg, rgba(20, 30, 50, 0.95) 0%, rgba(10, 15, 25, 0.98) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 16px;
        padding: 28px 35px;
        margin-bottom: 30px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.6), inset 0 1px 0 rgba(212, 175, 55, 0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 34px;
        font-weight: 800;
        background: linear-gradient(135deg, #d4af37 0%, #f5e56b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
        text-shadow: 0 0 40px rgba(212, 175, 55, 0.15);
    }
    .main-header .subtitle {
        margin: 6px 0 0 0;
        color: #8892a8;
        font-size: 15px;
        font-weight: 400;
        letter-spacing: 0.3px;
        border-left: 3px solid #d4af37;
        padding-left: 16px;
    }
    .main-header .date-badge {
        float: right;
        background: rgba(212, 175, 55, 0.12);
        border: 1px solid rgba(212, 175, 55, 0.25);
        padding: 6px 18px;
        border-radius: 30px;
        color: #d4af37;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* METRIC CARDS - GLASSMORPHISM */
    .metric-card {
        background: rgba(20, 30, 50, 0.65);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(212, 175, 55, 0.3);
        box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 30px rgba(212, 175, 55, 0.05);
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #8892a8;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #f0f4fa;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .metric-value .currency {
        font-size: 18px;
        color: #d4af37;
        font-weight: 600;
        margin-right: 4px;
    }
    .metric-sub {
        font-size: 13px;
        color: #5a6a82;
        margin-top: 4px;
        font-weight: 400;
    }
    
    /* DELINQUENCY CARD - GRADIENT BORDER */
    .metric-card-danger {
        border-left: 4px solid #ff4757;
        background: rgba(255, 71, 87, 0.08);
    }
    .metric-card-success {
        border-left: 4px solid #2ed573;
        background: rgba(46, 213, 115, 0.08);
    }
    .metric-card-warning {
        border-left: 4px solid #ffa502;
        background: rgba(255, 165, 2, 0.08);
    }
    .metric-value-danger { color: #ff4757; }
    .metric-value-success { color: #2ed573; }
    .metric-value-warning { color: #ffa502; }
    
    /* CHART CONTAINERS */
    .chart-container {
        background: rgba(15, 20, 30, 0.7);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 22px 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
        margin: 8px 0;
    }
    .chart-container h3 {
        color: #d4af37;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.1);
        padding-bottom: 10px;
    }
    
    /* DATAFRAME */
    .dataframe-container {
        background: rgba(15, 20, 30, 0.7);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    .dataframe-container h3 {
        color: #d4af37;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    
    /* STREAMLIT OVERRIDES */
    .stDataFrame {
        background: transparent !important;
    }
    .stDataFrame thead tr th {
        background: #1a2332 !important;
        color: #d4af37 !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        border-bottom: 2px solid #d4af37 !important;
    }
    .stDataFrame tbody tr td {
        background: transparent !important;
        color: #c8d0dc !important;
        border-bottom: 1px solid rgba(255,255,255,0.03) !important;
        font-size: 13px !important;
    }
    .stDataFrame tbody tr:hover td {
        background: rgba(212, 175, 55, 0.05) !important;
    }
    
    /* FOOTER */
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid rgba(255,255,255,0.04);
        color: #3a4a62;
        font-size: 12px;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* SIDEBAR SEPARATOR */
    .sidebar-separator {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(212, 175, 55, 0.2), transparent);
        margin: 20px 0;
    }
    
    /* FILTER LABELS */
    .filter-label {
        color: #8892a8;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============ HEADER ============
today = datetime.now().strftime("%B %d, %Y")

st.markdown(f"""
<div class="main-header">
    <span class="date-badge">📅 {today}</span>
    <h1>⚡ Lending Portfolio Analytics</h1>
    <div class="subtitle">Executive Risk Dashboard · Real-time Delinquency Monitoring</div>
</div>
""", unsafe_allow_html=True)

# ============ LOAD DATA ============
@st.cache_data
def load_data():
    portfolio = pd.read_csv('data/portfolio_raw.csv')
    clients = pd.read_csv('data/clients_raw.csv')
    products = pd.read_csv('data/products_raw.csv')
    merged = portfolio.merge(clients, on='client_id').merge(products, on='product_id')
    merged['origination_date'] = pd.to_datetime(merged['origination_date'])
    merged['last_payment_date'] = pd.to_datetime(merged['last_payment_date'])
    return merged

df = load_data()

# ============ SIDEBAR ============
st.sidebar.markdown("<h2 style='text-align:center;'>🏛️ CONTROL PANEL</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr class='sidebar-separator'>", unsafe_allow_html=True)

st.sidebar.markdown("<p class='filter-label'>📍 Province</p>", unsafe_allow_html=True)
province_filter = st.sidebar.multiselect(
    "",
    options=df['province'].unique(),
    default=df['province'].unique(),
    key="province"
)

st.sidebar.markdown("<p class='filter-label'>📦 Product Type</p>", unsafe_allow_html=True)
product_filter = st.sidebar.multiselect(
    "",
    options=df['product_type'].unique(),
    default=df['product_type'].unique(),
    key="product"
)

st.sidebar.markdown("<p class='filter-label'>⚠️ Payment Status</p>", unsafe_allow_html=True)
status_filter = st.sidebar.multiselect(
    "",
    options=df['payment_status'].unique(),
    default=df['payment_status'].unique(),
    key="status"
)

st.sidebar.markdown("<hr class='sidebar-separator'>", unsafe_allow_html=True)
st.sidebar.caption("🔒 Confidential · Simulated Data")

# ============ FILTER DATA ============
filtered = df[
    (df['province'].isin(province_filter)) &
    (df['product_type'].isin(product_filter)) &
    (df['payment_status'].isin(status_filter))
]

# ============ METRICS ROW ============
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📊 Total Loans</div>
        <div class="metric-value">{len(filtered):,}</div>
        <div class="metric-sub">Active portfolio accounts</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_value = filtered['remaining_balance'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 Portfolio Value</div>
        <div class="metric-value"><span class="currency">$</span>{total_value:,.0f}</div>
        <div class="metric-sub">Total outstanding balance</div>
    </div>
    """, unsafe_allow_html=True)

delinquent = filtered[filtered['payment_status'].isin(['90+ Days Past Due', 'Default'])]
del_rate = (len(delinquent) / len(filtered)) * 100 if len(filtered) > 0 else 0

with col3:
    if del_rate > 10:
        card_class = "metric-card-danger"
        value_class = "metric-value-danger"
        status_text = "⚠️ High Risk"
    elif del_rate > 5:
        card_class = "metric-card-warning"
        value_class = "metric-value-warning"
        status_text = "⚡ Moderate"
    else:
        card_class = "metric-card-success"
        value_class = "metric-value-success"
        status_text = "✅ Healthy"
    
    st.markdown(f"""
    <div class="metric-card {card_class}">
        <div class="metric-label">🚨 Delinquency Rate</div>
        <div class="metric-value {value_class}">{del_rate:.2f}%</div>
        <div class="metric-sub">{status_text} · {len(delinquent)} loans at risk</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_rate = filtered['interest_rate'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📈 Avg Interest Rate</div>
        <div class="metric-value">{avg_rate:.2f}%</div>
        <div class="metric-sub">Weighted portfolio yield</div>
    </div>
    """, unsafe_allow_html=True)

# ============ CHARTS ROW ============
st.markdown("<br>", unsafe_allow_html=True)
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="chart-container"><h3>📍 Delinquency by Province</h3>', unsafe_allow_html=True)
    
    prov_del = filtered[filtered['payment_status'].isin(['90+ Days Past Due', 'Default'])].groupby('province').size()
    
    if not prov_del.empty:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        colors_gold = ['#d4af37', '#c9a030', '#b8912a', '#a78224', '#96731e']
        bars = ax.bar(prov_del.index, prov_del.values, color=colors_gold[:len(prov_del)], 
                      edgecolor='#d4af37', linewidth=1.5, alpha=0.9)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', 
                    fontweight='700', fontsize=12, color='#d4af37')
        
        ax.set_ylabel('Count', color='#8892a8', fontweight='600', fontsize=11)
        ax.set_xlabel('Province', color='#8892a8', fontweight='600', fontsize=11)
        ax.tick_params(colors='#8892a8', labelsize=11)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#2a3a55')
        ax.spines['bottom'].set_color('#2a3a55')
        ax.grid(axis='y', linestyle='--', alpha=0.2, color='#d4af37')
        
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("✅ No delinquent loans in selected filters.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="chart-container"><h3>📊 Portfolio Composition</h3>', unsafe_allow_html=True)
    
    prod_counts = filtered['product_type'].value_counts()
    
    if not prod_counts.empty:
        fig2, ax2 = plt.subplots(figsize=(8, 4.5))
        fig2.patch.set_facecolor('none')
        ax2.set_facecolor('none')
        
        colors_pie = ['#d4af37', '#c9a030', '#b8912a', '#a78224', '#96731e', '#8a6518']
        wedges, texts, autotexts = ax2.pie(
            prod_counts.values,
            labels=prod_counts.index,
            autopct='%1.1f%%',
            colors=colors_pie[:len(prod_counts)],
            startangle=90,
            wedgeprops={'edgecolor': '#0b0e14', 'linewidth': 2.5},
            textprops={'fontsize': 11, 'fontweight': '600', 'color': '#f0f4fa'}
        )
        for autotext in autotexts:
            autotext.set_color('#0b0e14')
            autotext.set_fontweight('800')
            autotext.set_fontsize(12)
        ax2.axis('equal')
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("No data for selected filters.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============ DATA TABLE ============
st.markdown("---")
st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
st.markdown('<h3>📋 Loan Details</h3>', unsafe_allow_html=True)

display_cols = ['full_name', 'province', 'product_name', 'loan_amount', 'remaining_balance', 'payment_status', 'origination_date']
display_df = filtered[display_cols].copy()
display_df['loan_amount'] = display_df['loan_amount'].apply(lambda x: f"${x:,.2f}")
display_df['remaining_balance'] = display_df['remaining_balance'].apply(lambda x: f"${x:,.2f}")
display_df['origination_date'] = display_df['origination_date'].dt.strftime('%Y-%m-%d')

st.dataframe(
    display_df,
    use_container_width=True,
    height=350,
    column_config={
        "full_name": "Client Name",
        "province": "Province",
        "product_name": "Product",
        "loan_amount": "Original Amount",
        "remaining_balance": "Balance",
        "payment_status": "Status",
        "origination_date": "Origination"
    }
)
st.markdown('</div>', unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("""
<div class="footer">
    ⚡ Lending Analytics Platform v3.0 · Confidential · For Internal Use Only
</div>
""", unsafe_allow_html=True)