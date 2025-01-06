import pandas as pd
import os
import zipfile
import folium
import streamlit as st
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns
from kaggle.api.kaggle_api_extended import KaggleApi
st.set_page_config(
    page_title="Chicago Red Light and Speed Cameras",
    layout="wide",
    initial_sidebar_state="expanded",
)
@st.cache_data
def data_load():
    

    
    api = KaggleApi()
    api.authenticate()

   
    dataset_identifier = 'chicago-red-light-and-speed-camera-data'  

   
    DATA_DIR = 'data'
    os.makedirs(DATA_DIR, exist_ok=True)

    
    api.dataset_download_files(dataset_identifier, path=DATA_DIR, unzip=True)

    
    red_light_path = os.path.join(DATA_DIR, 'red-light-camera-violations.csv')
    speed_path = os.path.join(DATA_DIR, 'speed-camera-violations.csv')
    red_location_path = os.path.join(DATA_DIR, 'red-light-camera-locations.csv')
    speed_location_path = os.path.join(DATA_DIR, 'speed-camera-locations.csv')

   
    red_light = pd.read_csv(red_light_path)
    speed = pd.read_csv(speed_path)
    red_location = pd.read_csv(red_location_path)
    speed_location = pd.read_csv(speed_location_path)

    return red_light, speed, red_location, speed_location



red_light, speed, red_location, speed_location = data_load()


red_light['VIOLATION DATE'] = pd.to_datetime(red_light['VIOLATION DATE'], format = "%Y-%m-%dT%H:%M:%S.%f")
speed['VIOLATION DATE'] = pd.to_datetime(speed['VIOLATION DATE'], format = "%Y-%m-%dT%H:%M:%S.%f")



red_light_count_df = red_light.groupby('INTERSECTION')['VIOLATIONS'].sum().reset_index()


speed_count_df = speed.groupby('ADDRESS')['VIOLATIONS'].sum().reset_index()


violations_per_date = {}
months = red_light['VIOLATION DATE'].dt.month.unique()
days = red_light['VIOLATION DATE'].dt.day.unique()
for month in months:
    for day in days:
        violations_per_date[str(month) + '_' + str(day)] = 0
        day_data = red_light[(red_light['VIOLATION DATE'].dt.month == month) & (red_light['VIOLATION DATE'].dt.day == day)]
        for violation in day_data[['VIOLATIONS']].dropna().values.tolist():
            violations_per_date[str(month) + '_' + str(day)] += int(violation[0])
violations_per_date_speed = {}
months = speed['VIOLATION DATE'].dt.month.unique()
days = speed['VIOLATION DATE'].dt.day.unique()
for month in months:
    for day in days:
        violations_per_date_speed[str(month) + '_' + str(day)] = 0
        day_data = speed[(speed['VIOLATION DATE'].dt.month == month) & (speed['VIOLATION DATE'].dt.day == day)]
        for violation in day_data[['VIOLATIONS']].dropna().values.tolist():
            violations_per_date_speed[str(month) + '_' + str(day)] += int(violation[0])
#print(red_light_count)


#m = folium.Map(location=(41.8781, -87.6298), tiles = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', attr = 'mine')



st.sidebar.title('Navigation')
options = st.sidebar.radio("Go to", ["Map", "Stats"])
if options == "Map":
    m = folium.Map(location=(41.8781, -87.6298), tiles = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', attr = 'mine')
    for _, location in red_location.iterrows():
    
        folium.Marker(location = [location['LATITUDE'], location['LONGITUDE']], popup = location['INTERSECTION'], icon=folium.Icon(color = 'red', icon = 'dot')).add_to(m)
            
    for _, location in speed_location.iterrows():

        folium.Marker(location = [location['LATITUDE'], location['LONGITUDE']], popup=location['ADDRESS'] ).add_to(m)
    folium_static(m, width = 1400, height = 1000)
elif options == "Stats":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Red-Light Camera Violations")
        
        top_red_light = red_light_count_df.sort_values(by='VIOLATIONS', ascending=False).head(10)
        
        st.dataframe(top_red_light.style.format({'VIOLATIONS': '{:,}'}))

        fig_red, ax_red = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=top_red_light,
            x='VIOLATIONS',
            y='INTERSECTION',
            palette='Reds_r',
            ax=ax_red
        )
        ax_red.set_xlabel("Number of Violations")
        ax_red.set_ylabel("Intersection")
        ax_red.set_title("Top 10 Red-Light Camera Violations")
        plt.tight_layout()
        st.pyplot(fig_red)
    
    with col2:
        st.subheader("Top 10 Speed Camera Violations")
        
       
        top_speed = speed_count_df.sort_values(by='VIOLATIONS', ascending=False).head(10)
        
        
        st.dataframe(top_speed.style.format({'VIOLATIONS': '{:,}'}))
        
    
        fig_speed, ax_speed = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=top_speed,
            x='VIOLATIONS',
            y='ADDRESS',
            palette='Blues_r',
            ax=ax_speed
        )
        ax_speed.set_xlabel("Number of Violations")
        ax_speed.set_ylabel("Address")
        ax_speed.set_title("Top 10 Speed Camera Violations")
        plt.tight_layout()
        st.pyplot(fig_speed)
