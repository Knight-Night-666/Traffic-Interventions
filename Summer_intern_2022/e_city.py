#!/usr/bin/env python

from operator import truediv
import os
import sys
import optparse
import pandas as pd
import networkx as nx

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  # Checks for the binary in environ vars
import traci

dir_name = input("Enter the intervention name :- ")
csv_file = dir_name + "/plain.edg.csv"
sumocfg = dir_name + "/osm.sumocfg"
tripInfo = "outputs/"+dir_name+"/Before_intervention/TripDetails_before.xml"
command_file = dir_name + "/command.sh"
net_file = dir_name + "/osm.net.xml"

# os.system("bash "+ command_file)


def getConnectedComponent():
    df = pd.read_csv(csv_file, sep=";",engine='python')
    df = df.drop_duplicates(subset=["edge_id"],keep=False)
    adj_list = {}
    x = len(df)
    for i in range(x):
        val = df.iloc[i]
        if( val["edge_from"] in adj_list):
            adj_list[val["edge_from"]].append(val["edge_to"])
    
        else:
            adj_list[val["edge_from"]] = [val["edge_to"]]
        
    G = nx.DiGraph(adj_list)
    return G

def getNumberOfConnectedComponents(G):
    g = nx.number_strongly_connected_components(G) 
    return g

G = getConnectedComponent()
G1 = G.copy()

def check_edge(a):
    df = pd.read_csv(csv_file ,sep=";",engine='python')
    df = df.drop_duplicates(subset=["edge_id"],keep=False)    
    df = df.set_index("edge_id")
    edges = list(df.index)
    if a not in edges:
        return False
    
    val = df.loc[a]
    edge_from = val["edge_from"]
    edge_to = val["edge_to"]
    res = G.has_edge(edge_from,edge_to)
    
    if(not res):
        return False
    
    G_copy = G.copy()
    G_copy.remove_edge(edge_from,edge_to)
    
    if(getNumberOfConnectedComponents(G) == getNumberOfConnectedComponents(G_copy)):
        res = True
        G.remove_edge(edge_from,edge_to)
    
    else:
        res = False
    return res


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

def getEdgeId(node_from,node_to):
    df = pd.read_csv(csv_file,sep=";",engine='python')
    df = df.drop_duplicates(subset=["edge_id"],keep=False)

    df = df.set_index("edge_id")
    edges = df.index
    l = []
    for i in edges:
        val = df.loc[i]
        if(node_from  == val['edge_from']and node_to == val['edge_to']):
            l.append(i)
    return l


def getEdgeBetweenCentrality():
    ls = nx.edge_betweenness_centrality(G1)
    dic = {}
    for i in ls.keys():
        e = getEdgeId(i[0],i[1])
        val = ls[i]
        dic[e[0]] = val
    
    return dic


def check(arr,str1):
    flag=0
    for i in arr:
        if(i==str1):
            flag=1
    if(flag==1):
        return True
    else:
        return False

# contains TraCI control loop
def run():
    step = 0
    flag = 0
    traffic_diff_sort=[]
    traffic_diff={}
    roads_posi=[]
    roads_negi=[]
    finals=[]
    edg_lst=traci.edge.getIDList()
    
    for i in edg_lst:
        # print(i)
        if(i[0]!='-'):
            roads_posi.append(i)
        if(i[0]=='-'):
            roads_negi.append(i)
    

    for rd in roads_negi:
        road_pos = rd[1:]
        if(check(roads_posi,road_pos)):
            traffic_diff[road_pos]=0
            
    while step<=3600:
        traci.simulationStep()

        if(step%100==0):

            for rd in roads_negi:
                road_pos = rd[1:]
                if(check(roads_posi,road_pos)):
                    traffic_1=traci.edge.getLastStepVehicleNumber(rd)
                    traffic_2=traci.edge.getLastStepVehicleNumber(road_pos)
                    traffic_diff[road_pos]+=(traffic_1-traffic_2)
                    flag += 1
        step += 1
   
    for rd in roads_negi:
        road_pos = rd[1:]
        if(check(roads_posi,road_pos)):
            traffic_diff[road_pos]/=flag 
            if(traffic_diff[road_pos]>0):
                str1 = 'positive'
            else:
                str1 = 'negative'
            traffic_diff_sort.append((abs(traffic_diff[road_pos]),road_pos,str1))

    traffic_diff_sort.sort(key=lambda e: e[0],reverse=True)

    i=0
    while(len(finals)<5):
        if(check_edge(traffic_diff_sort[i][1])):
            finals.append((traffic_diff_sort[i][0],traffic_diff_sort[i][1],traffic_diff_sort[i][2]))
        i+=1
    
    f = open("outputs/" + dir_name +"/Before_intervention/output.txt","w")
    j=0
    centralities = getEdgeBetweenCentrality()
    while(j<5):
        f.write('ID of the edge to be made oneway: ' + finals[j][1] + '\n')
        txt = 'Traffic flow difference: '
        f.write(txt)
        f.write('{}'.format(finals[j][0]))
        f.write('\nTraffic flow direction: ' + finals[j][2]+ '\n')
        f.write('\n')
        j+=1    

    traci.close()
    sys.stdout.flush()


# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", sumocfg,
                             "--statistic-output", tripInfo])                       
    run()
