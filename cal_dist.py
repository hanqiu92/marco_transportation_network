from math import cos, sin, asin, sqrt
import numpy as np
import pickle
import json

city_dict = json.load(open('city_back.txt'))
code = pickle.load(open( "code.p", "rb" ))
lat = pickle.load(open( "lat.p", "rb" ))
lon = pickle.load(open( "lon.p", "rb" ))

def distance(lat1, lon1, lat2, lon2):
    R = 6378.137
    p = math.pi / 180.0
    a = sin((lat2 - lat1) * p) ** 2 + cos(lat1 * p) * cos(lat2 * p) * sin((lon2 - lon1) * p) ** 2
    return 2 * R * asin(sqrt(a))

od_dist = {}
city = code.keys()
for city1 in city:
    for city2 in city:
        if city1 != city2:
            od_dist[(code[city1],code[city2])] = sqrt((lat[city1] - lat[city2]) ** 2 + (lon[city1] - lon[city2]) ** 2)
            
pickle.dump( od_dist, open( "od_dist.p", "wb" ) )    