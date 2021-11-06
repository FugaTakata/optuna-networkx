import py4cytoscape as pfc
import networkx as nx
import optuna

LAYOUT_NAME = 'kamada-kawai'


def stress(pos, shortest_paths):
    keys = list(pos.keys())
    n = len(keys)

    s = 0
    for si in range(0, n):
        for ti in range(si + 1, n):
            ks = keys[si]
            kt = keys[ti]
            [sx, sy] = pos[ks]
            [tx, ty] = pos[kt]
            dx = sx - tx
            dy = sy - ty

            norm = (dx ** 2 + dy ** 2) ** 0.5
            dij = shortest_paths[ks][kt]
            e = norm - dij
            s += e ** 2
    return s


def k_nearest(pos, k):
    G = nx.DiGraph()

    keys = list(pos.keys())
    n = len(keys)

    ds = {}
    for si in range(0, n):
        ds[keys[si]] = []
        [sx, sy] = pos[keys[si]]
        for ti in range(0, n):
            [tx, ty] = pos[keys[ti]]
            dx = abs(sx - tx)
            dy = abs(sy - ty)
            d = (dx ** 2 + dy ** 2) ** 0.5
            ds[keys[si]].append({'id': keys[ti], 'd': d})

    for si in range(0, n):
        ds[keys[si]].sort(key=lambda x: x['d'])

    G.add_nodes_from(keys)
    for si in range(0, n):
        for t in ds[keys[si]][:k]:
            G.add_edge(keys[si], t['id'])

    return G


def jaccard_similarity_sum(G, S):
    s = 0
    for node in G.nodes:
        g_n = [n for n in G.neighbors(node)]
        s_n = [n for n in S.neighbors(node)]
        s += len(set(g_n) & set(s_n)) / len(set(g_n + s_n))

    return s


def shape_based(G, pos):
    k = 4
    S = k_nearest(pos, k)
    js = jaccard_similarity_sum(G, S)
    js /= len(G.nodes)

    return js


def get_shortestpaths(G):
    shortest_paths = {}
    for ns in G.nodes:
        shortest_paths[ns] = {}
        for nt in G.nodes:
            shortest_paths[ns][nt] = nx.shortest_path_length(
                G,
                source=ns,
                target=nt)
    return shortest_paths


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
                 'randomize': False}

        pfc.set_layout_properties(
            layout_name=LAYOUT_NAME, properties_dict=props)
        pfc.layout_network(layout_name=LAYOUT_NAME)

        positions_df = pfc.get_node_position()

        pos = {}
        for index, row in positions_df.iterrows():
            pos[int(index)] = row.to_list()

        stress_value = stress(pos, shortest_paths)
        shape_based_value = shape_based(G, pos)

        return stress_value, shape_based_value

    return objective


def main():
    G = nx.scale_free_graph(100)
    UG = nx.to_undirected(G)

    largest_cc = max(nx.connected_components(UG), key=len)
    LG = UG.subgraph(largest_cc)

    shortest_paths = get_shortestpaths(LG)

    study = optuna.create_study(directions=['minimize', 'maximize'])
    study.optimize(objective_wrapper(LG, shortest_paths), n_trials=10)

    best_params = study.best_trials[0].params
    print(best_params)
    pfc.set_layout_properties(layout_name=LAYOUT_NAME,
                              properties_dict=best_params)
    pfc.layout_network(layout_name=LAYOUT_NAME)

    plot_pareto_front = optuna.visualization.plot_pareto_front(study)
    plot_pareto_front.show()


if __name__ == '__main__':
    main()

# kamada-kawai layout properties and defaults
# {
#     'm_averageIterationsPerNode': 40.0,
#     'm_nodeDistanceStrengthConstant': 15.0,
#     'm_nodeDistanceRestLengthConstant': 45.0,
#     'm_disconnectedNodeDistanceSpringStrength': 0.05,
#     'm_disconnectedNodeDistanceSpringRestLength': 2000.0,
#     'm_anticollisionSpringStrength': 0.0,
#     'm_layoutPass': 2,
#     'singlePartition': False,
#     'unweighted': False,
#     'randomize': True
# }
