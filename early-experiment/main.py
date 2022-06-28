import networkx as nx
import py4cytoscape as pfc
import optuna
import matplotlib.pyplot as plt
import numpy as np
import random

from shape_based import shape_based
from stress import stress

LAYOUT_NAME = 'kamada-kawai'
N_TRIALS = 1

EXPORT_IMG_TYPE = 'png'

EDGE_WEIGHT = 30

np.random.seed(10)


def get_shortest_paths(G):
    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G))
    # shortest_paths = dict(nx.all_pairs_shortest_path_length(G))
    return shortest_paths


def get_coordinates():
    coordinates = []
    for index, row in pfc.get_node_position().iterrows():
        coordinates.append(row.to_dict())

    return coordinates


def get_average_degree(G):
    s = 0
    for n in G.nodes:
        s += G.degree[n]
    return s / len(G.nodes)


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
        print(pfc.get_network_property())

        coordinates = get_coordinates()
        # stress_v = stress(coordinates, shortest_paths,
        #                   props['m_disconnectedNodeDistanceSpringStrength'],
        #                   props['m_nodeDistanceRestLengthConstant'])
        stress_v = stress(coordinates, shortest_paths,
                          1,
                          1)
        shape_based_v = shape_based(G, coordinates, K)

        return stress_v, shape_based_v

    return objective


def main():
    pfc.delete_all_networks()
    G = nx.scale_free_graph(200)
    # G = nx.karate_club_graph()

    G = nx.Graph(G)
    G.remove_edges_from(list(nx.selfloop_edges(G)))

    G2 = G

    weighted_edges = []
    for e in G.edges:
        weighted_edges.append((e[0], e[1], EDGE_WEIGHT))
    G.add_weighted_edges_from(weighted_edges)

    weighted_edges2 = []
    for e in G2.edges:
        weighted_edges2.append(
            (e[0], e[1], {'weight': random.randrange(1, EDGE_WEIGHT), 'hello': random.randrange(1, EDGE_WEIGHT * 100)}))
        # weighted_edges2.append(
        #     (e[0], e[1], random.randrange(1, EDGE_WEIGHT * 10)))
    # G2.add_weighted_edges_from(weighted_edges2)
    G2.add_edges_from(weighted_edges2)

    # print(G.edges(data=True))
    largest_cc = max(nx.connected_components(G), key=len)
    LG = G.subgraph(largest_cc)

    largest_cc2 = max(nx.connected_components(G2), key=len)
    LG2 = G2.subgraph(largest_cc2)

    # subax1 = plt.subplot(121)
    # pos1 = nx.kamada_kawai_layout(
    #     G, weight='weight')
    # nx.draw(
    #     G, pos1, node_size=30)

    # subax2 = plt.subplot(122)
    # pos2 = nx.kamada_kawai_layout(
    #     G, weight='weight')
    # nx.draw(
    #     G, pos2, node_size=30)

    # plt.show()

    # print(pos1, pos2)

    suid = pfc.create_network_from_networkx(G)
    pfc.set_node_shape_default('ELLIPSE')
    pfc.set_node_size_default(15)
    pfc.set_node_font_size_default(10)

    # shortest_paths = get_shortest_paths(LG)

    props = {'m_averageIterationsPerNode': 55.604209420236984,
             'm_nodeDistanceStrengthConstant': 38.90783455144209,
             'm_nodeDistanceRestLengthConstant': 23.40870116324407,
             'm_disconnectedNodeDistanceSpringStrength': 0.24047191051681993,
             'm_disconnectedNodeDistanceSpringRestLength': 438.5597357094961,
             'm_anticollisionSpringStrength': 0.2813340044871838,
             'm_layoutPass': 1,
             'singlePartition': False,
             'unweighted': False,
             'randomize': False}

    coords = []
    target_folder = 'images/'

    name = 'same'
    shortest_paths = get_shortest_paths(LG)
    shortest_paths2 = get_shortest_paths(LG2)

    for i in range(1):
        pfc.delete_all_networks()
        suid = pfc.create_network_from_networkx(LG)
        pfc.set_layout_properties(layout_name=LAYOUT_NAME,
                                  properties_dict=props)
        pfc.layout_network(layout_name=LAYOUT_NAME)
        pfc.export_image(f"{target_folder}{name}{1}-{i}", type=EXPORT_IMG_TYPE,
                         resolution=600, overwrite_file=True, height=1000, width=1000)
        coordinates = get_coordinates()
        coords.append(coordinates)
        stress_v = stress(coordinates, shortest_paths,
                          1,
                          1)

        pfc.delete_all_networks()
        suid = pfc.create_network_from_networkx(LG2)
        pfc.set_layout_properties(layout_name=LAYOUT_NAME,
                                  properties_dict=props)
        pfc.layout_network(layout_name=LAYOUT_NAME)
        pfc.export_image(f"{target_folder}diff{2}-{i}", type=EXPORT_IMG_TYPE,
                         resolution=600, overwrite_file=True, height=1000, width=1000)
        coordinates2 = get_coordinates()
        coords.append(coordinates2)
        stress_v2 = stress(coordinates2, shortest_paths2,
                           1,
                           1)

        print(stress_v, stress_v2)

    # for i in range(4):
    # pfc.set_layout_properties(layout_name=LAYOUT_NAME,
    #                           properties_dict=props)
    # pfc.layout_network(layout_name=LAYOUT_NAME)
    # pfc.export_image(f"{target_folder}diff{2}-{i}", type=EXPORT_IMG_TYPE,
    #                  resolution=600, overwrite_file=True, height=1000, width=1000)

    # coords.append(get_coordinates())

    # print(coords)

    # bests = {}
    # coords = []
    # for id in range(1, 1 + 1):
    #     K = id
    #     TARGET_FOLDER = f'images/{K}-nearest/'

    #     bests[f'{K}-nearest'] = []

    #     study = optuna.create_study(directions=['minimize', 'maximize'])
    #     study.optimize(objective_wrapper(
    #         LG, shortest_paths, K), n_trials=N_TRIALS)

    #     for best in study.best_trials:
    #         id = best._trial_id
    #         bests[f'{K}-nearest'].append({'id': id, 'result': best.values,
    #                                      'params': best.params})
    #         best_params = best.params
    #         pfc.set_layout_properties(layout_name=LAYOUT_NAME,
    #                                   properties_dict=best_params)
    #         pfc.layout_network(layout_name=LAYOUT_NAME)
    #         pfc.export_image(f"{TARGET_FOLDER}{id}", type=EXPORT_IMG_TYPE,
    #                          resolution=600, overwrite_file=True, height=1000, width=1000)
    #         coords.append(get_coordinates())

    # plot_pareto_front = optuna.visualization.plot_pareto_front(study)
    # plot_pareto_front.show()
    # print(coords)
    # print(bests)


if __name__ == '__main__':
    main()
    # print(pfc.get_visual_property_names())
    # print(pfc.get_visual_style_names())
    # pfc.cyrest_api()
