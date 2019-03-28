import csv;
import sys;
from geopy.distance import geodesic;

class Place: # A type of Linked List Node that also has coordinate and distance information
    def __init__(self, name=None, lat=None, long=None):
        self.name = name
        self.lat = lat
        self.long = long

        self.nextPlace = None
        self.nearestDistance = sys.maxint


class Route: # A Linked List comprised of places
    def __init__(self):
        self.headval = None
        self.tailval = None
        self.length = 0

    def listprint(self):
        printval = self.headval
        while printval is not None:
            print (printval.name, printval.lat, printval.long)
            printval = printval.nextPlace

if __name__ == '__main__':

    parks = [] # List of Tuples(Park Name, Long, Lat, Nearest Park)

    shortestRoute = Route()
    # Load CSV of National Park Coordinates
    with open('C:\Users\Josh\Desktop\Python\National Parks Info - National Parks GPS Coords.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            parks.append((row[0],row[1], row[2]))
            #print(row[0],row[1],row[2],)


    #print parks[1][0] # Place Name
    #print parks[1][1] # Latitude
    #print parks[1][2] # Longitude

    # add the first place as the head of the Linked List
    shortestRoute.headval = Place(name = parks[1][0], lat=parks[1][1], long=parks[1][2])
    shortestRoute.tailval = shortestRoute.headval
    shortestRoute.length = 1
    nearestParkIndex = 0
    parks[nearestParkIndex] = None


    while shortestRoute.length <= parks.__len__():
        # Initialize loop
        nearestPark = None
        nearestParkDistance = sys.maxint

        # Iterate through all parks and find the nearest park to the current tail of the Route
        for currPark in parks:

            if shortestRoute.length is parks.__len__(): # We are done if all of the parks have been used
                break

            if currPark is not None: # Ignore parks we've already added to the route

                # Find distance between Route Tail and currPark
                # currPark[1] = Latitude
                # currPark[2] = Longitude
                currDist = geodesic( (shortestRoute.tailval.lat, shortestRoute.tailval.long), (currPark[1],currPark[2]) )

                #print currDist

                if nearestPark is None: # Initial Condition: The first park is always the nearest
                    nearestPark = currPark
                    nearestParkDistance = currDist
                    next

                if currDist < nearestParkDistance: # We found a nearer park than previously discovered
                    nearestPark = currPark
                    nearestParkDistance = currDist
                    nearestParkIndex = currPark.index()

        # TODO: Need outer loop here to iterate until we run out of new parks
        # Each iteration, append nearestPark to shortestRoute.tailval
        parks[nearestParkIndex] = None # Remove the nearest park from the possible parks
        shortestRoute.headval.nextPlace = shortestRoute.tailval
        shortestRoute.tailval = Place(nearestPark[0], nearestPark[1], nearestPark[2]) # Add reference to nearest place

    # Traverse parks and find distance to all other parks, keep track of shortest park name until we get to the end.
    # When we reach the end, mark the park as used so

    shortestRoute.listprint()



