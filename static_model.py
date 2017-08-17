import numpy as np
from gurobipy import *
import time
import pickle

def get_static_design(record,l,param,save_dir,dist_lb):
    # ignore those with less than (dist_lb) daily flows and less than 20 km
    edge_value = {}
    for key,value in record.iteritems():
        if value > dist_lb and l[key] > 20:
            edge_value[key] = value / 10000

    # filter the most important OD for later use
    epsilon = 0.01
    node_list = []
    for key,value in edge_value.iteritems():
        if key[0] not in node_list:
            node_list += [key[0]]
        if key[1] not in node_list:
            node_list += [key[1]]

    flag = False
    while flag == False:
        node_value = {}
        total_flow = 0
        for key,value in edge_value.iteritems():
            if key[0] in node_list and key[1] in node_list:
                node_value[key[0]] = value + node_value.get(key[0],0.0)
                node_value[key[1]] = value + node_value.get(key[1],0.0)
                total_flow += value
        key = min(node_value,key=node_value.get)
        if node_value.get(key,0.0) < epsilon * total_flow:
            node_list.remove(key)
        else:
            flag = True

    new_edge_value = {}
    for key,value in edge_value.iteritems():
        if key[0] in node_list and key[1] in node_list:
            new_edge_value[key] = value
    edge_value = new_edge_value

    print "node counts: {}".format(len(node_value))
    print "edge counts: {}".format(len(edge_value))

    edge_list = []
    for node1 in node_list:
        for node2 in node_list:
            if node1 != node2:
                edge_list += [(node1,node2)]
    d = edge_value
    n = len(d)
    max_value = sum(d.values())

    t = time.time()

    m = Model("Static")

    dn = {}
    for node in node_list:
        dn[node] = {}
    for key,value in d.iteritems():
        dn[key[0]][key[1]] = value

    c_a = {}
    x_a = {}
    f_a = {}
    y_a = {}
    c_ro = {}
    f_ro = {}
    y_ro = {}
    c_ra = {}
    f_ra = {}
    y_ra = {}
    for node in node_list:
        x_a[node] = m.addVar(vtype = GRB.BINARY)

    for edge in edge_list:
        y_a[edge] = m.addVar(vtype = GRB.BINARY)
        y_ra[edge] = m.addVar(vtype = GRB.BINARY)
        y_ro[edge] = m.addVar(vtype = GRB.BINARY)

        c_a[edge] = m.addVar(lb=0.0)
        c_ra[edge] = m.addVar(lb=0.0)
        c_ro[edge] = m.addVar(lb=0.0)

        for node in node_list:
            f_a[(edge,node)] = m.addVar(lb=0.0)
            f_ra[(edge,node)] = m.addVar(lb=0.0)
            f_ro[(edge,node)] = m.addVar(lb=0.0)

    m.update()

    for edge in edge_list:
        m.addConstr(y_a[edge] <= 0.5 * (x_a[edge[0]] + x_a[edge[1]]),'edge_aviation_{}_{}'.format(edge[0],edge[1]))
        m.addConstr(c_a[edge] <= max_value * y_a[edge],'bound_aviation_{}_{}'.format(edge[0],edge[1]))
        m.addConstr(c_ra[edge] <= max_value * y_ra[edge],'bound_rail_{}_{}'.format(edge[0],edge[1]))
        m.addConstr(c_ro[edge] <= max_value * y_ro[edge],'bound_road_{}_{}'.format(edge[0],edge[1]))

        m.addConstr(quicksum([f_a[(edge,node)] for node in node_list]) <= c_a[edge],
                    'capacity_aviation_{}_{}'.format(edge[0],edge[1]))
        m.addConstr(quicksum([f_ra[(edge,node)] for node in node_list]) <= c_ra[edge],
                    'capacity_rail_{}_{}'.format(edge[0],edge[1]))
        m.addConstr(quicksum([f_ro[(edge,node)] for node in node_list]) <= c_ro[edge],
                    'capacity_road_{}_{}'.format(edge[0],edge[1]))

    for node in node_list:
        in_edge_list = [edge for edge in edge_list if node == edge[1]]
        out_edge_list = [edge for edge in edge_list if node == edge[0]]
        for ori in node_list:
            if ori == node:
                # total balance for the start
                m.addConstr(quicksum(f_a[(edge,ori)] + f_ra[(edge,ori)] + f_ro[(edge,ori)] for edge in out_edge_list) ==
                            quicksum(f_a[(edge,ori)] + f_ra[(edge,ori)] + f_ro[(edge,ori)] for edge in in_edge_list) + \
                            sum(dn[ori].values()), 'demand_{}_{}'.format(node,ori))
            else:
                # total balance for other nodes
                m.addConstr(quicksum(f_a[(edge,ori)] + f_ra[(edge,ori)] + f_ro[(edge,ori)] for edge in in_edge_list) ==
                            quicksum(f_a[(edge,ori)] + f_ra[(edge,ori)] + f_ro[(edge,ori)] for edge in out_edge_list) + \
                            dn[ori].get(node,0.0), 'demand_{}_{}'.format(node,ori))
    m.update()

    print 'model setup time: {}'.format(time.time() - t)

    alpha = param['alpha']
    beta_ra = param['beta_ra']
    beta_ro = param['beta_ro']
    gamma_a = param['gamma_a']
    gamma_ra = param['gamma_ra']
    gamma_ro = param['gamma_ro']

    m.setObjective(quicksum(x_a[node] for node in node_list) * alpha + \
                   quicksum([((y_ra[edge] * beta_ra + y_ro[edge] * beta_ro) * l[edge]) for edge in edge_list]) + \
                   quicksum([((c_a[edge] * gamma_a + c_ra[edge] * gamma_ra + c_ro[edge] * gamma_ro) * l[edge]) for edge in edge_list]),
                   GRB.MINIMIZE)
    m.update()
    m.optimize()

    pickle.dump(x_a,open( save_dir + "x_a.p", "wb" ))
    pickle.dump(y_ra,open( save_dir + "y_ra.p", "wb" ))
    pickle.dump(y_ro,open( save_dir + "y_ro.p", "wb" ))
    pickle.dump(c_a,open( save_dir + "c_a.p", "wb" ))
    pickle.dump(c_ra,open( save_dir + "c_ra.p", "wb" ))
    pickle.dump(c_ro,open( save_dir + "c_ro.p", "wb" ))
