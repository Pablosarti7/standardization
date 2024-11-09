import pandas as pd
import streamlit as st
import requests
import usaddress

api_key = 'API_KEY'

st.write("""
         # Data Cleaning
         Start by downloading the sample files on the sidebar.
""")

with st.sidebar:
    st.write("""
             This files below are sample files, download and upload them to start the 
             standardization. Then compare the original files with the new processed files.""")
    
    with open("pr-file.csv", "rb") as file:
        st.download_button(
            label="Download PR file.",
            data=file,
            file_name='pr.csv',
            mime='text/csv',
        )

    with open("zillow-file.csv", "rb") as file:
        st.download_button(
            label="Download Zillow file.",
            data=file,
            file_name='zillow.csv',
            mime='text/csv',
        )

uploaded_file_one = st.file_uploader("Input PR file", type=['csv'])

uploaded_file_two = st.file_uploader("Input Zillow file", type=['csv'])
st.markdown("---")

if uploaded_file_one is not None and uploaded_file_two is not None:
    with st.status("Reading files.", expanded=True) as status:

        pr_df = pd.read_csv(uploaded_file_one)
        zillow_df = pd.read_csv(uploaded_file_two)

        def parse_address(address):
            try:
                return usaddress.tag(address)
            except usaddress.RepeatedLabelError as e:
                return 'Address parsing failed'

        def standardize_address(address, api_key):
            parsed_address = parse_address(address)
            if parsed_address is None:
                return 'Parsed address is empty'

            # Construct a query for the API
            try:
                query = ' '.join(parsed_address[0].values())
            except AttributeError:
                query = 'None'

            response = requests.get(f"https://api.opencagedata.com/geocode/v1/json?q={query}&key={api_key}")
            
            if response.status_code != 200:
                return 'API request failed'
            
            data = response.json()
            # Extract the standardized address
            # The structure depends on the API response format
            if data['results']:
                return data['results'][0]['formatted']

            return 'No results found'

        api_key = '1cf198e6626b4be1bc9e375edf5053d5'
        
        st.write("Standardizing PR file")

        for index, row in pr_df.iterrows():
            address = str(row['Address']) + " " + str(row['City']) + " " + str(row['State']) + " " + str(row['ZIP'])
            standardized = standardize_address(address, api_key)
            if standardized:
                pr_df.at[index, 'Address'] = standardized

        st.write("Standardizing Zillow file")

        for index, row in zillow_df.iterrows():
            address = str(row['address/streetAddress']) + " " + str(row['address/city']) + " " + str(row['address/state']) + " " + str(row['address/zipcode'])
            standardized = standardize_address(address, api_key)
            if standardized:
                zillow_df.at[index, 'address/streetAddress'] = standardized

        st.dataframe(pr_df)
        st.dataframe(zillow_df)

    st.success('Done!')
