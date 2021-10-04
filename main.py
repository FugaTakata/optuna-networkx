from networkx.algorithms.shortest_paths import weighted
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import optuna

import data

np.random.seed(10)

G = nx.Graph()

nodes = []
edges = []
for node in data.data['nodes']:
    nodes.append((node['id'], {'name': node['name']}))
for edge in data.data['links']:
    edges.append((edge['source'], edge['target']))

G.add_nodes_from(nodes)
G.add_edges_from(edges)


def stress(pos, g):
    keys = list(pos.keys())
    n = len(keys)
    s = 0
    for j in range(1, n):
        for i in range(n):
            kj = keys[j]
            ki = keys[i]
            dx = pos[ki][0] - pos[kj][0]
            dy = pos[ki][1] - pos[kj][1]
            norm = (dx ** 2 + dy ** 2) ** 0.5
            if ki != kj and nx.has_path(g, source=kj, target=ki):
                dij = nx.shortest_path_length(
                    g,
                    source=kj,
                    target=ki,
                    weight='length')
                print(dij)
                e = (norm - dij) / dij
                s += e ** 2
    return s


def objective(trial):
    k = trial.suggest_float('k', 0, 1)
    pos = nx.spring_layout(G, iterations=50, threshold=1e-4, k=k)
    TG = nx.Graph()

    TG.add_nodes_from(nodes)
    for (s, t) in edges:
        l = ((pos[s][0] - pos[t][0]) ** 2 +
             (pos[s][1] - pos[t][1]) ** 2) ** 0.5
        TG.add_edge(s, t, length=l)

    return stress(pos, TG)


study = optuna.create_study()
study.optimize(objective, n_trials=200)

best_params = study.best_params
found_k = best_params['k']

print(f'found k: {found_k}')


found_pos = nx.spring_layout(G, iterations=50, threshold=1e-4, k=found_k)
nx.draw(G, pos=found_pos)


plt.show()
