#Name: Chuhua Zhang
# CS230: Section 3
# Data: Fast Food Restaurants in the USA
# URL: http://localhost:8501/

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk
import streamlit as st

st.title("Welcome to Owen's USA Fast Food Restaurants website")
st.subheader("""
On this website, you can explore all types of restaurants across the USA by filtering the location of the state/city, you will get the detail of the name of the restaurant and including it's physical address, and type.  
""")
st.write("""
1. Use filters in the sidebar to customize and filter the data to see restaurants in specific states and cities.  
2. There are visualizations including bar charts, tables, and an interactive map for you to explore the data.  
3. You can also get detailed information about specific restaurant locations in selected cities and categories.
""")

try:
    data = pd.read_csv("fast_food_usa.csv")
except FileNotFoundError:
    st.error("The dataset file was not found. Please ensure 'fast_food_usa.csv' is in the correct location.")
    st.stop()


# Sidebar for Filters
st.sidebar.title("Filter Options")

# To select a state from the dropdown menu, if nothing is selected by default is all states
unique_states = sorted(data["province"].unique())  # Extract unique states from 'province' column
unique_states = ["All States"] + unique_states  # Add "All States" option at the top
selected_state = st.sidebar.selectbox(
    "Select State",
    options=unique_states
)

# show the data from that specific selected state
if selected_state == "All States":
    state_filtered_data = data  # No filtering, show all data
else:
    state_filtered_data = data[data["province"] == selected_state]  # Filter rows by selected state

# To select a city from the dropdown menu, if nothing is selected by default is all cities
unique_cities = sorted(state_filtered_data["city"].unique())  # Extract unique cities in the selected state
unique_cities = ["All Cities"] + unique_cities  # Add "All Cities" option
selected_city = st.sidebar.selectbox(
    "Select City",
    options=unique_cities
)

# show the data from that specific selected city
if selected_city == "All Cities":
    city_filtered_data = state_filtered_data  # No filtering, show all data for the state
else:
    city_filtered_data = state_filtered_data[state_filtered_data["city"] == selected_city]  # Filter rows by selected city

# To select a category from the dropdown menu, if nothing is selected by default is all category
all_categories = city_filtered_data["categories"].dropna().str.split(", ").explode().unique()
unique_categories = sorted(all_categories)
unique_categories = ["All Categories"] + unique_categories
selected_category = st.sidebar.selectbox(
    "Select Subcategory",
    options=unique_categories
)
# show the data from that specific selected category
if selected_category == "All Categories":
    final_filtered_data = city_filtered_data  # No filtering, show all data for the state and city
else:
    final_filtered_data = city_filtered_data[city_filtered_data["categories"].str.contains(selected_category, na=False)]  # Filter rows by category

# display the table
columns_to_display = ["name", "address", "postalCode", "categories"]
st.write(f"Filtered Restaurants in {selected_city if selected_city != 'All Cities' else 'All Cities'}, {selected_state if selected_state != 'All States' else 'All States'}:")
st.write(final_filtered_data[columns_to_display])


# show the total number of restaurants
restaurant_count = final_filtered_data.shape[0]
st.write(f"Total Restaurants: {restaurant_count}")

#The bar chart pre-condition
if selected_state == "All States":
    state_counts = data["province"].value_counts()
    chart_title = "Number of Restaurants by State"
    x_label = "State"
else:
    state_counts = data[data["province"] == selected_state]["city"].value_counts()
    chart_title = f"Number of Restaurants in {selected_state}"
    x_label = "City"

# Create a bar chart
num_bars = len(state_counts)
fig_width = max(10, num_bars * 0.5)  # Ensure a minimum width, adjust width per bar

st.subheader(chart_title)
fig, ax = plt.subplots(figsize=(fig_width, 6))  # Dynamic width, fixed height
state_counts.sort_values(ascending=False).plot(
    kind="bar",
    ax=ax,
    color="skyblue",
    edgecolor="black"
)
ax.set_title(chart_title, fontsize=16)
ax.set_xlabel(x_label, fontsize=12)
ax.set_ylabel("Number of Restaurants", fontsize=12)
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

# The table
restaurant_counts = (
    data.groupby(["province", "name"])
    .size()
    .reset_index(name="count")
)

# Find the restaurant with the highest count in each state
restaurant_counts = (
    data.groupby(["province", "name"])
    .size()
    .reset_index(name="count")
)

top_restaurants_by_state = (
    restaurant_counts.loc[restaurant_counts.groupby("province")["count"].idxmax()]
    .sort_values(by="province")
)
top_restaurants_by_state.rename(columns={"province": "state"}, inplace=True)

# Allow users to sort the table by number of stores
st.title("Top Restaurants by State")
st.write("The table below shows the which restaurant has the most stores in each state, you can click on the count and select the order in descending and ascending, as well as alphabetical order for state and restaurant name.")
st.dataframe(top_restaurants_by_state.sort_values(by="count", ascending=False))

# interactive map pre-conditions
if selected_state == "All States":
    map_data = data
else:
    map_data = data[data["province"] == selected_state]

map_data = map_data[["latitude", "longitude", "name", "address"]].dropna()

# creating the map
st.title("Interactive Map of Restaurants")
view_state = pdk.ViewState(
    latitude=map_data["latitude"].mean(),
    longitude=map_data["longitude"].mean(),
    zoom=5 if selected_state == "All States" else 8,
    pitch=0,
)

# Define the scatterplot layer
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position="[longitude, latitude]",
    get_color="[255, 0, 0, 160]",  # Red dots
    get_radius=400,  # Adjust the size of dots
    pickable=True,  # Make dots interactive
)
tooltip = {
    "html": "<b>Restaurant Name:</b> {name}<br><b>Address:</b> {address}",
    "style": {"backgroundColor": "black", "color": "white"},
}

deck = pdk.Deck(
    layers=[scatter_layer],
    initial_view_state=view_state,
    tooltip=tooltip,
)
st.pydeck_chart(deck)

st.title("Thank you for visiting the website !")