import folium
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
from folium.plugins import HeatMap

MONTREAL_CENTER = [45.5017, -73.5673]
DEFAULT_ZOOM = 11
HEATMAP_GRADIENT = {
    0.15: "navy",
    0.35: "blue",
    0.55: "lime",
    0.75: "yellow",
    1.0: "red",
}

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
latest_year = year_options[-1]

filter_values = st.sidebar.multiselect(
    "Select type of Crimes",
    crime_options,
    default=crime_options,
)
year_values = st.sidebar.multiselect(
    "Select Years",
    year_options,
    default=[latest_year],
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

st.caption(f"Showing {len(filtered_data):,} crimes for the selected filters.")

# Create a map object
if len(filtered_data) > 0:
    map_center = [
        filtered_data["LATITUDE"].mean(skipna=True),
        filtered_data["LONGITUDE"].mean(skipna=True),
    ]

else:
    # If there are no non-NaN values, set a default location (e.g., city center)
    map_center = MONTREAL_CENTER

map = folium.Map(
    location=map_center,
    zoom_start=DEFAULT_ZOOM,
    tiles="OpenStreetMap",
    prefer_canvas=True,
)
folium.TileLayer("CartoDB positron", name="Light map").add_to(map)
folium.TileLayer("CartoDB dark_matter", name="Dark map").add_to(map)

# Create a heatmap layer
heat_points = filtered_data[["LATITUDE", "LONGITUDE"]].dropna().copy()
heat_points["LATITUDE"] = heat_points["LATITUDE"].round(5)
heat_points["LONGITUDE"] = heat_points["LONGITUDE"].round(5)
heat_points = (
    heat_points
    .groupby(["LATITUDE", "LONGITUDE"])
    .size()
    .reset_index(name="WEIGHT")
)
heat_points["WEIGHT"] = heat_points["WEIGHT"].clip(upper=10)
heat_data = heat_points[["LATITUDE", "LONGITUDE", "WEIGHT"]].values.tolist()

if heat_data:
    # Add the heatmap layer to the map
    HeatMap(
        heat_data,
        name="Crime heat map",
        radius=9,
        blur=12,
        min_opacity=0.25,
        max_zoom=16,
        gradient=HEATMAP_GRADIENT,
    ).add_to(map)
    map.fit_bounds([
        [filtered_data["LATITUDE"].min(), filtered_data["LONGITUDE"].min()],
        [filtered_data["LATITUDE"].max(), filtered_data["LONGITUDE"].max()],
    ])
else:
    st.warning("No crimes match the selected filters.")

folium.LayerControl(collapsed=False).add_to(map)

# Display the map
folium_static(map, width=1200, height=700)



