# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %% [markdown]
# # Introduction: Business Problem
#
# Kolkata is considered one of the largest cities in India. It is among the top metro cities in India and is the capital of West Bengal.
# Nowadays, the hotel management industry is becoming one of the
# leading industries among all.
# This project deals with the major venue categories in the neighborhoods of Kolkata.
#
# Our aim is to find the best location to open a **hotel**,**fast food restaurant**, **pizza place** and **multiplex** in the city of joy, Kolkata, to maximize the profit of the owner.
#
# We want to open these in popular neighborhoods which are
# attractive in business aspects.
#
#
# %% [markdown]
# ### Importing required libraries

# %%
# import required libraries
from geopy.geocoders import Nominatim
import geocoder
from bs4 import BeautifulSoup
# from pandas.io.json import json_normalize
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans
import folium
import pandas as pd
import re
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import requests
import numpy as np

# %% [markdown]
# # Data Requirements
#
# Kolkata has many popular neighborhoods. Let's use the list of locations available online in thie site mentioned below.
#
# http://www.nivalink.com/localities-and-landmarks/kolkata
#
# The extracting of data available online is done with the help of Beautiful Soup

# %%
data = requests.get(
    "http://www.nivalink.com/localities-and-landmarks/kolkata").text
soup = BeautifulSoup(data, 'html.parser')
soup

# %% [markdown]
# Here we are using the **find_all method** available in **Beautiful Soup package** to get the  required data and storing it in the form of a pandas dataframe.

# %%
neighborhoodList = []
for row in soup.find_all("div", class_="columnizer")[0].findAll("li"):
    neighborhoodList.append(row.text)

for row in soup.find_all("div", class_="columnizer")[1].findAll("li"):
    neighborhoodList.append(row.text)

kl_df = pd.DataFrame({"Neighborhood": neighborhoodList})

kl_df

# %% [markdown]
# As our data does not have the coordinates of the location that we extracted, we will use the **geocoder package** to get the
# **latitudes** and **longitudes**.

# %%


def get_latlng(neighborhood):
    # initialize your variable to None
    lat_lng_coords = None
    # loop until you get the coordinates
    while(lat_lng_coords is None):
        g = geocoder.arcgis('{}, Kolkata, India'.format(neighborhood))
        lat_lng_coords = g.latlng
    return lat_lng_coords

# %% [markdown]
# After declaring the function we are running a loop through each and every value in the neighborhood dataframe to get the coordinates and updating them in the dataframe


# %%
# iterate to get the latitude and longitude
coords = [get_latlng(neighborhood)
          for neighborhood in kl_df["Neighborhood"].tolist()]


# %%
df_coords = pd.DataFrame(coords, columns=['Latitude', 'Longitude'])


# %%
kl_df['Latitude'] = df_coords['Latitude']
kl_df['Longitude'] = df_coords['Longitude']
kl_df

# %% [markdown]
# We have a total of 65 neighborhoods in total to analyse.
# %% [markdown]
# # Data Visualization
#
# With the help of **Folium** let's visuaize the neighborhood data that we collected. This will be done with by using the coordinates of the location that we collected and updated in our pandas dataset.

# %%
address = 'kolkata, india'

geolocator = Nominatim(user_agent="kl_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geographical coordinate of kolkata, India are {}, {}.'.format(
    latitude, longitude))


# %%

kl_map = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, neighborhood in zip(kl_df['Latitude'], kl_df['Longitude'], kl_df['Neighborhood']):
    label = '{}'.format(neighborhood)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7).add_to(kl_map)

kl_map

# %% [markdown]
# # Analysis of neighborhood
#
# Here with the help of the **FourSquare API** we will try to collect **popular venues** around our locations

# %%
CLIENT_ID = 'U1IPVRAMPLBFIFMILS4T043G0RFFYDDP4MO2HLOQSXUQXB5X'  # your Foursquare ID
# your Foursquare Secret
CLIENT_SECRET = 'UMUZJISLISPZHOQ5Y5X2EC1FVIC5ZL5NAOARJRPMXR35S4E3'
VERSION = '20180604'  # Foursquare API version
LIMIT = 100

# %% [markdown]
# ###  Exploring neighborhoods in Kolkata
#
# The following function will send a explore request for each neighborhood and return the **100 most popular places** in the neighborhood around 3500 meters.
#

# %%


def getNearbyVenues(names, latitudes, longitudes, radius=3500):

    venues_list = []
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)

        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID,
            CLIENT_SECRET,
            VERSION,
            lat,
            lng,
            radius,
            LIMIT)

        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']

        # return only relevant information for each nearby venue
        venues_list.append([(
            name,
            lat,
            lng,
            v['venue']['name'],
            v['venue']['location']['lat'],
            v['venue']['location']['lng'],
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame(
        [item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood',
                             'Neighborhood Latitude',
                             'Neighborhood Longitude',
                             'Venue',
                             'Venue Latitude',
                             'Venue Longitude',
                             'Venue Category']

    return(nearby_venues)

# %% [markdown]
# We are using the the above function on the Kolkata neighborhoods dataframe and store the data of the popular venues in the **kl_df pandas dataframe**.


# %%
kl_venues = getNearbyVenues(names=kl_df['Neighborhood'],
                            latitudes=kl_df['Latitude'],
                            longitudes=kl_df['Longitude']
                            )
kl_venues.head()


# %%
kl_venues

# %% [markdown]
# A total of 5016 venues were obtained. Now let's see the total count of venues per neighborhood

# %%
kl_venues.groupby('Neighborhood').count()

# %% [markdown]
# Let's check the number of unique categories and their names of all the venues returned.

# %%
print('There are {} unique categories.'.format(
    len(kl_venues['Venue Category'].unique())))
print('There are {}  categories.'.format(kl_venues['Venue Category'].unique()))
