import networkx as nx
import py4cytoscape as pfc
import optuna
import matplotlib as plt

from shape_based import shape_based
from stress import stress


LAYOUT_NAME = 'kamada-kawai'
N_TRIALS = 5

EXPORT_IMG_TYPE = 'svg'


def get_shortest_paths(G):
    shortest_paths = dict(nx.all_pairs_shortest_path_length(G))
    return shortest_paths


def get_coordinates():
    coordinates = []
    for index, row in pfc.get_node_position().iterrows():
        coordinates.append(row.to_dict())

    return coordinates


def objective_wrapper(G, shortest_paths, K):
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
        shape_based_v = shape_based(G, coordinates, K)

        return stress_v, shape_based_v

    return objective


def main():
    G = nx.scale_free_graph(100)
    G = nx.Graph(G)

    UG = nx.to_undirected(G)

    largest_cc = max(nx.connected_components(UG), key=len)
    LG = UG.subgraph(largest_cc)

    shortest_paths = get_shortest_paths(LG)
    bests = {}
    for id in range(1, 10 + 1):
        K = id
        TARGET_FOLDER = f'images/{K}-nearest/'

        bests[f'{K}-nearest'] = []

        study = optuna.create_study(directions=['minimize', 'maximize'])
        study.optimize(objective_wrapper(
            LG, shortest_paths, K), n_trials=N_TRIALS)

        for best in study.best_trials:
            id = best._trial_id
            bests[f'{K}-nearest'].append(best.values)
            best_params = best.params
            pfc.set_layout_properties(layout_name=LAYOUT_NAME,
                                      properties_dict=best_params)
            pfc.layout_network(layout_name=LAYOUT_NAME)
            pfc.export_image(f"{TARGET_FOLDER}{id}", type=EXPORT_IMG_TYPE,
                             resolution=600, overwrite_file=True)

        plot_pareto_front = optuna.visualization.plot_pareto_front(study)
        plot_pareto_front.show()
    print(bests)


if __name__ == '__main__':
    main()
