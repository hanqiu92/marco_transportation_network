import pickle

def process_by_month(year,month):
    total_in_record = {}
    total_out_record = {}
    if month in [1,3,5,7,8,10,12]:
        days = 31
    elif month in [4,6,9,11]:
        days = 30
    elif month == 2:
        days = 29
    for day in xrange(days):
        date = year * 10000 + month * 100 + day + 1
        temp_in = pickle.load( open( "in_"+str(date)+".p", "rb" ) )
        temp_out = pickle.load( open( "out_"+str(date)+".p", "rb" ) )
        total_in_record[date] = temp_in
        total_out_record[date] = temp_out

    pickle.dump( total_in_record, open( "in_"+str(month)+".p", "wb" ) )
    pickle.dump( total_out_record, open( "out_"+str(month)+".p", "wb" ) )

year = 2016
for m in xrange(1):
    month = m + 5
    process_by_month(year,month)
