import pickle
from static_model import get_static_design

save_dir_static = "result/static/"
save_dir_robust = "result/robust/"

od_dist = pickle.load(open( "od_dist.p", "rb" ))
record_agg_year = pickle.load(open( "data/record_agg_year.p", "rb" ))
record_all = pickle.load(open( "data/record_total.p", "rb" ))

record_ave = {}
for od,value in record_agg_year.iteritems():
    if -1 not in od:
        record_ave[od] = value / 365.0

record_max = {}
od_pair_raw = set()
for _,record_daily in record_all.iteritems():
    for od,value in record_daily.iteritems():
        if -1 not in od:
            record_max[od] = max(record_max.get(od,-1),value)

param = {'alpha':500, 'beta_ra':250, 'beta_ro':100, 'gamma_a':10, 'gamma_ra':3, 'gamma_ro':10}

print "static model:"
get_static_design(record_ave,od_dist,param,save_dir_static,10000.0)
print "robust model:"
get_static_design(record_max,od_dist,param,save_dir_robust,10000.0)

