import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -----------------------------------------
# Page Configuration & Header
# -----------------------------------------
st.set_page_config(page_title="Global AI Talent Tracker", layout="wide")
st.title("Global AI Talent Mobility")
st.markdown("### Where do top AI researchers train, and where do they end up working?")
st.markdown("Explore the migration pathways of top-tier AI researchers from their undergraduate training regions to their current employment destinations.")

# -----------------------------------------
# Data Loading (2025 MacroPolo Dataset)
# -----------------------------------------
@st.cache_data
def load_data():
    # Embedded 2025 dataset for self-contained execution
    data = {
        'country_or_region': ['China', 'USA', 'India', 'UK', 'Germany', 'Other'],
        'educated_count': [1756, 1109, 462, 185, 139, 971],
        'work_count': [508, 2727, 92, 277, 185, 833],
        'same_origin_work': [193, 887, 92, 120, 76, 450],
        'working_outside': [1563, 222, 370, 65, 63, 521],
        'educated_elsewhere_arriving': [315, 1840, 0, 157, 109, 383]
    }
    df = pd.DataFrame(data)
    df['total_flow'] = df['educated_count'] + df['work_count']
    return df.sort_values('total_flow', ascending=False)

df = load_data()
countries = df['country_or_region'].tolist()

# -----------------------------------------
# Sidebar Filtering Engine
# -----------------------------------------
st.sidebar.header("Filter & Highlight")
st.sidebar.markdown("Use this panel to isolate specific migration pathways.")
selected_country = st.sidebar.selectbox("Highlight specific country pathways:", ["All Regions"] + countries)

st.sidebar.markdown("---")
st.sidebar.markdown("**About the Data**\n\nThis dashboard represents a sample of 4,622 elite AI researchers publishing at top-tier conferences (NeurIPS, ICML, ICLR).")

# -----------------------------------------
# Sankey Diagram Generation
# -----------------------------------------
n = len(countries)
labels = [f"{c} (Trained)" for c in countries] + [f"{c} (Work)" for c in countries] + ["International Mobility Pool"]

source = []
target = []
value = []
link_colors = []

# Define colors for highlighting
color_highlight_stay = "rgba(100, 100, 200, 0.7)"
color_highlight_leave = "rgba(255, 100, 100, 0.7)"
color_highlight_arrive = "rgba(100, 200, 100, 0.7)"
color_muted = "rgba(220, 220, 220, 0.3)"

for i, row in df.iterrows():
    c = row['country_or_region']
    
    # Check if this row is targeted by the filter
    is_active = (selected_country == "All Regions") or (selected_country == c)
    
    # 1. Stayed in origin country (Trained -> Work)
    if row['same_origin_work'] > 0:
        source.append(i)
        target.append(i + n)
        value.append(row['same_origin_work'])
        link_colors.append(color_highlight_stay if is_active else color_muted)
    
    # 2. Left origin country (Trained -> International Pool)
    if row['working_outside'] > 0:
        source.append(i)
        target.append(2 * n)
        value.append(row['working_outside'])
        link_colors.append(color_highlight_leave if is_active else color_muted)
        
    # 3. Arrived in work country (International Pool -> Work)
    if row['educated_elsewhere_arriving'] > 0:
        source.append(2 * n)
        target.append(i + n)
        value.append(row['educated_elsewhere_arriving'])
        link_colors.append(color_highlight_arrive if is_active else color_muted)

# Build the Plotly figure
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=20,
        thickness=25,
        line=dict(color="black", width=0.5),
        label=labels,
        color="#3498db"
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=link_colors
    )
)])

fig.update_layout(
    title_text="Flow of Elite AI Researchers: Undergraduate Training to Current Workplace",
    font_size=13,
    height=750,
    margin=dict(t=50, l=20, r=20, b=20)
)

# Render chart
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------
# Dynamic Metrics Panel
# -----------------------------------------
st.markdown("### Regional Highlights")
if selected_country != "All Regions":
    country_data = df[df['country_or_region'] == selected_country].iloc[0]
    
    retention_rate = (country_data['same_origin_work'] / country_data['educated_count']) * 100
    net_brain_gain = country_data['work_count'] - country_data['educated_count']
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Trained Domestically", f"{country_data['educated_count']:,}")
    col2.metric("Currently Employed", f"{country_data['work_count']:,}")
    col3.metric("Retention Rate", f"{retention_rate:.1f}%")
    col4.metric("Net Talent Gain/Drain", f"{net_brain_gain:+,}")
else:
    # Show global aggregates when "All Regions" is selected
    total_researchers = df['educated_count'].sum()
    total_mobile = df['working_outside'].sum()
    global_mobility_rate = (total_mobile / total_researchers) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Elite Researchers", f"{total_researchers:,}")
    col2.metric("Internationally Mobile", f"{total_mobile:,}")
    col3.metric("Global Mobility Rate", f"{global_mobility_rate:.1f}%")

# -----------------------------------------
# Raw Data Table
# -----------------------------------------
with st.expander("View Underlying Data Table"):
    display_df = df.rename(columns={
        'country_or_region': 'Region',
        'educated_count': 'Trained (Count)',
        'work_count': 'Employed (Count)',
        'same_origin_work': 'Domestic Retention',
        'working_outside': 'Emigrated',
        'educated_elsewhere_arriving': 'Immigrated'
    }).drop(columns=['total_flow'])
    st.dataframe(display_df, use_container_width=True)
