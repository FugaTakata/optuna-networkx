import networkx as nx
import matplotlib.pyplot as plt
import optuna
import numpy as np
from optuna import study


np.random.seed(10)


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


def jaccard_similarity(G, S):
    s = 0
    for node in G.nodes:
        g_n = [n for n in G.neighbors(node)]
        s_n = [n for n in S.neighbors(node)]
        s += len(set(g_n) & set(s_n)) / len(set(g_n + s_n))

    js = s / len(G.nodes)
    return js


def shape_based(G, pos):
    k = 4
    # generate shape graph, k may be a hyperparams
    S = k_nearest(pos, k)
    js = jaccard_similarity(G, S)

    return js


def objective_variable_graph(G, shortest_paths):
    def objective(trial):
        k = trial.suggest_float('k', 0, 1)
        i = trial.suggest_int('i', 50, 200)

        pos = nx.spring_layout(G, iterations=i, threshold=1e-4, k=k)
        stress_value = stress(pos, shortest_paths)
        shape_based_value = shape_based(G, pos)

        return stress_value, shape_based_value
        # return stress_value
        # return shape_based_value

    return objective


def main():
    # G = nx.karate_club_graph()
    G = nx.davis_southern_women_graph()

    shortest_paths = {}
    for ns in G.nodes:
        shortest_paths[ns] = {}
        for nt in G.nodes:
            shortest_paths[ns][nt] = nx.shortest_path_length(
                G,
                source=ns,
                target=nt)

    # study = optuna.create_study()
    # study = optuna.create_study(direction='maximize')
    study = optuna.create_study(directions=["minimize", "maximize"])
    study.optimize(objective_variable_graph(G, shortest_paths), n_trials=1000)

    best_params = study.best_trials[0].params
    # plot_pareto_front = optuna.visualization.plot_pareto_front(
    #     study)
    # param_importance = optuna.visualization.plot_param_importances(
    #     study, target=lambda t: t.values[0])
    # plot_countour = optuna.visualization.plot_contour(
    #     study, target=lambda t: t.values[0])
    # plot_optimization_history = optuna.visualization.plot_optimization_history(
    #     study, target=lambda t: t.values[0])

    # plot_pareto_front.show()
    # param_importance.show()
    # plot_countour.show()
    # plot_optimization_history.show()

    found_k = best_params['k']
    found_i = best_params['i']
    print(f'found k: {found_k}, found i: {found_i}')

    found_pos = nx.spring_layout(
        G,
        iterations=found_i,
        threshold=1e-4,
        k=found_k)
    nx.draw(G, pos=found_pos)

    plt.show()


if __name__ == "__main__":
    main()
