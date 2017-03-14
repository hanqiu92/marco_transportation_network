import pickle

code = pickle.load(open( "code.p", "rb" ))

# aggregate to whole dataset
total_in_data = {}
for i in xrange(12):
    temp = pickle.load(open( "data/in_"+str(i+1)+".p", "rb" ))
    for key,value in temp.iteritems():
        total_in_data[key] = value
temp = pickle.load(open( "data/in_11_2016.p", "rb" ))
for key,value in temp.iteritems():
    total_in_data[key] = value
pickle.dump( total_in_data, open( "data/in_total.p", "wb" ) )

total_out_data = {}
for i in xrange(12):
    temp = pickle.load(open( "data/out_"+str(i+1)+".p", "rb" ))
    for key,value in temp.iteritems():
        total_out_data[key] = value
temp = pickle.load(open( "data/out_11_2016.p", "rb" ))
for key,value in temp.iteritems():
    total_out_data[key] = value
pickle.dump( total_out_data, open( "data/out_total.p", "wb" ) )

# transform shape
record_total = {}
for key,value in in_total.iteritems():
    temp = {}
    for item in value:
        if item:
            if item[0] in code:
                d = code[item[0]]
            else:
                d = -1
            if item[1] in code:
                o = code[item[1]]
            else:
                o = -1
            temp[(o,d)] = item[2]
    record_total[key] = temp
for key,value in out_total.iteritems():
    temp = record_total[key]
    for item in value:
        if item:
            if item[0] in code:
                o = code[item[0]]
            else:
                o = -1
            if item[1] in code:
                d = code[item[1]]
            else:
                d = -1
            if (o,d) in temp:
                temp[(o,d)] = (item[2] + temp[(o,d)]) / 2
            else:
                temp[(o,d)] = item[2]
    record_total[key] = temp   
    
# process missing value
for key,value in record_total.iteritems():
    for key1 in value.keys():
        if (key1[1],key1[0]) in value:
            temp = (value[key1] + value[(key1[1],key1[0])]) / 2
            value[key1] = temp
            value[(key1[1],key1[0])] = temp
        else:
            value[(key1[1],key1[0])] = value[key1]         
pickle.dump( record_total, open( "data/record_total.p", "wb" ) ) 

record_agg_year = {}
for key,value in record_total.iteritems():
    if key >= 20151201:
        for key1 in value:
            if key1 in record_agg_year:
                record_agg_year[key1] += value[key1]
            else:
                record_agg_year[key1] = value[key1]
pickle.dump( record_agg_year, open( "data/record_agg_year.p", "wb" ) ) 

record_agg_month = {}
for i in xrange(12):
    record_agg_month[i+1] = {}
for key,value in record_total.iteritems():
    if key >= 20151201:
        month = (key / 100) % 100
        for key1 in value:
            if key1 in record_agg_month[month]:
                record_agg_month[month][key1] += value[key1]
            else:
                record_agg_month[month][key1] = value[key1]
pickle.dump( record_agg_month, open( "data/record_agg_month.p", "wb" ) )                 
            