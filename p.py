import py4cytoscape as pfc
import networkx as nx
import optuna


def main():
    pfc.delete_all_networks()

    G = nx.scale_free_graph(50)

    pfc_g = pfc.create_network_from_networkx(G)
    l = pfc.layout_network('kamada-kawai')
    pfc.set_layout_properties
    p = pfc.get_node_position()
    print(p)

    props = {}
    props_names = pfc.get_layout_property_names('kamada-kawai')
    for name in props_names:
        props[name] = pfc.get_layout_property_value('kamada-kawai', name)
    print(props)


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
