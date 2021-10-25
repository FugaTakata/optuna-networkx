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
    for i in range(0, n):
        for j in range(i + 1, n):
            ki = keys[i]

            kj = keys[j]
            dx = pos[ki][0] - pos[kj][0]
            dy = pos[ki][1] - pos[kj][1]
            norm = (dx ** 2 + dy ** 2) ** 0.5
            if nx.has_path(g, source=kj, target=ki):
                dij = nx.shortest_path_length(
                    g,
                    source=kj,
                    target=ki,
                )
                e = (norm - dij)
                s += e ** 2
    return s


def objective(trial):
    k = trial.suggest_float('k', 0, 1)
    i = trial.suggest_int('i', 50, 200)
    pos = nx.spring_layout(G, iterations=i, threshold=1e-4, k=k)

    return stress(pos, G)


study = optuna.create_study()
study.optimize(objective, n_trials=200)

best_params = study.best_params
found_k = best_params['k']
found_i = best_params['i']

print(f'found k: {found_k}, found i: {found_i}')


found_pos = nx.spring_layout(G, iterations=found_i, threshold=1e-4, k=found_k)
nx.draw(G, pos=found_pos)


plt.show()
