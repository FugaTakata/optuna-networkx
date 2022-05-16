import networkx as nx
import py4cytoscape as pfc
import optuna


LAYOUT_NAME = 'kamada-kawai'
N_TRIALS = 100
K_NEAREST_K = 5
TARGET_FOLDER = f'{K_NEAREST_K}-nearest'
IMAGES_FOLDER = 'images'
EXPORT_IMG_TYPE = 'png'


def get_shortest_paths(G):
    shortest_paths = dict(nx.all_pairs_shortest_path_length(G))
    return shortest_paths


def get_coordinates():
    coordinates = []
    for _index, row in pfc.get_node_position().iterrows():
        coordinates.append(row.to_dict())

    return coordinates


def calc_distance(sx, sy, tx, ty):
    dx = sx - tx
    dy = sy - ty
    distance = (dx ** 2 + dy ** 2) ** 0.5

    return distance


def stress(coordinates, distance, K, L):
    n = len(coordinates)
    s = 0

    for i in range(1, n):
        for j in range(0, i):
            dx = coordinates[i]['x'] - coordinates[j]['x']
            dy = coordinates[i]['y'] - coordinates[j]['y']
            norm = (dx ** 2 + dy ** 2) ** 0.5

            dij = distance[j][i]
            lij = L * dij
            kij = K / (dij ** 2)
            e = (kij * ((norm - lij) ** 2)) / 2

            s += e
    return s


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


def shape_based(G, coordinates):
    S = k_nearest(coordinates, K_NEAREST_K)

    js_v = jaccard_similarity_sum(G, S)

    return js_v


def objective_wrapper(G, shortest_paths):
    pfc.delete_all_networks()
    suid = pfc.create_network_from_networkx(G)

    def objective(trial):
        props = {'m_averageIterationsPerNode': trial.suggest_float('m_averageIterationsPerNode', 0, 100),
                 'm_nodeDistanceStrengthConstant': trial.suggest_float('m_nodeDistanceStrengthConstant', 0, 50),
                 'm_nodeDistanceRestLengthConstant': trial.suggest_float('m_nodeDistanceRestLengthConstant', 0, 100),
                 'm_disconnectedNodeDistanceSpringStrength': trial.suggest_float('m_disconnectedNodeDistanceSpringStrength', 0, 1),
                 'm_disconnectedNodeDistanceSpringRestLength': trial.suggest_float('m_disconnectedNodeDistanceSpringRestLength', 0, 10000),
                 'm_anticollisionSpringStrength': trial.suggest_float('m_anticollisionSpringStrength', 0, 1),
                 'm_layoutPass': trial.suggest_int('m_layoutPass', 0, 5),
                 'singlePartition': False,
                 'unweighted': False,
                 'randomize': False
                 }

        pfc.set_layout_properties(
            layout_name=LAYOUT_NAME, properties_dict=props)
        pfc.layout_network(layout_name=LAYOUT_NAME)

        coordinates = get_coordinates()
        stress_v = stress(coordinates, shortest_paths,
                          props['m_disconnectedNodeDistanceSpringStrength'],
                          props['m_nodeDistanceRestLengthConstant'])
        shape_based_v = shape_based(G, coordinates)

        return stress_v, shape_based_v

    return objective


def main():
    G = nx.scale_free_graph(100)
    UG = nx.to_undirected(G)

    largest_cc = max(nx.connected_components(UG), key=len)
    LG = UG.subgraph(largest_cc)

    shortest_paths = get_shortest_paths(LG)

    study = optuna.create_study(directions=['minimize', 'maximize'])
    study.optimize(objective_wrapper(LG, shortest_paths), n_trials=N_TRIALS)

    for best in study.best_trials:
        id = best._trial_id
        best_params = best.params
        pfc.set_layout_properties(layout_name=LAYOUT_NAME,
                                  properties_dict=best_params)
        pfc.layout_network(layout_name=LAYOUT_NAME)
        pfc.export_image(f"{IMAGES_FOLDER}/{TARGET_FOLDER}/{id}", type=EXPORT_IMG_TYPE,
                         resolution=600, overwrite_file=True)

    plot_pareto_front = optuna.visualization.plot_pareto_front(study)
    plot_pareto_front.show()


if __name__ == '__main__':
    main()
