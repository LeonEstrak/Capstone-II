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

