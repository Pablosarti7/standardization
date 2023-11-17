from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from geopy.geocoders import GoogleV3


api_key = 'AIzaSyAGjauD74twN-leFtr5dGDzM203i94ZK4U'

geolocator = GoogleV3(api_key=api_key)

st.write("""
         # Data Cleaning
         Upload a zillow and a Realtor CSV file.
""")

uploaded_file_one = st.file_uploader("Choose PR file", type=['csv'])
st.markdown("---")
uploaded_file_two = st.file_uploader("Choose Zillow file", type=['csv'])



if uploaded_file_one is not None and uploaded_file_two is not None:
    pr_df = pd.read_csv(uploaded_file_one)
    zillow_df = pd.read_csv(uploaded_file_two)
    
    def standardize_address(address):
        location = geolocator.geocode(address)

        if location:
            return location.address
        else:
            return None

        
    pr_df['standardized_address'] = pr_df['Address'].apply(standardize_address)
    zillow_df['standardized_address'] = zillow_df['address/streetAddress'].apply(standardize_address)
    
    # st.dataframe(pr_df)
    # st.dataframe(zillow_df)

    merged_data = pd.merge(pr_df, zillow_df, on='standardized_address')

    columns_to_keep = ['Address', 'City', 'State', 'ZIP', 'Est Value', 'Est Open Loans $', '1st Rate %', 'Purchase Date',
                    'listedBy/email', 'listedBy/name', 'listedBy/phone', 'listedBy/profileUrl',
                    'livingArea', 'longitude', 'lotSize', 'pageViewCount', 'price',
                    'rentZestimate', 'timeOnZillow', 'url', 'yearBuilt', 'zestimate'
    ]

    merged_data = merged_data[columns_to_keep]
    
    ####

    # Ensure the columns are in numeric format
    merged_data['Est Open Loans $'] = pd.to_numeric(merged_data['Est Open Loans $'], errors='coerce')
    merged_data['price'] = pd.to_numeric(merged_data['price'], errors='coerce')

    # Calculate the ratio
    merged_data['Loans_to_Price'] = merged_data['Est Open Loans $'] / merged_data['price']

    # Filter rows where this value is greater than 88%
    merged_data = merged_data[merged_data['Loans_to_Price'] > 0.88]

    # Convert '1st Rate %' to string, then remove '%' and convert to float
    merged_data['1st Rate %'] = merged_data['1st Rate %'].astype(str).str.rstrip('%').astype(float) / 100

    # Now filter rows
    merged_data = merged_data[merged_data['1st Rate %'] <= 0.05]

    ####

    # Convert "Purchase Date" to datetime format
    merged_data['Purchase Date'] = pd.to_datetime(merged_data['Purchase Date'], errors='coerce')

    # Get the date for 3 years ago from today
    three_years_ago = datetime.today() - timedelta(days=3*365)

    # Keep rows where "1st Rate %" is blank and "Purchase Date" is more than 3 years from today
    merged_data = merged_data[(~merged_data['1st Rate %'].isnull()) | ((merged_data['1st Rate %'].isnull()) & (merged_data['Purchase Date'] < three_years_ago))]

    # Get the date for 1 year ago from today
    one_year_ago = datetime.today() - timedelta(days=365)

    # Filter rows
    merged_data = merged_data[merged_data['Purchase Date'] >= one_year_ago]

    st.dataframe(merged_data)