import csv
import sys
import random
import pandas as pd
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
        self.nearestDistance = sys.maxsize

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
        while printval is not None:
            print (printval.name, printval.lat, printval.long, printval.nearestDistance)
            printval = printval.nextPlace

    def listprint_csv(self):
        print('Name,', 'Latitude,', 'Longitude,', 'Distance to Next Place (km)')
        printval = self.headval

        while printval is not None:
            print (printval.name.replace(',', ''), ',',
                   printval.lat, ',',
                   printval.long, ',',
                   str(printval.nearestDistance).replace('km',''))
            printval = printval.nextPlace

    def add_place(self, place):

        if self.headval is None: # if empty route, add starting place
            self.headval = place
            self.tailval = place

        else: # update tail value to point to the new place
            self.tailval.nextPlace = place
            self.tailval = place
        self.length = self.length + 1







if __name__ == '__main__':

    # df = dataframe
    df = pd.read_csv('NationalParkGPSCoords.csv')# pandas dataframe of national parks and their coordinates
    df['Coordinates'] = list(zip(df.Longitude, df.Latitude)) # GeoDataFrame needs shapely object, so create Coord tuple column
    df['Coordinates'] = df['Coordinates'].apply(Point) # Convert tuple to Point
    gdf = geopandas.GeoDataFrame(df, geometry='Coordinates')

    gdf['Visited'] = False # append Visited column and initialize to false
    gdf['Distance to Next'] = -1
    gdf['Visitation Index'] = -1 # Keep track of the order in which we visit each place for replay at the end
    print(gdf.loc[:,['Name','Coordinates']]) # print all rows of Place Name and Coordinate columns only

    # plot the coordinates over a country-level map
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    print(world.columns)
    print(world.iloc[:, 0:3])

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

    plt.show()


    currentLocation = 0 # Index of the starting location
    gdf.loc[currentLocation, 'Visited'] = True
    gdf.loc[currentLocation, 'Visitation Index'] = 0
    #print(pp)
    for row in df.itertuples(index=True, name='Pandas'): # row is a tuple
        if getattr(row, 'Visited') is False:
            # find distance between currentLocation and row
            # keep track of NearestNeighbor index

            print(row[0])



    parks = [] # List of Places

    shortestRoute = Route()
    # Load CSV of National Park Coordinates
    with open('NationalParkGPSCoords.csv', encoding="utf8") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        next(readCSV) # skip CSV header: Place Name, Latitude, Longitude
        for row in readCSV:
            currPlace = Place()
            currPlace.name = row[0]
            currPlace.lat = row[1]
            currPlace.long = row[2]
            parks.append(currPlace)

    # TODO: Add user input to select starting point
    # Add the first place as the head of the Linked List
    startingPlace = parks[0] # Start at the first park in the CSV
    # startingPlace = random.choice(parks) # Choose a random starting place
    shortestRoute.add_place(startingPlace)

    # Compute until we have processed all of the parks.
    while shortestRoute.length <= parks.__len__():
        # Initialize loop
        nearestPark = None
        nearestParkDistance = sys.maxsize

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

            if currDist < nearestParkDistance:  # We found a nearer park than previously discovered
                nearestPark = currPark
                nearestParkDistance = currDist

        # Update ShortestRoute with the nearest Park
        parks.remove(nearestPark)  # Remove the nearest park from the possible parks
        shortestRoute.tailval.nextPlace = nearestPark  # Point last place to the nearest place
        shortestRoute.tailval.nearestDistance = currDist
        shortestRoute.tailval = nearestPark  # Make the nearest place the last place

    # Print Result
    #shortestRoute.listprint()
    #shortestRoute.listprint_csv()


## TODO: Plot points on map

