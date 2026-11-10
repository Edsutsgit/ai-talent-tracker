import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Load the Data
data = {
    'country_or_region': ['China', 'USA', 'India', 'UK', 'Germany', 'Other'],
    'educated_count': [1756, 1109, 462, 185, 139, 971],
    'work_count': [508, 2727, 92, 277, 185, 833],
    'same_origin_work': [193, 887, 92, 120, 76, 450],
    'working_outside': [1563, 222, 370, 65, 63, 521],
    'educated_elsewhere_arriving': [315, 1840, 0, 157, 109, 383]
}
df = pd.DataFrame(data)

# 2. Assign consistent colors to each country
palette = px.colors.qualitative.Pastel
color_map = {country: palette[i % len(palette)] for i, country in enumerate(df['country_or_region'])}

def to_rgba(hex_color, opacity=0.4):
    """Helper to convert hex/rgb to rgba for transparent links."""
    if hex_color.startswith('#'):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"
    return hex_color

# 3. Page Configuration & Sidebar
st.set_page_config(page_title="Global AI Talent Tracker", layout="wide")
st.title("Global AI Talent Mobility")
st.markdown("### Where do top AI researchers trian, and where do they end up working?")
st.markdown("Explore the migration pathways of top-tier AI researchers from their undergraduate training regions to their current employment destinations.")

#Sidebar
st.sidebar.header("Filter & Highlight")
st.sidebar.markdown("Use this panel to isolate specific migration pathways.")
options = ["All Regions"] + df['country_or_region'].tolist()
selected_view = st.sidebar.selectbox("Highlight specific country pathways:", options)

st.sidebar.markdown("---")
st.sidebar.markdown("**About the Data**\n\nThis dashboard represents a sample of 4,622 elite AI researchers publishing at top-tier conferences (NeurIPS, ICML, ICLR).")

# 4. Build Unified Nodes (Always includes all countries)
countries = df['country_or_region'].tolist()
num_countries = len(countries)
pool_index = num_countries * 2

labels = [f"{c} (Trained)" for c in countries] + \
         [f"{c} (Work)" for c in countries] + \
         ["International Talent Pool"]

# Apply colors: full color if selected or global view, muted grey otherwise
node_colors = []
for c in countries:
    if selected_view == "All Regions" or c == selected_view:
        node_colors.append(color_map[c])
    else:
        node_colors.append("#e0e0e0") # Muted grey for unselected educated nodes

for c in countries:
    if selected_view == "All Regions" or c == selected_view:
        node_colors.append(color_map[c])
    else:
        node_colors.append("#e0e0e0") # Muted grey for unselected working nodes
        
node_colors.append("#444444") # Dark grey for the central pool

# 5. Build Unified Flows (Always includes all flows)
source = []
target = []
value = []
link_colors = []

for i, row in df.iterrows():
    educated_idx = i
    working_idx = i + num_countries
    country = row['country_or_region']
    
    # Determine link opacity and color based on selection
    is_highlighted = (selected_view == "All Regions" or country == selected_view)
    
    if is_highlighted:
        outbound_color = to_rgba(color_map[country], 0.5)
        inbound_color = "rgba(68, 68, 68, 0.4)" # Standard grey for pool inbound
    else:
        outbound_color = "rgba(220, 220, 220, 0.2)" # Faint grey for muted outbound flows
        inbound_color = "rgba(220, 220, 220, 0.2)"  # Faint grey for muted inbound flows
    
    # Flow 1: Educated locally -> Working locally (Domestic Retention)
    if row['same_origin_work'] > 0:
        source.append(educated_idx)
        target.append(working_idx)
        value.append(row['same_origin_work'])
        link_colors.append(outbound_color)
        
    # Flow 2: Educated locally -> International Talent Pool (Brain Drain)
    if row['working_outside'] > 0:
        source.append(educated_idx)
        target.append(pool_index)
        value.append(row['working_outside'])
        link_colors.append(outbound_color)
        
    # Flow 3: International Talent Pool -> Working locally (Brain Gain)
    if row['educated_elsewhere_arriving'] > 0:
        source.append(pool_index)
        target.append(working_idx)
        value.append(row['educated_elsewhere_arriving'])
        link_colors.append(inbound_color)

# 6. Render Plotly Figure
fig = go.Figure(data=[go.Sankey(
    arrangement="snap",
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color=node_colors
    ),
    link=dict(
        source=source,
        target=target,
        value=value,
        color=link_colors
    )
)])

fig.update_layout(
#    title_text=f"AI Talent Flow Highlight: {selected_view}",
    title_text="Flow of Elite AI Researchers: Undergraduate Training to Current Workplace",
    font_size=14,
    height=700
)

st.plotly_chart(fig, use_container_width=True)
