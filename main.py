import folium
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
from folium.plugins import HeatMap


# Streamlit configuration
st.set_page_config(layout="wide")
st.title("Montreal Crimes Visualization")

# Read CSV file
data = pd.read_csv("actes-criminels.csv")

# Convert "DATE" column to datetime type
data["DATE"] = pd.to_datetime(data["DATE"])

# Filter out rows with NaN values in latitude or longitude columns
data = data.dropna(subset=["LATITUDE", "LONGITUDE"])
data = data.sort_values(by="DATE")


# Add filters
filter_values = st.sidebar.multiselect("Select type of Crimes", data["CATEGORIE"].unique())
year_values = st.sidebar.multiselect("Select Years", data["DATE"].dt.year.unique())
month_values = st.sidebar.multiselect("Select Months", data["DATE"].dt.month.unique())

# Apply filters
filtered_data = data[data["CATEGORIE"].isin(filter_values)&
                     data["DATE"].dt.year.isin(year_values)&
                     data["DATE"].dt.month.isin(month_values)&
                     data["LATITUDE"].notna()&
                     data["LONGITUDE"].notna()]

#st.dataframe(filtered_data)

# Create a map object
if len(filtered_data) > 0:
    map = folium.Map(location=[filtered_data["LATITUDE"].mean(skipna=True), filtered_data["LONGITUDE"].mean(skipna=True)], zoom_start=13, tiles='Stamen Terrain')

else:
    # If there are no non-NaN values, set a default location (e.g., city center)
    map = folium.Map(location=[45.5017, -73.5673], zoom_start=13, tiles='Stamen Terrain' )

# Create a heatmap layer
heat_data = filtered_data[['LATITUDE', 'LONGITUDE']]
heat_data = heat_data.dropna()  # Drop any remaining NaN values

# Add the heatmap layer to the map
HeatMap(heat_data).add_to(map)

# Display the map
folium_static(map)



