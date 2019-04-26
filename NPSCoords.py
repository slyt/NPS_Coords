import csv
import sys
import random
import pandas as pd
import numpy as np
import geopandas
from shapely.geometry import Point
import matplotlib.pyplot as plt
from geopy.distance import geodesic


class Place: # A type of Linked List Node that also has coordinate and distance information
    def __init__(self, name=None, lat=None, long=None):
        self.name = name
        self.lat = lat
        self.long = long

        self.nextPlace = None
        self.nearestDistance = -1
        self.index = -1

    def distance_to(self, destination):
        # Find distance between Route Tail and currPark
        # currPark[1] = Latitude
        # currPark[2] = Longitude
        return geodesic((self.lat, self.long), (destination.lat, destination.long))


class Route: # A Linked List comprised of places
    def __init__(self):
        self.headval = None
        self.tailval = None
        self.length = 0

    def listprint(self):
        printval = self.headval
        count = 0
        while printval is not None:
            print (count, printval.name, printval.lat, printval.long, printval.nearestDistance)
            printval = printval.nextPlace
            count = count + 1

    def listprint_csv(self):
        # Index is the original index in the initial dataframe
        print('Index,', 'Name,', 'Latitude,', 'Longitude,', 'Distance to Next Place (km)')
        printval = self.headval

        while printval is not None:
            print (printval.index, ',',
                    printval.name.replace(',', ''), ',',
                   printval.lat, ',',
                   printval.long, ',',
                   str(printval.nearestDistance).replace('km',''))
            printval = printval.nextPlace

    def convert_to_dataframe(self):
        df = pd.DataFrame(columns=['Index','Name','Distance_To_Next_km'])
        convertval = self.headval
        for i in range(self.length):
            df.loc[i]=[convertval.index,
                      convertval.name,
                      str(convertval.nearestDistance).replace('km', '')]
            convertval = convertval.nextPlace
        return df

    def add_place(self, place):

        if self.headval is None: # if empty route, add starting place
            self.headval = place
            self.tailval = place

        else: # update tail value to point to the new place
            self.tailval.nextPlace = place
            self.tailval = place
        self.length = self.length + 1


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



if __name__ == '__main__':

    # df = dataframe
    df = pd.read_csv('NationalParkGPSCoords.csv')# pandas dataframe of national parks and their coordinates
    df['Coordinates'] = list(zip(df.Longitude, df.Latitude)) # GeoDataFrame needs shapely object, so create Coord tuple column
    df['Coordinates'] = df['Coordinates'].apply(Point) # Convert tuple to Point
    gdf = geopandas.GeoDataFrame(df, geometry='Coordinates')

    gdf['Visited'] = False # append Visited column and initialize to false
    gdf['Distance to Next'] = -1
    gdf['Visitation Index'] = -1 # Keep track of the order in which we visit each place for replay at the end
    #print(gdf.loc[:,['Name','Coordinates']]) # print all rows of Place Name and Coordinate columns only

    # Plot the coordinates over a country-level map
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    ax = world[world.continent == 'North America'].plot(color='white', edgecolor='black') # restrict to North America
    ax.set_title('Shortest Path to US National Parks')
    gdf.plot(ax=ax, color='red')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    for idx,row in gdf.iterrows():
        plt.annotate(s=row.Name,
                     xy=(row.Longitude, row.Latitude),
                     xytext=(row.Longitude+1, row.Latitude+1),
                     horizontalalignment='center')
    #plt.show()


    # Solve Traveling Salesman Problem (TSP) using Nearest Neighbor (NN) approach using a pre-computed distance matrix
    distanceMatrix = create_distance_matrix_numpy(df)
    print(distanceMatrix)


    # Solve Traveling Salesman Problem (TSP) using Nearest Neighbor (NN) approach and a Linked List datastructure
    # Initialize data
    parks = []
    shortestRoute = Route()
    for idx,row in gdf.iterrows():
        currPlace = Place()
        currPlace.name = row.Name
        currPlace.lat = row.Latitude
        currPlace.long = row.Longitude
        currPlace.index = idx
        parks.append(currPlace)

    # TODO: Add user input to select starting point
    # Add the first place as the head of the Linked List
    startingPlace = parks[0] # Start at the first park in the CSV
    # startingPlace = random.choice(parks) # Choose a random starting place
    shortestRoute.add_place(startingPlace)

    # Compute until we have processed all of the parks.
    while parks.__len__() is not 0:
        # Initialize loop
        nearestPark = None
        nearestParkDistance = -1

        # Iterate through all parks and find the nearest park to the current tail of the Route
        for currPark in parks:

            if shortestRoute.length is parks.__len__()+1:  # We are done if all of the parks have been used
                break

            if currPark is None:  # This park has already been added to the Route and should be skipped
                continue

            # Find distance between Route Tail and currPark
            currDist = shortestRoute.tailval.distance_to(currPark)

            if nearestPark is None:  # Initial Condition: The first park is always the nearest
                nearestPark = currPark
                nearestParkDistance = currDist
                next

            if nearestParkDistance is not -1 and currDist < nearestParkDistance:  # We found a nearer park than previously discovered
                nearestPark = currPark
                nearestParkDistance = currDist

# TODO: Use Route.add_place() below so that length of route is updated. Then we can iterate over the route to convert to dataframe
        # Update ShortestRoute with the nearest Park
        parks.remove(nearestPark)  # Remove the nearest park from the possible parks
        shortestRoute.tailval.nextPlace = nearestPark  # Point last place to the nearest place
        shortestRoute.tailval.nearestDistance = currDist
        shortestRoute.tailval = nearestPark  # Make the nearest place the last place

    # Print the Nearest Neighbor solution to TSP
    #shortestRoute.listprint()
    #shortestRoute.listprint_csv()
    #print(shortestRoute.convert_to_dataframe())



