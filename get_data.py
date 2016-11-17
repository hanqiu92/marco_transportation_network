import requests
from ast import literal_eval
import json
import time
import pickle

city_dict = json.load(open('city_back.txt'))
city_num = len(city_dict)

def get(city,date,city_dict):
    url='http://lbs.gtimg.com/maplbs/qianxi/'+str(date)+'/'+str(city)+'.js'
    params={'callback':'JSONP_LOADER'}
    res=requests.get(url,params)
    if res.status_code == 200:
        result = res.text[26:]
        result = literal_eval(result)
        for i in xrange(len(result)):
            # append current city name
            result[i].insert(0,city / 100)
            # parse the other city
            city_name = unicode(result[i][1],'utf-8')
            if city_name in city_dict:
                result[i][1] = city_dict[city_name][2]
            else:
                print city, city_name
        return result
    return []

def get_by_date(date,city_dict):
    in_record = [0] * len(city_dict) * 10
    out_record = [0] * len(city_dict) * 10
    n = 0
    for value in city_dict.values():
        city = value[2]
        #in
        temp_in_record = get(city * 100 + 6,date,city_dict)
        if temp_in_record:
            for i in xrange(len(temp_in_record)):
                in_record[10 * n + i] = temp_in_record[i]
        else:
            for i in xrange(10):
                in_record[10 * n + i] = []
        # out
        temp_out_record = get(city * 100 + 16,date,city_dict)
        # update
        if temp_out_record:
            for i in xrange(len(temp_out_record)):
                out_record[10 * n + i] = temp_out_record[i]
        else:
            for i in xrange(10):
                out_record[10 * n + i] = []
        # count
        n += 1
    return in_record,out_record

def get_by_month(year,month,city_dict):
    total_in_record = {}
    total_out_record = {}
    if month in [1,3,5,7,8,10,12]:
        days = 31
    elif month in [4,6,9,11]:
        days = 30
    elif month == 2:
        days = 29
    for day in xrange(days):
        t = time.time()
        date = year * 10000 + month * 100 + day + 1
        out = get_by_date(date,city_dict)
        total_in_record[date] = out[0]
        total_out_record[date] = out[1]
        print date,', time: ',time.time() - t

    pickle.dump( total_in_record, open( "in_"+str(month)+".p", "wb" ) )
    pickle.dump( total_out_record, open( "out_"+str(month)+".p", "wb" ) )

year = 2016
for m in xrange(8):
    month = m + 3
    get_by_month(year,month,city_dict)
