import pprint
import random
import json

import networkx as nx
import py4cytoscape as p4c
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Delaunay

from args import k_from, k_to, graph_n, params_n, TITLE

KK = 'kamada-kawai'
FR = 'fruchterman-rheingold'

EDGE_WEIGHT = 30


def get_shortest_paths(G):

    shortest_paths = dict(nx.all_pairs_dijkstra_path_length(G))
    return shortest_paths


def get_coordinates():
    coordinates = []
    for index, row in p4c.get_node_position().iterrows():
        coord = row.to_dict()
        coordinates.append({'id': index, 'x': coord['x'], 'y': coord['y']})

    return coordinates


def get_average_degree(G):
    s = 0
    # ma = 0
    # mi = float('inf')
    for n in G.nodes:
        s += G.degree[n]
    #     if ma < G.degree[n]:
    #         ma = G.degree[n]
    #     if mi > G.degree[n]:
    #         mi = G.degree[n]

    # print(ma, mi)
    return s / len(G.nodes)


def calc_distance(sx, sy, tx, ty):
    dx = sx - tx
    dy = sy - ty
    distance = (dx ** 2 + dy ** 2) ** 0.5

    return distance


def k_nearest(g, coordinates, K, distances):
    sg = nx.Graph()
    sg.add_nodes_from(g.nodes)
    if distances is None:
        distances = {}
        for s in coordinates:
            sid = s['id']
            distances[sid] = []
            for t in coordinates:
                tid = t['id']
                if sid == tid:
                    distance = float('inf')
                else:
                    distance = calc_distance(s['x'], s['y'], t['x'], t['y'])
                distances[sid].append({'id': tid, 'd': distance})

        for s in coordinates:
            sid = s['id']
            distances[sid].sort(key=lambda x: x['d'])

    weighted_edges = []
    for sid in sg.nodes:
        for t in distances[sid][:K]:
            tid = t['id']
            weighted_edges.append((sid, tid, EDGE_WEIGHT))

    sg.add_weighted_edges_from(weighted_edges)

    return sg, distances
    # return sg


def delaunay_triangulation(G, coordinates):
    index_nodeid_map = {}
    pos_array = []
    for index, coordinate in enumerate(coordinates):
        pos = [coordinate['x'], coordinate['y']]
        pos_array.append(pos)
        index_nodeid_map[index] = coordinate['id']
    # pos_array = [[p['x'], p['y']] for p in coordinates]
    pos_ndarray = np.array(pos_array)
    delaunay = Delaunay(pos_ndarray)

    S = nx.Graph()
    S.add_nodes_from(G.nodes)

    weighted_edges = []
    for n in delaunay.simplices:
        n0 = n[0]
        n1 = n[1]
        n2 = n[2]
        weighted_edges.append(
            (index_nodeid_map[n0], index_nodeid_map[n1], EDGE_WEIGHT))
        weighted_edges.append(
            (index_nodeid_map[n0], index_nodeid_map[n2], EDGE_WEIGHT))
        weighted_edges.append(
            (index_nodeid_map[n1], index_nodeid_map[n2], EDGE_WEIGHT))

    S.add_weighted_edges_from(weighted_edges)

    return S


def jaccard_similarity_sum(G, S):
    s = 0
    for node in G.nodes:
        g_n = [n for n in G.neighbors(node)]
        s_n = [n for n in S.neighbors(node)]
        and_n = list(set(g_n) & set(s_n))
        or_n = list(set(g_n + s_n))
        # print(node)
        # pprint.pprint(G.edges)
        # pprint.pprint(S.edges)
        # pprint.pprint({'g': list(g_n), 's': list(s_n), 'a': list(
        #     set(g_n) & set(s_n)), 'o': list(set(g_n + s_n))})
        s += len(and_n) / len(or_n)

    return s / len(G.nodes)


def generate_graph():
    # n = random.uniform(100, 300)
    # g = nx.scale_free_graph(n)
    g = nx.les_miserables_graph()
    g = nx.Graph(g)
    g = g.to_undirected()
    g.remove_edges_from(list(nx.selfloop_edges(g)))

    largest_cc = max(nx.connected_components(g), key=len)
    lg = g.subgraph(largest_cc)

    # print([i for i in g.neighbors(0)])

    rg = nx.Graph()

    nodes = [str(node) for node in lg.nodes]
    rg.add_nodes_from(nodes)

    weighted_edges = []
    for e in lg.edges:
        weighted_edges.append((str(e[0]), str(e[1]), EDGE_WEIGHT))

    rg.add_weighted_edges_from(weighted_edges)

    return rg


def generate_params(layout_name):
    if layout_name == KK:
        params = {'m_averageIterationsPerNode': random.uniform(0, 150),
                  'm_nodeDistanceStrengthConstant': random.uniform(0, 50),
                  'm_nodeDistanceRestLengthConstant': random.uniform(0, 100),
                  'm_disconnectedNodeDistanceSpringStrength': random.uniform(0, 1),
                  'm_disconnectedNodeDistanceSpringRestLength': random.uniform(0, 10000),
                  'm_anticollisionSpringStrength': random.uniform(0, 1),
                  'm_layoutPass': 0,
                  'singlePartition': False,
                  'unweighted': False,
                  'randomize': False
                  }
    elif layout_name == FR:
        params = {
            "update_iterations": 0,
            "attraction_multiplier": random.uniform(0, 0.03 * 2),
            "repulsion_multiplier": random.uniform(0, 0.04 * 2),
            "gravity_multiplier": random.uniform(0, 1 * 2),
            "conflict_avoidance": random.uniform(0, 20 * 2),
            "max_distance_factor": random.uniform(0, 20 * 2),
            "spread_factor": random.uniform(0, 2 * 2),
            "temperature": random.uniform(0, 80 * 2),
            "nIterations": random.randint(300, 500),
            "singlePartition": False,
            "layout3D": False,
            "randomize": False,
        }

    return params


def export_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)


def main():
    p4c.delete_all_networks()

    layout_names = [KK, FR]

    graphs = []
    layout_params_maps = []
    for _ in range(graph_n):
        graphs.append(generate_graph())

    for _ in range(params_n):
        params_map = {KK: generate_params(KK), FR: generate_params(FR)}
        layout_params_maps.append(params_map)

    data = {'sbms': [], 'graphs': [],
            'layout_params_maps': layout_params_maps}

    for graph in graphs:
        data['graphs'].append(nx.node_link_data(graph))

    p4c.create_network_from_networkx(graphs[0])
    p4c.set_node_shape_default('ELLIPSE')
    p4c.set_node_size_default(15)
    p4c.set_node_font_size_default(10)

    i = 0

    for graph in graphs:
        p4c.create_network_from_networkx(graph)

        for params_map in layout_params_maps:

            sbm = {}
            for layout_name in layout_names:
                sbm[layout_name] = {}

                p4c.set_layout_properties(
                    layout_name, properties_dict=params_map[layout_name])
                p4c.layout_network(layout_name)

                coordinates = get_coordinates()

                distances = None
                for k in range(k_from, k_to + 1):
                    # print('e', graph.edges)
                    # print('n', [i for i in graph.neighbors('0')])
                    # print(get_average_degree(graph))
                    sg, distances = k_nearest(graph, coordinates, k, distances)
                    sbm[layout_name][f"{k}-n"] = jaccard_similarity_sum(
                        graph, sg)
                sg = delaunay_triangulation(graph, coordinates)
                sbm[layout_name]['d-t'] = jaccard_similarity_sum(graph, sg)
                print(i, graph_n * params_n * len(layout_names))
                i += 1

            data['sbms'].append(sbm)

    export_json(f"data/{TITLE}.json", data)


if __name__ == '__main__':
    main()
