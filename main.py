import folium
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
from folium.plugins import HeatMap

MONTREAL_CENTER = [45.5017, -73.5673]

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
crime_options = sorted(data["CATEGORIE"].dropna().unique())
year_options = sorted(data["DATE"].dt.year.dropna().unique())
month_options = list(range(1, 13))

filter_values = st.sidebar.multiselect(
    "Select type of Crimes",
    crime_options,
    default=crime_options,
)
year_values = st.sidebar.multiselect(
    "Select Years",
    year_options,
    default=year_options,
)
month_values = st.sidebar.multiselect(
    "Select Months",
    month_options,
    default=month_options,
)

# Apply filters
filtered_data = data[data["CATEGORIE"].isin(filter_values)&
                     data["DATE"].dt.year.isin(year_values)&
                     data["DATE"].dt.month.isin(month_values)&
                     data["LATITUDE"].notna()&
                     data["LONGITUDE"].notna()]

#st.dataframe(filtered_data)

# Create a map object
if len(filtered_data) > 0:
    map_center = [
        filtered_data["LATITUDE"].mean(skipna=True),
        filtered_data["LONGITUDE"].mean(skipna=True),
    ]

else:
    # If there are no non-NaN values, set a default location (e.g., city center)
    map_center = MONTREAL_CENTER

map = folium.Map(location=map_center, zoom_start=11, tiles="CartoDB positron")

# Create a heatmap layer
heat_data = (
    filtered_data[["LATITUDE", "LONGITUDE"]]
    .dropna()
    .values
    .tolist()
)

if heat_data:
    # Add the heatmap layer to the map
    HeatMap(
        heat_data,
        radius=16,
        blur=18,
        min_opacity=0.35,
        max_zoom=13,
    ).add_to(map)
else:
    st.warning("No crimes match the selected filters.")

# Display the map
folium_static(map)



