# streamlit_energy_dashboard_with_kpi_percentage.py

import streamlit as st
import pandas as pd
import plotly.express as px

# ============================
# Load Data
# ============================
@st.cache_data
def load_data():
    """
    Load CSV data and convert numeric columns
    """
    df = pd.read_csv('energy_EU.csv')  # Replace with your CSV path
    
    # Convert all columns except 'Country' to numeric
    cols_to_convert = [col for col in df.columns if col != "Country"]
    df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric, errors='coerce')
    
    return df

df = load_data()

# ============================
# Dashboard Title
# ============================
st.title("EU Energy Generation Dashboard")

# ============================
# Sidebar Filters
# ============================
st.sidebar.header("Filters")
countries = st.sidebar.multiselect(
    "Select Countries:",
    options=df['Country'].unique(),
    default=df['Country'].unique()
)

filtered_df = df[df['Country'].isin(countries)]

# ============================
# KPIs at the Top with % Share
# ============================

# Define renewable and non-renewable sources
renewables = ['Hydro-electricity', 'Geo-thermal', 'Tide and wave', 'Solar', 'Wind', 'Biomass and waste']
non_renewables = ['Nuclear', 'Fossil fuels']

# Total power generated across selected countries and sources
total_power = filtered_df[renewables + non_renewables].sum().sum()

# Total renewable and non-renewable power
total_renewable = filtered_df[renewables].sum().sum()
total_non_renewable = filtered_df[non_renewables].sum().sum()

# Calculate percentages
perc_renewable = total_renewable / total_power * 100 if total_power else 0
perc_non_renewable = total_non_renewable / total_power * 100 if total_power else 0

# Display KPIs in 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<h2 style='text-align:center;color:blue'>{100:.1f}%</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-size:14px'>Total Power Generated (GWh): {int(total_power):,}</p>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<h2 style='text-align:center;color:green'>{perc_renewable:.1f}%</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-size:14px'>Total Renewable Power (GWh): {int(total_renewable):,}</p>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<h2 style='text-align:center;color:red'>{perc_non_renewable:.1f}%</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;font-size:14px'>Total Non-Renewable Power (GWh): {int(total_non_renewable):,}</p>", unsafe_allow_html=True)



# ============================
# Power Generation Share
# ============================
st.subheader("⚡ Share of Power Generation by Source")

power_sources = non_renewables + renewables

# Add a Total_Power column for sorting
filtered_df["Total_Power"] = filtered_df[power_sources].sum(axis=1)

# Sort countries by total power
country_order = filtered_df.sort_values("Total_Power", ascending=False)["Country"].tolist()

# Melt data for stacked bar chart
df_melted = filtered_df.melt(
    id_vars='Country',
    value_vars=power_sources,
    var_name='Source',
    value_name='Generation'
)

# Sort sources globally by total generation
source_order = df_melted.groupby("Source")["Generation"].sum().sort_values(ascending=False).index.tolist()

fig_power = px.bar(
    df_melted,
    x='Country',
    y='Generation',
    color='Source',
    title='Power Generation Share by Source',
    labels={'Generation': 'Power Generation (GWh)', 'Country': 'Country'},
    text_auto='.0f',  # Integer labels
    category_orders={'Country': country_order, 'Source': source_order}
)
fig_power.update_xaxes(tickangle=45)
st.plotly_chart(fig_power, use_container_width=True)

# ============================
# Total Energy Consumption
# ============================
st.subheader("📊 Total Energy Consumption by Country")
consumption_order = filtered_df.sort_values("Consumption", ascending=False)["Country"].tolist()

fig_consumption = px.bar(
    filtered_df,
    x='Country',
    y='Consumption',
    title='Total Energy Consumption',
    labels={'Consumption': 'Consumption (GWh)', 'Country': 'Country'},
    text_auto='.0f',  # Integer labels
    color='Consumption',
    category_orders={'Country': consumption_order}
)
fig_consumption.update_xaxes(tickangle=45)
st.plotly_chart(fig_consumption, use_container_width=True)

# ============================
# Exports vs Imports
# ============================
st.subheader("📦 Energy Exports vs Imports by Country")
df_trade = filtered_df.melt(
    id_vars='Country',
    value_vars=['Exports', 'Imports'],
    var_name='Trade Type',
    value_name='Value'
)

trade_order = filtered_df.assign(Total_Trade=filtered_df['Exports']+filtered_df['Imports'])\
                         .sort_values("Total_Trade", ascending=False)["Country"].tolist()

fig_trade = px.bar(
    df_trade,
    x='Country',
    y='Value',
    color='Trade Type',
    title='Exports vs Imports',
    text_auto='.0f',  # Integer labels
    category_orders={'Country': trade_order}
)
fig_trade.update_xaxes(tickangle=45)
st.plotly_chart(fig_trade, use_container_width=True)
