import random
import pandas as pd
import numpy as np
import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt
from geopy.distance import geodesic



def create_distance_matrix(df):
    # df is a pandas DataFrame that must contain Longitude and Latitude columns
    length = df.shape[0]

    # intialize square matrix of shape length x length
    matrix = [[0 for i in range(length)] for j in range(length)]
    for i in range(length):
        for j in range(length):
            distance =  round(geodesic( (df.loc[i, "Latitude"], df.loc[i, "Longitude"]), (df.loc[j, "Latitude"], df.loc[j, "Longitude"])).km)
            matrix[i][j] = distance
    return matrix


def print_matrix(matrix):
    # print a Python 2d array (does not work for Numpy Array)
    length = len(matrix)
    for i in range(length):
        for j in range(length):
         print(matrix[i][j], "", end="")
    print("\n")


def create_distance_matrix_numpy(df):
  # Takes a pandas DataFrame that must contain Longitude and Latitude columns
  # Returns a numpy matrix where the indexes of each row/column correspond with the point in the input DataFrame
  length = df.shape[0]

  matrix = np.empty((length, length))
  for i in range(length):
    for j in range(length):
      distance = round( geodesic((df.loc[i, "Latitude"], df.loc[i, "Longitude"]), (df.loc[j, "Latitude"], df.loc[j, "Longitude"])).km)
      matrix[i,j] = distance
  return matrix

def distance_between(location1, location2):
    '''Returns rounded integer of number of kilometers (km) between two locations on Earth'''
    return round(geodesic((location1['Latitude'], location1['Longitude']),
                   (location2['Latitude'], location2['Longitude'])).km)

def find_nearest(location, list_of_neighbors):
    '''Returns a dict containing the original list Index, Name, and distance-to nearest neighbor'''

    if len(list_of_neighbors) is 0:
        return {'Index':None, 'Name': None, 'Distance': None}

    # Choose first neighbor to calculate distance
    currNeighbor = list_of_neighbors[0]
    minDistance = distance_between(location, currNeighbor)
    minIndex = 0


    for i in range(1,len(list_of_neighbors)): # start at index 1 because we already tested the 0 index neighbor
        currNeighbor = list_of_neighbors[i]
        currDistance = distance_between(location, currNeighbor)
        if currDistance < minDistance:
            minIndex = i
            minDistance = currDistance

    return {'Index':minIndex, 'Neighbor': list_of_neighbors[minIndex], 'Distance':minDistance} # initialize dict with default values


if __name__ == '__main__':

    # df = dataframe
    df = pd.read_csv('NationalParkGPSCoords.csv')# pandas dataframe of national parks and their coordinates

    # TODO: Break Park column into seperate columns: Name, City, State, Country
    # nameDf = df['Park'].str.split(',', expand = True)
    # print(nameDf.iloc[:,1:4])
    # Could shift rows over that have None instead of USA

    df['Coordinates'] = list(zip(df.Longitude, df.Latitude)) # GeoDataFrame needs shapely object, so create Coord tuple column
    df['Coordinates'] = df['Coordinates'].apply(Point) # Convert tuple to Point


    # TODO: re-implement Nearest Neighbor using List of Tuples as underlying datastructure
    # Place:
    # A Dictionary will represent a Place and contain {Name, Longitude, Latitude, Distance To Next Place in km}
    #
    # Route:
    # A List of Places is used to represent the Nearest Neighbor Route.
    # The indexes (i) of the Route will represent the order in which visitation should occur to replay the Route.
    # StartLocation: i = 0
    # EndLocation: i = len(Route)-1
    # The EndLocation will have Distance To Next Place = -1
    #
    # Unvisited Places:
    # A Set will represent the remaining unvisited Places. The set will be generated each time we visit a new location.
    # The set will use the same Place Tuple as mentioned above, and the Distance will be calculated.
    route = []
    unvisited = []

    # Initialize unvisited List
    for row in df.itertuples():
        place = {'Name':row.Name,
                 'Latitude':row.Latitude,
                 'Longitude':row.Longitude}
        unvisited.append(place)

    # Choose start location and prepare to solve
    currLocation = unvisited.pop(18)

    for i in range(len(unvisited)): # Use index loop because unvisited[] will be modified upon each iteration
        nearest = find_nearest(location=currLocation, list_of_neighbors=unvisited)
        currLocation.update( {'Distance': nearest['Distance']} ) # Add Distance to dictionary
        route.append(currLocation)
        del unvisited[nearest['Index']]
        currLocation = nearest['Neighbor']

    # Append final location with distance of 0
    currLocation.update( {'Distance': 0} ) # Add Distance to dictionary
    route.append(currLocation)


    # Merge results in original DataFrame
    dfRoute = pd.DataFrame(route)
    dfRoute['Visit_Order'] = dfRoute.index
    df = df.merge(dfRoute.set_index('Name'))
    df = df.sort_values('Visit_Order')
    print(df.loc[:,['Name','Visit_Order']])


    # Plot result on a geographical map
    gdf = geopandas.GeoDataFrame(df, geometry='Coordinates')
    # print(gdf.loc[:,['Name','Coordinates']]) # print all rows of Place Name and Coordinate columns only

    # Plot the coordinates over a country-level map
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    ax = world[world.continent == 'North America'].plot(color='white', edgecolor='black')  # restrict to North America
    ax.set_title('Shortest Path to US National Parks')
    gdf.plot(ax=ax, color='red')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Annotate the plot (looks terrible)
    # for idx,row in gdf.iterrows():
    #     plt.annotate(s=row.Park,
    #                  xy=(row.Longitude, row.Latitude),
    #                  xytext=(row.Longitude+1, row.Latitude+1),
    #                  horizontalalignment='center')

    plt.show()


    # TODO: Solve Traveling Salesman Problem (TSP) using Nearest Neighbor (NN) approach using a pre-computed distance matrix
    #distanceMatrix = create_distance_matrix_numpy(df)
    #print(distanceMatrix)


    #TODO: Animate routing solutions on geographical map

