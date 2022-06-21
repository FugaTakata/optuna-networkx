import json

import networkx as nx
import py4cytoscape as p4c
import optuna
import matplotlib.pyplot as plt
import numpy as np

LAYOUT_NAME = 'kamada-kawai'
# LAYOUT_NAME = 'fruchterman-rheingold'
N_TRIALS = 100

K_FROM = 2
K_TO = 2
k_range = range(K_FROM, K_TO + 1)

EDGE_WEIGHT = 30

np.random.seed(1)

shape_based_values = {}


def get_shortest_paths(G):
    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G))
    # shortest_paths = dict(nx.all_pairs_shortest_path_length(G))
    return shortest_paths


def get_coordinates():
    coordinates = []
    for index, row in p4c.get_node_position().iterrows():
        coordinates.append(row.to_dict())

    return coordinates


def get_average_degree(G):
    s = 0
    for n in G.nodes:
        s += G.degree[n]
    return s / len(G.nodes)


def get_props(trial):
    if LAYOUT_NAME == 'kamada-kawai':
        props = {'m_averageIterationsPerNode': trial.suggest_float('m_averageIterationsPerNode', 0, 150),
                 'm_nodeDistanceStrengthConstant': trial.suggest_float('m_nodeDistanceStrengthConstant', 0, 50),
                 'm_nodeDistanceRestLengthConstant': trial.suggest_float('m_nodeDistanceRestLengthConstant', 0, 100),
                 'm_disconnectedNodeDistanceSpringStrength': trial.suggest_float('m_disconnectedNodeDistanceSpringStrength', 0, 1),
                 'm_disconnectedNodeDistanceSpringRestLength': trial.suggest_float('m_disconnectedNodeDistanceSpringRestLength', 0, 10000),
                 'm_anticollisionSpringStrength': trial.suggest_float('m_anticollisionSpringStrength', 0, 1),
                 'm_layoutPass': 0,
                 'singlePartition': False,
                 'unweighted': False,
                 'randomize': False
                 }

    elif LAYOUT_NAME == 'fruchterman-rheingold':
        props = {
            "update_iterations": 0,
            "attraction_multiplier": trial.suggest_float("attraction_multiplier", 0, 0.03 * 2),
            "repulsion_multiplier": trial.suggest_float("repulsion_multiplier", 0, 0.04 * 2),
            "gravity_multiplier": trial.suggest_float("gravity_multiplier", 0, 1 * 2),
            "conflict_avoidance": trial.suggest_float("conflict_avoidance", 0, 20 * 2),
            "max_distance_factor": trial.suggest_float("max_distance_factor", 0, 20 * 2),
            "spread_factor": trial.suggest_float("spread_factor", 0, 2 * 2),
            "temperature": trial.suggest_float("temperature", 0, 80 * 2),
            "nIterations": 500,
            "singlePartition": False,
            "layout3D": False,
            "randomize": False,
        }

    return props


def show_k_nearest(average_degree):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('k')
    ax.set_ylabel('shape_based_v')
    ax.grid(True)

    for k in k_range:
        k_str = str(k)
        n = len(shape_based_values[k_str])
        ax.scatter([k] * n, shape_based_values[k_str])

    print(f"average_degree={average_degree}")

    plt.savefig(
        f'images/k-nearest_distribution_{K_FROM}-{K_TO}_{LAYOUT_NAME}_average_degree={average_degree}.png')
    plt.show()


def calc_distance(sx, sy, tx, ty):
    dx = sx - tx
    dy = sy - ty
    distance = (dx ** 2 + dy ** 2) ** 0.5

    return distance


def k_nearest(coordinates, K):
    G = nx.DiGraph()
    n = len(coordinates)

    distances = []
    for si, sc in enumerate(coordinates):
        distances.append([0] * n)
        for ti, tc in enumerate(coordinates):
            distances[si][ti] = {}
            distances[si][ti]['si'] = si
            distances[si][ti]['ti'] = ti
            if si == ti:
                distances[si][ti]['distance'] = float('inf')
            else:
                distances[si][ti]['distance'] = calc_distance(
                    sc['x'], sc['y'], tc['x'], tc['y'])

    for si, sc in enumerate(coordinates):
        distances[si].sort(key=lambda x: x['distance'])

    G.add_nodes_from(range(len(coordinates)))
    for si, sd in enumerate(distances):
        for td in distances[si][:K]:
            G.add_edge(td['si'], td['ti'])

    return G


def jaccard_similarity_sum(G, S):
    s = 0
    for node in G.nodes:
        g_n = [n for n in G.neighbors(node)]
        s_n = [n for n in S.neighbors(node)]
        s += len(set(g_n) & set(s_n)) / len(set(g_n + s_n))

    return s / len(G.nodes)


def shape_based(G, coordinates, K):
    S = k_nearest(coordinates, K)

    js_v = jaccard_similarity_sum(G, S)

    return js_v


def objective_wrapper(G, K):
    def objective(trial):

        props = get_props(trial)

        p4c.set_layout_properties(
            layout_name=LAYOUT_NAME, properties_dict=props)
        p4c.layout_network(layout_name=LAYOUT_NAME)

        coordinates = get_coordinates()

        shape_based_v = shape_based(G, coordinates, K)

        shape_based_values[str(K)].append(shape_based_v)

        return shape_based_v

    return objective


def main():
    p4c.delete_all_networks()

    with open('generated_graph.json') as f:
        node_link_data = json.load(f)

    G = nx.node_link_graph(node_link_data)

    average_degree = get_average_degree(G)

    suid = p4c.create_network_from_networkx(G)
    p4c.set_node_shape_default('ELLIPSE')
    p4c.set_node_size_default(15)
    p4c.set_node_font_size_default(10)

    global shape_based_values
    for k in k_range:
        shape_based_values[str(k)] = []
        study = optuna.create_study(direction='maximize')
        study.optimize(objective_wrapper(G, k), n_trials=N_TRIALS)
        shape_based_values[f"{str(k)}-best_id"] = study.best_trial.number

    print(shape_based_values)

    show_k_nearest(average_degree)


if __name__ == '__main__':
    main()
