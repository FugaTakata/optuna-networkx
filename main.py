from networkx.algorithms.shortest_paths import weighted
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import optuna
import requests
import json

# import data
import d

np.random.seed(10)

G = nx.Graph()

url = 'http://localhost:3000/api/n'

nodes = []
edges = []
for node in d.d['nodes']:
    # nodes.append((node['id'], {'name': node['name']}))
    nodes.append((node['id'], {'name': node['id']}))
for edge in d.d['links']:
    # edges.append((edge['source']['id'], edge['target']['id']))
    edges.append((edge['source'], edge['target']))

G.add_nodes_from(nodes)
G.add_edges_from(edges)

path = {}

for ns in nodes:
    path[ns[0]] = {}
    for nt in nodes:
        if nx.has_path(G, source=ns[0], target=nt[0]):
            p = nx.shortest_path_length(G,  source=ns[0], target=nt[0])
            path[ns[0]][nt[0]] = p

print(path)


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
            # if nx.has_path(g, source=kj, target=ki):
            if ki in path and kj in path[ki]:
                # dij = nx.shortest_path_length(
                #     g,
                #     source=kj,
                #     target=ki,
                # )
                dij = path[ki][kj]
                e = (norm - dij)
                s += e ** 2
    return s


def objective(trial):
    # k = trial.suggest_float('k', 0, 1)
    # i = trial.suggest_int('i', 50, 200)
    # pos = nx.spring_layout(G, iterations=i, threshold=1e-4, k=k)

    c = trial.suggest_float('c', -2, 2)
    x = trial.suggest_float('x', 0, 2)
    y = trial.suggest_float('y', 0, 2)

    print(url + f'?c={c}&x={x}&y={y}')
    res = requests.get(url + f'?c={c}&x={x}&y={y}')
    obj = json.loads(res.text)
    pos = {}
    for d in obj['nodes']:
        pos[d['id']] = [d['x'] / 1000,  d['y']/1000]
        # pos[d['id']] = [d['x'],  d['y']]
    return stress(pos, G)


study = optuna.create_study()
study.optimize(objective, n_trials=59)

best_params = study.best_params
fc = best_params['c']
fx = best_params['x']
fy = best_params['y']

print(f'found c: {fc}, found x: {fx}, found y: {fy}')


# found_pos = nx.spring_layout(G, iterations=found_i, threshold=1e-4, k=found_k)
res = requests.get(url + f'?c={fc}&x={fx}&y={fy}')
obj = json.loads(res.text)
# print(obj)
fpos = {}
for d in obj['nodes']:
    fpos[d['id']] = [d['x'] / 1000,  d['y']/1000]
    # fpos[d['id']] = [d['x'],  d['y']]
nx.draw(G, pos=fpos)


plt.show()
