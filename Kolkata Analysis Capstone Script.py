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

# %% [markdown]
# # Methodology
#
# We have the neighborhoods data of kolkata (65 total neighborhoods)and also have the most popular venues in each neighborhood obtained using Foursquare API (5016 venues). But we see that there are multiple neighborhoods with less than 40 venues returned. In order to make a good prediction and create a good analysis let's consider only the neighborhoods with more than 40 venues, as the neighborhoods with less than 40 venues are less popular and hence less populated. So as we want the new bussiness owner to make profit in thier ventures we should only consider neighborhoods which are popular.
#
# We can perform one hot encoding on the obtained data set and use it find the 10 most common venue category in each neighborhood. Then clustering can be performed on the dataset.
# We are using the K - Means clustering technique. To find the optimal number of clusters silhouette score technique is used.
#
# The clusters obtained can be analyzed to find the major types of venue categories in each cluster. This data can be used to suggest business personnels suitable locations based on the category.
#
#

# %%
df = kl_venues.groupby(['Neighborhood'], sort=False)['Venue'].count()
df.plot.bar(figsize=(18, 6))

# %% [markdown]
# The following plot shows only the neighborhoods from which 40 or more than 40 venues were obtained.

# %%
df = df[df >= 40]
df.plot.bar(figsize=(18, 6))

# %% [markdown]
# Lets create a new dataframe, kl_venues_top that contains only the neighborhoods with 40 and above venues with their details included.

# %%
kl_venues_top = kl_venues[kl_venues['Neighborhood'].isin(df.index.tolist())]
kl_venues_top.head()

# %% [markdown]
# #### One Hot Encoding
#

# %%

kl_onehot = pd.get_dummies(
    kl_venues_top['Venue Category'], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
kl_onehot['Neighborhood'] = kl_venues_top['Neighborhood']

# move neighborhood column to the first column
fixed_columns = kl_onehot.columns.tolist()
fixed_columns.insert(0, fixed_columns.pop(fixed_columns.index('Neighborhood')))
kl_onehot = kl_onehot.reindex(columns=fixed_columns)

print(kl_onehot.shape)
kl_onehot.head()

# %% [markdown]
# Let's check the number of unique categories and their names of all the venues returned.
#
#

# %%
print('There are {} unique categories.'.format(
    len(kl_venues['Venue Category'].unique())))


# %%
print('There are {}  categories.'.format(kl_venues['Venue Category'].unique()))

# %% [markdown]
# Lets group the data by neighborhood and taking the mean value of the frequency of occurrence of each category.

# %%
kl_grouped = kl_onehot.groupby('Neighborhood').mean().reset_index()
print(kl_grouped.shape)
kl_grouped

# %% [markdown]
# After removing the neighborhoods with less than 40 venues we are left with 54 neighborhoods and 102 unique categories

# %%
kl_grouped.shape

# %% [markdown]
#  The following function returns the top_venues of each neighborhood.

# %%


def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)

    return row_categories_sorted.index.values[0:num_top_venues]

# %% [markdown]
# Lets use the above function to obtaine the 10 most common venues in each neighborhood and store in the new pandas dataframe **neighborhoods_venues_sorted**.


# %%
num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = kl_grouped['Neighborhood']

for ind in np.arange(kl_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(
        kl_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()

# %% [markdown]
# **Cluster Neighborhoods**
#
# Here K-Means clustering technique is used. Lets use the silhouette_score to obtain the best value for the number of clusters.

# %%
kl_grouped_clustering = kl_grouped.drop('Neighborhood', 1)

max_score = 25
scores = []

for kclusters in range(2, max_score):
    # Run k-means clustering
    kmeans = KMeans(n_clusters=kclusters, init='k-means++',
                    random_state=0).fit_predict(kl_grouped_clustering)

    # Gets the silhouette score
    score = silhouette_score(kl_grouped_clustering, kmeans)
    scores.append(score)

plt.figure(figsize=(20, 10))
plt.plot(np.arange(2, max_score), scores, 'ro-')
plt.xlabel("Number of clusters")
plt.ylabel("Silhouette Score")
plt.xticks(np.arange(2, max_score))
plt.show()

# %% [markdown]
# As seen from the above line plot, the best number of clusters having the **highest silhouette score** is **4**(as the peak is achieved).

# %%

kclusters = 4

kl_grouped_clustering = kl_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(
    kl_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_

# %% [markdown]
# Add the cluster labels to the neighborhoods_venues_sorted dataframe. Let's create a new dataframe kl_merged which has the neighborhood details, cluster labels and the 10 most common venues in that neighborhood.

# %%
# add clustering labels
neighborhoods_venues_sorted.insert(0, 'Cluster Labels', kmeans.labels_)

kl_merged = kl_venues_top[kl_venues_top.columns[0:3]].drop_duplicates()
kl_merged.reset_index(drop=True, inplace=True)

# merge to add latitude/longitude for each neighborhood
kl_merged = kl_merged.join(neighborhoods_venues_sorted.set_index(
    'Neighborhood'), on='Neighborhood')

kl_merged.head()

# %% [markdown]
# The data type of cluster labels is needed to be converted to int32 so that it can be used to check the clusters
# %% [markdown]
# Here we are checking the the number of neighborhoods inside each cluster

# %%

df = kl_merged.copy([['Cluster Labels', 'Neighborhood']])
a = df.groupby(['Cluster Labels'])['Neighborhood'].value_counts()
print(a)

# %% [markdown]
# ## Results
#
# Let’s examine the clusters and find all the venue categories that distinguish each cluster. Let's also print the ten most common venue category in each cluster.
#

# %%

cluster1 = kl_merged.loc[kl_merged['Cluster Labels'] == 0, kl_merged.columns[[0] +
                                                                             list(range(4, kl_merged.shape[1]))]]
venues1 = (cluster1['1st Most Common Venue'].append(
    cluster1['2nd Most Common Venue']).append(
    cluster1['3rd Most Common Venue']).append(
    cluster1['4th Most Common Venue']).append(
    cluster1['5th Most Common Venue']).append(
    cluster1['6th Most Common Venue']).append(
    cluster1['7th Most Common Venue']).append(
    cluster1['8th Most Common Venue']).append(
    cluster1['9th Most Common Venue']).append(
    cluster1['10th Most Common Venue']))

print(venues1.value_counts().head(10))


# %%
kl_merged.loc[kl_merged['Cluster Labels'] == 0,
              kl_merged.columns[[0] + list(range(4, kl_merged.shape[1]))]]


# %%
cluster2 = kl_merged.loc[kl_merged['Cluster Labels'] == 1, kl_merged.columns[[0] +
                                                                             list(range(4, kl_merged.shape[1]))]]
venues2 = (cluster2['1st Most Common Venue'].append(
    cluster2['2nd Most Common Venue']).append(
    cluster2['3rd Most Common Venue']).append(
    cluster2['4th Most Common Venue']).append(
    cluster2['5th Most Common Venue']).append(
    cluster2['6th Most Common Venue']).append(
    cluster2['7th Most Common Venue']).append(
    cluster2['8th Most Common Venue']).append(
    cluster2['9th Most Common Venue']).append(
    cluster2['10th Most Common Venue']))

print(venues2.value_counts().head(10))


# %%
kl_merged.loc[kl_merged['Cluster Labels'] == 1,
              kl_merged.columns[[0] + list(range(4, kl_merged.shape[1]))]]


# %%

cluster3 = kl_merged.loc[kl_merged['Cluster Labels'] == 2, kl_merged.columns[[0] +
                                                                             list(range(4, kl_merged.shape[1]))]]
venues3 = (cluster3['1st Most Common Venue'].append(
    cluster3['2nd Most Common Venue']).append(
    cluster3['3rd Most Common Venue']).append(
    cluster3['4th Most Common Venue']).append(
    cluster3['5th Most Common Venue']).append(
    cluster3['6th Most Common Venue']).append(
    cluster3['7th Most Common Venue']).append(
    cluster3['8th Most Common Venue']).append(
    cluster3['9th Most Common Venue']).append(
    cluster3['10th Most Common Venue']))

print(venues3.value_counts().head(10))


# %%
kl_merged.loc[kl_merged['Cluster Labels'] == 2,
              kl_merged.columns[[0] + list(range(4, kl_merged.shape[1]))]]


# %%

cluster4 = kl_merged.loc[kl_merged['Cluster Labels'] == 3, kl_merged.columns[[0] +
                                                                             list(range(4, kl_merged.shape[1]))]]
venues4 = (cluster4['1st Most Common Venue'].append(
    cluster4['2nd Most Common Venue']).append(
    cluster4['3rd Most Common Venue']).append(
    cluster4['4th Most Common Venue']).append(
    cluster4['5th Most Common Venue']).append(
    cluster4['6th Most Common Venue']).append(
    cluster4['7th Most Common Venue']).append(
    cluster4['8th Most Common Venue']).append(
    cluster4['9th Most Common Venue']).append(
    cluster4['10th Most Common Venue']))

print(venues4.value_counts().head(10))


# %%
kl_merged.loc[kl_merged['Cluster Labels'] == 3,
              kl_merged.columns[[0] + list(range(4, kl_merged.shape[1]))]]
