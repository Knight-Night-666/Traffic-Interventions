import pandas as pd
import networkx as nx

csv_file = "./high_traffic/plain.edg.csv"

def getConnectedComponent():
    df = pd.read_csv(csv_file,sep=';',engine='python')
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

def check_edge(a):
    df = pd.read_csv(csv_file,sep=";",engine='python')
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

def maxKCentrality(k):
    values = nx.edge_betweenness_centrality(G)
    copy = values
    lis = []
    while len(lis) < k:
        max_val = max(copy,key = copy.get)
        # print(len(copy))
        a = getEdgeId(max_val[0],max_val[1])
        # print(a)
        if(check_edge(a[0])):
            lis.append(max_val)
        copy.pop(max_val)

    return lis

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

result = {}
k = 1
# G = getConnectedComponent()
f= open("outputs/centrality/before_intervention/output.txt","w")
for i in maxKCentrality(5):
    val = getEdgeId(i[0],i[1])
    result[k] = val
    k = k+1
    
for i in result.values():
    f.write(i[0] + "\n")