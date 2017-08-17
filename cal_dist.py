from math import radians, cos, sin, asin, sqrt
import numpy as np
import pickle
import json

city_dict = json.load(open('city_back.txt'))
code = pickle.load(open( "code.p", "rb" ))
lat = pickle.load(open( "lat.p", "rb" ))
lon = pickle.load(open( "lon.p", "rb" ))

def distance(lat1, lon1, lat2, lon2):
    R = 6378.137
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    a = sin((lat2 - lat1) / 2.0) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2.0) ** 2
    return 2 * R * asin(sqrt(a))

od_dist = {}
city = code.keys()
for city1 in city:
    for city2 in city:
        if city1 != city2:
            od_dist[(code[city1],code[city2])] = sqrt((lat[city1] - lat[city2]) ** 2 + (lon[city1] - lon[city2]) ** 2)
            
pickle.dump( od_dist, open( "od_dist.p", "wb" ) )    