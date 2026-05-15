import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
from scipy import stats
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Vendor Performance Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #0f1117; }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1e2130, #252a3a);
        border: 1px solid #2e3347;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .kpi-label { color: #8b92a5; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { color: #ffffff; font-size: 28px; font-weight: 700; margin: 6px 0; }
    .kpi-delta { color: #4ade80; font-size: 13px; }
    
    /* Section headers */
    .section-header {
        color: #e2e8f0;
        font-size: 18px;
        font-weight: 600;
        border-left: 4px solid #6366f1;
        padding-left: 12px;
        margin: 20px 0 12px 0;
    }
    
    /* Sidebar */
    .css-1d391kg { background-color: #161a26; }
    
    /* Hide default streamlit header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────
def format_dollars(value):
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.1f}K"
    else:
        return f"${value:.0f}"


@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/vendor_sales_summary.csv')
        df = df[
            (df['GrossProfit'] > 0) &
            (df['ProfitMargin'] > 0) &
            (df['TotalSalesQuantity'] > 0)
        ]
        df['VendorName'] = df['VendorName'].str.strip()
        df['UnitPurchasePrice'] = df['TotalPurchaseDollars'] / df['TotalPurchaseQuantity'].replace(0, np.nan)
        df['UnsoldInventoryValue'] = (df['TotalPurchaseQuantity'] - df['TotalSalesQuantity']) * df['PurchasePrice']
        df['OrderSize'] = pd.qcut(df['TotalPurchaseQuantity'], q=3, labels=["Small", "Medium", "Large"])
        return df
    except Exception as e:
        st.error(f"❌ CSV file not found! Make sure `data/vendor_sales_summary.csv` is in your repo.\n\nError: {e}")
        st.stop()


# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
df = load_data()

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📦 Vendor Dashboard")
    st.markdown("---")

    st.markdown("### 🔍 Filters")

    all_vendors = sorted(df['VendorName'].unique().tolist())
    selected_vendors = st.multiselect(
        "Select Vendor(s)",
        options=all_vendors,
        default=[],
        placeholder="All Vendors"
    )

    margin_range = st.slider(
        "Profit Margin Range (%)",
        min_value=float(df['ProfitMargin'].min()),
        max_value=float(df['ProfitMargin'].max()),
        value=(float(df['ProfitMargin'].min()), float(df['ProfitMargin'].max())),
        step=1.0
    )

    order_sizes = st.multiselect(
        "Order Size",
        options=["Small", "Medium", "Large"],
        default=["Small", "Medium", "Large"]
    )

    st.markdown("---")
    st.markdown("### 📌 Navigation")
    page = st.radio(
        "",
        ["📊 Overview", "🏆 Top Performers", "📦 Inventory Analysis", "📈 Statistical Analysis"],
        label_visibility="collapsed"
    )

# ─────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────
filtered_df = df.copy()

if selected_vendors:
    filtered_df = filtered_df[filtered_df['VendorName'].isin(selected_vendors)]

filtered_df = filtered_df[
    (filtered_df['ProfitMargin'] >= margin_range[0]) &
    (filtered_df['ProfitMargin'] <= margin_range[1])
]

if order_sizes:
    filtered_df = filtered_df[filtered_df['OrderSize'].isin(order_sizes)]


# ═══════════════════════════════════════════
# PAGE 1: OVERVIEW
# ═══════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("# 📦 Vendor Performance Dashboard")
    st.markdown(f"Showing **{len(filtered_df):,} records** · {filtered_df['VendorName'].nunique()} vendors · {filtered_df['Brand'].nunique()} brands")
    st.markdown("---")

    # KPI CARDS
    col1, col2, col3, col4, col5 = st.columns(5)

    total_sales = filtered_df['TotalSalesDollars'].sum()
    total_purchase = filtered_df['TotalPurchaseDollars'].sum()
    total_profit = filtered_df['GrossProfit'].sum()
    avg_margin = filtered_df['ProfitMargin'].mean()
    unsold_capital = filtered_df['UnsoldInventoryValue'].sum()

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Sales</div>
            <div class="kpi-value">{format_dollars(total_sales)}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Purchase</div>
            <div class="kpi-value">{format_dollars(total_purchase)}</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Gross Profit</div>
            <div class="kpi-value">{format_dollars(total_profit)}</div>
            <div class="kpi-delta">▲ Profitable</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Avg Profit Margin</div>
            <div class="kpi-value">{avg_margin:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Unsold Capital</div>
            <div class="kpi-value">{format_dollars(unsold_capital)}</div>
            <div class="kpi-delta" style="color:#f87171;">⚠ Locked</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ROW 2: Distribution Plots
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Profit Margin Distribution</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 3.5))
        fig.patch.set_facecolor('#1e2130')
        ax.set_facecolor('#1e2130')
        sns.histplot(filtered_df['ProfitMargin'], kde=True, bins=30, color='#6366f1', ax=ax)
        ax.axvline(avg_margin, color='#f59e0b', linestyle='--', label=f'Mean: {avg_margin:.1f}%')
        ax.legend(facecolor='#252a3a', labelcolor='white')
        ax.set_xlabel('Profit Margin (%)', color='#8b92a5')
        ax.set_ylabel('Count', color='#8b92a5')
        ax.tick_params(colors='#8b92a5')
        for spine in ax.spines.values():
            spine.set_edgecolor('#2e3347')
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown('<div class="section-header">Stock Turnover Distribution</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 3.5))
        fig.patch.set_facecolor('#1e2130')
        ax.set_facecolor('#1e2130')
        clip_data = filtered_df['StockTurnover'].clip(upper=3)
        sns.histplot(clip_data, kde=True, bins=30, color='#10b981', ax=ax)
        ax.axvline(1, color='#f87171', linestyle='--', label='Turnover = 1')
        ax.legend(facecolor='#252a3a', labelcolor='white')
        ax.set_xlabel('Stock Turnover', color='#8b92a5')
        ax.set_ylabel('Count', color='#8b92a5')
        ax.tick_params(colors='#8b92a5')
        for spine in ax.spines.values():
            spine.set_edgecolor('#2e3347')
        st.pyplot(fig)
        plt.close()

    # ROW 3: Correlation Heatmap
    st.markdown('<div class="section-header">Correlation Heatmap</div>', unsafe_allow_html=True)
    numeric_cols = ['TotalSalesDollars', 'TotalPurchaseDollars', 'GrossProfit',
                    'ProfitMargin', 'StockTurnover', 'SalestoPurchaseRatio', 'FreightCost']
    available_cols = [c for c in numeric_cols if c in filtered_df.columns]
    corr = filtered_df[available_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#1e2130')
    ax.set_facecolor('#1e2130')
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.5, ax=ax, cbar_kws={'shrink': 0.8})
    ax.tick_params(colors='#e2e8f0', labelsize=9)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()


# ═══════════════════════════════════════════
# PAGE 2: TOP PERFORMERS
# ═══════════════════════════════════════════
elif page == "🏆 Top Performers":
    st.markdown("# 🏆 Top Performers")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # Top 10 Vendors by Sales
    with col1:
        st.markdown('<div class="section-header">Top 10 Vendors by Sales</div>', unsafe_allow_html=True)
        top_vendors = filtered_df.groupby('VendorName')['TotalSalesDollars'].sum().nlargest(10).reset_index()

        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor('#1e2130')
        ax.set_facecolor('#1e2130')
        bars = ax.barh(top_vendors['VendorName'], top_vendors['TotalSalesDollars'],
                       color=sns.color_palette("Blues_r", 10))
        for bar, val in zip(bars, top_vendors['TotalSalesDollars']):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                    format_dollars(val), va='center', color='white', fontsize=8)
        ax.tick_params(colors='#e2e8f0', labelsize=8)
        ax.set_xlabel('Total Sales ($)', color='#8b92a5')
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_dollars(x)))
        for spine in ax.spines.values():
            spine.set_edgecolor('#2e3347')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    # Top 10 Brands by Sales
    with col2:
        st.markdown('<div class="section-header">Top 10 Brands by Sales</div>', unsafe_allow_html=True)
        top_brands = filtered_df.groupby('Description')['TotalSalesDollars'].sum().nlargest(10).reset_index()

        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor('#1e2130')
        ax.set_facecolor('#1e2130')
        bars = ax.barh(top_brands['Description'].astype(str), top_brands['TotalSalesDollars'],
                       color=sns.color_palette("Reds_r", 10))
        for bar, val in zip(bars, top_brands['TotalSalesDollars']):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                    format_dollars(val), va='center', color='white', fontsize=8)
        ax.tick_params(colors='#e2e8f0', labelsize=8)
        ax.set_xlabel('Total Sales ($)', color='#8b92a5')
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_dollars(x)))
        for spine in ax.spines.values():
            spine.set_edgecolor('#2e3347')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.markdown("---")

    # Low Sales High Margin Brands
    st.markdown('<div class="section-header">💡 Low Sales but High Margin Brands (Promotion Targets)</div>', unsafe_allow_html=True)
    brand_perf = filtered_df.groupby('Description').agg(
        TotalSalesDollars=('TotalSalesDollars', 'sum'),
        ProfitMargin=('ProfitMargin', 'mean')
    ).reset_index()

    low_sales_thresh = brand_perf['TotalSalesDollars'].quantile(0.15)
    high_margin_thresh = brand_perf['ProfitMargin'].quantile(0.85)

    target_brands = brand_perf[
        (brand_perf['TotalSalesDollars'] <= low_sales_thresh) &
        (brand_perf['ProfitMargin'] >= high_margin_thresh)
    ]

    col1, col2 = st.columns([2, 1])
    with col1:
        plot_df = brand_perf[brand_perf['TotalSalesDollars'] < 10000]
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor('#1e2130')
        ax.set_facecolor('#1e2130')
        ax.scatter(plot_df['TotalSalesDollars'], plot_df['ProfitMargin'],
                   color='#6366f1', alpha=0.3, label='All Brands')
        ax.scatter(target_brands['TotalSalesDollars'], target_brands['ProfitMargin'],
                   color='#f59e0b', s=80, label='🎯 Target Brands')
        ax.axhline(high_margin_thresh, linestyle='--', color='#f87171', alpha=0.7, label=f'High Margin: {high_margin_thresh:.1f}%')
        ax.axvline(low_sales_thresh, linestyle='--', color='#f87171', alpha=0.7, label=f'Low Sales: {format_dollars(low_sales_thresh)}')
        ax.set_xlabel('Total Sales ($)', color='#8b92a5')
        ax.set_ylabel('Profit Margin (%)', color='#8b92a5')
        ax.tick_params(colors='#8b92a5')
        ax.legend(facecolor='#252a3a', labelcolor='white', fontsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor('#2e3347')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.markdown(f"**{len(target_brands)} brands identified**")
        st.dataframe(
            target_brands[['Description', 'TotalSalesDollars', 'ProfitMargin']]
            .sort_values('ProfitMargin', ascending=False)
            .rename(columns={'Description': 'Brand', 'TotalSalesDollars': 'Sales ($)', 'ProfitMargin': 'Margin (%)'})
            .reset_index(drop=True),
            use_container_width=True,
            height=300
        )


# ═══════════════════════════════════════════
# PAGE 3: INVENTORY ANALYSIS
# ═══════════════════════════════════════════
elif page == "📦 Inventory Analysis":
    st.markdown("# 📦 Inventory Analysis")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # Bulk Purchasing Impact
    with col1:
        st.markdown('<div class="section-header">Bulk Purchasing vs Unit Price</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor('#1e2130')
        ax.set_facecolor('#1e2130')
        sns.boxplot(data=filtered_df, x='OrderSize', y='UnitPurchasePrice',
                    palette=['#6366f1', '#10b981', '#f59e0b'],
                    order=['Small', 'Medium', 'Large'], ax=ax)
        ax.set_xlabel('Order Size', color='#8b92a5')
        ax.set_ylabel('Unit Purchase Price ($)', color='#8b92a5')
        ax.tick_params(colors='#e2e8f0')
        for spine in ax.spines.values():
            spine.set_edgecolor('#2e3347')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

        # Summary table
        bulk_summary = filtered_df.groupby('OrderSize', observed=True)['UnitPurchasePrice'].mean().reset_index()
        bulk_summary.columns = ['Order Size', 'Avg Unit Price ($)']
        bulk_summary['Avg Unit Price ($)'] = bulk_summary['Avg Unit Price ($)'].round(2)
        st.dataframe(bulk_summary, use_container_width=True, hide_index=True)

    # Slow Moving Inventory
    with col2:
        st.markdown('<div class="section-header">Slow-Moving Vendors (Turnover < 1)</div>', unsafe_allow_html=True)
        slow_movers = (
            filtered_df[filtered_df['StockTurnover'] < 1]
            .groupby('VendorName')[['StockTurnover']]
            .mean()
            .sort_values('StockTurnover')
            .head(10)
            .reset_index()
        )

        if len(slow_movers) == 0:
            st.info("No slow-moving vendors in current filter.")
        else:
            fig, ax = plt.subplots(figsize=(6, 4))
            fig.patch.set_facecolor('#1e2130')
            ax.set_facecolor('#1e2130')
            bars = ax.barh(slow_movers['VendorName'], slow_movers['StockTurnover'],
                           color='#f87171')
            ax.axvline(1, color='white', linestyle='--', alpha=0.5, label='Turnover = 1')
            ax.set_xlabel('Avg Stock Turnover', color='#8b92a5')
            ax.tick_params(colors='#e2e8f0', labelsize=8)
            ax.legend(facecolor='#252a3a', labelcolor='white')
            for spine in ax.spines.values():
                spine.set_edgecolor('#2e3347')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

    st.markdown("---")

    # Capital Locked in Unsold Inventory
    st.markdown('<div class="section-header">💰 Capital Locked in Unsold Inventory (Top 10 Vendors)</div>', unsafe_allow_html=True)
    unsold = (
        filtered_df.groupby('VendorName')['UnsoldInventoryValue']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor('#1e2130')
        ax.set_facecolor('#1e2130')
        bars = ax.barh(unsold['VendorName'], unsold['UnsoldInventoryValue'],
                       color=sns.color_palette("YlOrRd_r", 10))
        for bar, val in zip(bars, unsold['UnsoldInventoryValue']):
            ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                    format_dollars(val), va='center', color='white', fontsize=8)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: format_dollars(x)))
        ax.tick_params(colors='#e2e8f0', labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor('#2e3347')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col2:
        total_unsold = filtered_df['UnsoldInventoryValue'].sum()
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Unsold Capital</div>
            <div class="kpi-value" style="color:#f87171;">{format_dollars(total_unsold)}</div>
            <div class="kpi-delta" style="color:#f87171;">Locked in inventory</div>
        </div>""", unsafe_allow_html=True)

        unsold_display = unsold.copy()
        unsold_display['UnsoldInventoryValue'] = unsold_display['UnsoldInventoryValue'].apply(format_dollars)
        unsold_display.columns = ['Vendor', 'Unsold Value']
        st.dataframe(unsold_display, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════
# PAGE 4: STATISTICAL ANALYSIS
# ═══════════════════════════════════════════
elif page == "📈 Statistical Analysis":
    st.markdown("# 📈 Statistical Analysis")
    st.markdown("---")

    # Confidence Interval Comparison
    st.markdown('<div class="section-header">95% Confidence Interval — Top vs Low Vendors (Profit Margin)</div>', unsafe_allow_html=True)

    top_threshold = filtered_df['TotalSalesDollars'].quantile(0.75)
    low_threshold = filtered_df['TotalSalesDollars'].quantile(0.25)

    top_vendors_data = filtered_df[filtered_df['TotalSalesDollars'] >= top_threshold]['ProfitMargin'].dropna()
    low_vendors_data = filtered_df[filtered_df['TotalSalesDollars'] <= low_threshold]['ProfitMargin'].dropna()

    def confidence_interval(data, confidence=0.95):
        mean_val = np.mean(data)
        std_err = np.std(data, ddof=1) / np.sqrt(len(data))
        t_critical = stats.t.ppf((1 + confidence) / 2, df=len(data) - 1)
        margin = t_critical * std_err
        return mean_val, mean_val - margin, mean_val + margin

    top_mean, top_lower, top_upper = confidence_interval(top_vendors_data)
    low_mean, low_lower, low_upper = confidence_interval(low_vendors_data)

    # T-Test
    t_stat, p_value = stats.ttest_ind(top_vendors_data, low_vendors_data)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Top Vendors Mean Margin</div>
            <div class="kpi-value">{top_mean:.1f}%</div>
            <div class="kpi-delta">CI: [{top_lower:.1f}%, {top_upper:.1f}%]</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Low Vendors Mean Margin</div>
            <div class="kpi-value">{low_mean:.1f}%</div>
            <div class="kpi-delta" style="color:#f59e0b;">CI: [{low_lower:.1f}%, {low_upper:.1f}%]</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        sig = "✅ Significant" if p_value < 0.05 else "❌ Not Significant"
        color = "#4ade80" if p_value < 0.05 else "#f87171"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">T-Test p-value</div>
            <div class="kpi-value">{p_value:.4f}</div>
            <div class="kpi-delta" style="color:{color};">{sig}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#1e2130')
    ax.set_facecolor('#1e2130')

    sns.histplot(top_vendors_data, kde=True, color='#6366f1', bins=30, alpha=0.5, label='Top Vendors', ax=ax)
    ax.axvline(top_lower, color='#6366f1', linestyle='--', alpha=0.8)
    ax.axvline(top_upper, color='#6366f1', linestyle='--', alpha=0.8)
    ax.axvline(top_mean, color='#6366f1', linestyle='-', linewidth=2)

    sns.histplot(low_vendors_data, kde=True, color='#f87171', bins=30, alpha=0.5, label='Low Vendors', ax=ax)
    ax.axvline(low_lower, color='#f87171', linestyle='--', alpha=0.8)
    ax.axvline(low_upper, color='#f87171', linestyle='--', alpha=0.8)
    ax.axvline(low_mean, color='#f87171', linestyle='-', linewidth=2)

    ax.set_xlabel('Profit Margin (%)', color='#8b92a5')
    ax.set_ylabel('Frequency', color='#8b92a5')
    ax.tick_params(colors='#8b92a5')
    ax.legend(facecolor='#252a3a', labelcolor='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2e3347')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.markdown("---")

    # Pareto Chart - Vendor Purchase Contribution
    st.markdown('<div class="section-header">Pareto Chart — Vendor Purchase Contribution</div>', unsafe_allow_html=True)

    vendor_perf = filtered_df.groupby('VendorName').agg(
        TotalPurchaseDollars=('TotalPurchaseDollars', 'sum')
    ).reset_index().sort_values('TotalPurchaseDollars', ascending=False).head(10)

    vendor_perf['PurchaseContribution%'] = (
        vendor_perf['TotalPurchaseDollars'] / filtered_df['TotalPurchaseDollars'].sum() * 100
    ).round(2)
    vendor_perf['Cumulative%'] = vendor_perf['PurchaseContribution%'].cumsum().round(2)

    fig, ax1 = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor('#1e2130')
    ax1.set_facecolor('#1e2130')

    bars = ax1.bar(vendor_perf['VendorName'], vendor_perf['PurchaseContribution%'],
                   color=sns.color_palette("mako", 10))
    for i, (bar, val) in enumerate(zip(bars, vendor_perf['PurchaseContribution%'])):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 1,
                 f"{val}%", ha='center', color='white', fontsize=8)

    ax2 = ax1.twinx()
    ax2.plot(vendor_perf['VendorName'], vendor_perf['Cumulative%'],
             color='#f59e0b', marker='o', linestyle='dashed', linewidth=2)
    ax2.set_ylabel('Cumulative %', color='#f59e0b')
    ax2.tick_params(colors='#f59e0b')
    ax2.axhline(y=100, color='#4ade80', linestyle='dashed', alpha=0.5)

    ax1.set_xticklabels(vendor_perf['VendorName'], rotation=45, ha='right', color='#e2e8f0', fontsize=8)
    ax1.set_ylabel('Purchase Contribution %', color='#8b92a5')
    ax1.tick_params(colors='#8b92a5')
    for spine in ax1.spines.values():
        spine.set_edgecolor('#2e3347')
    for spine in ax2.spines.values():
        spine.set_edgecolor('#2e3347')

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    # Raw Data Table
    st.markdown("---")
    st.markdown('<div class="section-header">📋 Raw Data Explorer</div>', unsafe_allow_html=True)
    show_cols = ['VendorName', 'Description', 'TotalSalesDollars', 'TotalPurchaseDollars',
                 'GrossProfit', 'ProfitMargin', 'StockTurnover']
    available_show = [c for c in show_cols if c in filtered_df.columns]
    st.dataframe(
        filtered_df[available_show].sort_values('GrossProfit', ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=400
    )
