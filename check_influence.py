from re import T
import networkx as nx
import py4cytoscape as pfc
import random

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

TARGET = 'unweighted'
VALUE = False

LAYOUT_NAME = 'kamada-kawai'
N_TRIALS = 100

EXPORT_IMG_TYPE = 'png'

EDGE_WEIGHT = 300

ITER_COUNT = 1


def get_coordinates():
    coordinates = []
    for index, row in pfc.get_node_position().iterrows():
        coordinates.append(row.to_dict())

    return coordinates


def layout_and_export(export_path, props):
    print(props)
    pfc.set_layout_properties(layout_name=LAYOUT_NAME,
                              properties_dict=props)
    pfc.layout_network(layout_name=LAYOUT_NAME)
    pfc.export_image(export_path, type=EXPORT_IMG_TYPE,
                     resolution=600, overwrite_file=True, height=1000, width=1000)


def main():
    G = nx.scale_free_graph(100)

    G = nx.Graph(G)
    G.remove_edges_from(list(nx.selfloop_edges(G)))

    weighted_edges = []
    for e in G.edges:
        weighted_edges.append((e[0], e[1], int(random.randrange(1, 400))))
        # weighted_edges.append((e[0], e[1], EDGE_WEIGHT))
    G.add_weighted_edges_from(weighted_edges)

    largest_cc = max(nx.connected_components(G), key=len)
    LG = G.subgraph(largest_cc)

    suid = pfc.create_network_from_networkx(LG)

    pfc.set_node_shape_default('ELLIPSE')
    pfc.set_node_size_default(15)
    pfc.set_node_font_size_default(10)

    for i in range(ITER_COUNT):
        suid = pfc.create_network_from_networkx(LG)

        props[TARGET] = True
        layout_and_export(
            f"images/check_influence/{TARGET}={props[TARGET]}/{i}", props)

        # print(get_coordinates())

        props[TARGET] = False
        layout_and_export(
            f"images/check_influence/{TARGET}={props[TARGET]}/{i}", props)
        # print(get_coordinates())


if __name__ == '__main__':
    main()
