import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Assuming df is already loaded from '/content/swiggy (1).csv'
# If running this as a standalone script, you would load it here:
df = pd.read_csv('/content/swiggy (1).csv')

# Set page configuration
st.set_page_config(page_title='Swiggy Data Dashboard', page_icon=':curry:', layout='wide')

st.title('Swiggy Restaurant Data Dashboard :curry:')
st.markdown('Explore restaurant data with interactive filters and visualizations.')

# --- Sidebar for Filters ---
st.sidebar.header('Filter Options')

# City Filter
all_cities = df['City'].unique().tolist()
selected_cities = st.sidebar.multiselect(
    'Select City(s)',
    options=all_cities,
    default=all_cities
)

# Food Type Filter
# Extract all unique food types and flatten the list, then get unique values
all_food_types = sorted(list(set([ft.strip() for sublist in df['Food type'].apply(lambda x: x.split(',')) for ft in sublist])))
selected_food_type = st.sidebar.selectbox(
    'Select Food Type',
    options=['All'] + all_food_types,
    index=0
)

# Price Range Slider
min_price, max_price = int(df['Price'].min()), int(df['Price'].max())
price_range = st.sidebar.slider(
    'Select Price Range (INR)',
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# Filter data based on selections
filtered_df = df[df['City'].isin(selected_cities)]

if selected_food_type != 'All':
    filtered_df = filtered_df[filtered_df['Food type'].str.contains(selected_food_type, case=False, na=False)]

filtered_df = filtered_df[
    (filtered_df['Price'] >= price_range[0]) & (filtered_df['Price'] <= price_range[1])
]

# Display Filtered Data
st.subheader('Filtered Restaurant Data')
st.dataframe(filtered_df)

# --- Summary Report ---
st.subheader('Summary Report')

if not filtered_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Restaurants", len(filtered_df))
    col2.metric("Average Price (INR)", f"{filtered_df['Price'].mean():.2f}")
    col3.metric("Average Rating", f"{filtered_df['Avg ratings'].mean():.2f}")
    
    # Highest-rated restaurant
    highest_rated_restaurant = filtered_df.loc[filtered_df['Avg ratings'].idxmax()]
    col4.metric("Highest Rated Restaurant", highest_rated_restaurant['Restaurant'] + f" ({highest_rated_restaurant['Avg ratings']} stars)")
else:
    st.warning('No restaurants found matching your criteria.')

# --- Data Visualization ---
st.subheader('Data Visualizations')

if not filtered_df.empty:
    # Visualization 1: Count of Restaurants per City
    st.markdown('#### Count of Restaurants per City')
    city_counts = filtered_df['City'].value_counts().reset_index()
    city_counts.columns = ['City', 'Number of Restaurants']
    st.bar_chart(city_counts.set_index('City'))

    # Visualization 2: Average Rating per Food Type (Top 10)
    st.markdown('#### Top 10 Food Types by Average Rating')
    # Expand food types to individual rows for proper aggregation
    expanded_food_types = filtered_df.assign(Food_Type_Split=filtered_df['Food type'].str.split(',')).explode('Food_Type_Split')
    expanded_food_types['Food_Type_Split'] = expanded_food_types['Food_Type_Split'].str.strip()
    
    avg_ratings_food_type = expanded_food_types.groupby('Food_Type_Split')['Avg ratings'].mean().sort_values(ascending=False).head(10).reset_index()
    avg_ratings_food_type.columns = ['Food Type', 'Average Rating']
    
    if not avg_ratings_food_type.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(avg_ratings_food_type['Food Type'], avg_ratings_food_type['Average Rating'], color='skyblue')
        ax.set_xlabel('Food Type')
        ax.set_ylabel('Average Rating')
        ax.set_title('Top 10 Food Types by Average Rating')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info('No food types to visualize with current filters.')
else:
    st.info('No data available for visualizations with the current filters.')
