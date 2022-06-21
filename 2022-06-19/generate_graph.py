import json

import networkx as nx

EDGE_WEIGHT = 30

G = nx.scale_free_graph(200)

G = nx.Graph(G)
G.remove_edges_from(list(nx.selfloop_edges(G)))

weighted_edges = []
for e in G.edges:
    weighted_edges.append((e[0], e[1], EDGE_WEIGHT))

G.remove_edges_from(list(G.edges))
G.add_weighted_edges_from(weighted_edges)

largest_cc = max(nx.connected_components(G), key=len)
LG = G.subgraph(largest_cc)

node_link_data = nx.node_link_data(LG)

with open('generated_graph.json', mode='w') as f:
    json.dump(node_link_data, f, ensure_ascii=False)
