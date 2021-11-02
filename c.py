import networkx as nx
from py2cytoscape.data.cyrest_client import CyRestClient
import matplotlib.pyplot as plt

cy = CyRestClient(ip='127.0.0.1', port=1234)

cy.session.delete()


def main():
    g = nx.scale_free_graph(500)
    g = nx.to_undirected(g)
    for k in nx.connected_components(g):
        print(k)
        for i in range(500):
            if i not in k:
                print(i)
    largest_cc = max(nx.connected_components(g), key=len)

    print(largest_cc)
    g = g.subgraph(largest_cc)
    # g = nx.karate_club_graph()
    # g = nx.davis_southern_women_graph()
    # g = nx.complete_graph(50)

    # deg = nx.degree(g)
    # btw = nx.betweenness_centrality(g)

    # nx.set_node_attributes(g, 'degree', deg)
    # nx.set_node_attributes(g, 'betweenness', btw)
    # nx.set_node_attributes(g, deg, 'degree')
    # nx.set_node_attributes(g, btw, 'betweenness')
    print(nx.to_numpy_array(g))
    labels = [str(node) for node in g.nodes]

    # g_cy = cy.network.create_from_ndarray(
    #     nx.to_numpy_array(g), labels=g.nodes)
    g_cy = cy.network.create_from_ndarray(
        nx.to_numpy_array(g), labels=labels)
    # g_cy = cy.network.create_from_networkx(g)
    # cy.network.create_from_dataframe()
    # g_cy = cy.network.create(data=g)

    cy.layout.apply(name='kamada-kawai', network=g_cy)
    n = g_cy.get_first_view()
    p = [item for item in n['elements']['nodes']]
    # for a in p:
    #     print(a)
    # p = [{'x': item['position']['x'], 'y': item['position']['y'],
    #       'id': item['data']['name']} for item in n['elements']['nodes']]
    # print(n['elements']['nodes'])
    pos = {}
    for p in [{'x': item['position']['x'], 'y': item['position']['y'],
               'id': item['data']['name']} for item in n['elements']['nodes']]:
        pos[int(p['id'])] = [p['x'], p['y']]
    print(pos)
    print(labels)
    # print(g.nodes)
    # print(g_cy.get_nodes())
    nx.draw(g, pos=pos)

    plt.show()


if __name__ == "__main__":
    main()

# from py2cytoscape.data.cyrest_client import CyRestClient

# cy = CyRestClient()
# network = cy.network.create(
#     name='My Network', collection='My network collection')
# print('Empty network created: SUID = ' + str(network.get_id()))

{'data': {'id': '249689', 'shared_name': '499', 'name': '499', 'SUID': 249689, 'id_original': '499',
          'selected': False}, 'position': {'x': 660.8644527169517, 'y': -899.5105417385441}, 'selected': False}


# n_pos
# {'Evelyn Jefferson': array([0.49197558, -0.03999435]), 'Laura Mandeville': array([0.61542163, 0.00390014]), 'Theresa Anderson': array([0.45243517, 0.10137317]), 'Brenda Rogers': array([0.54735248, -0.15405955]), 'Charlotte McDowd': array([0.81854894, 0.01534754]), 'Frances Anderson': array([0.49722908, 0.48792155]), 'Eleanor Nye': array([0.2821468, 0.42431412]), 'Pearl Oglethorpe': array([-0.10327476,  0.48845044]), 'Ruth DeSand': array([0.10308101, 0.36000132]), 'Verne Sanderson': array([-0.3534142,  0.19664374]), 'Myra Liddel': array([-0.61584073,  0.05750541]), 'Katherina Rogers': array([-0.50432347, -0.39459303]), 'Sylvia Avondale': array([-0.34692166, -0.36768832]), 'Nora Fayette': array([-0.41689226, -0.2133971]), 'Helen Lloyd': array(
#     [-0.4760031, -0.02747151]), 'Dorothy Murchison': array([-0.01969066, -0.40504529]), 'Olivia Carleton': array([-0.90205118,  0.41468255]), 'Flora Price': array([-0.7371946,  0.53816651]), 'E1': array([0.82818736, -0.41289361]), 'E2': array([1., 0.08902894]), 'E3': array([0.80342419, 0.23024832]), 'E4': array([0.90078585, -0.19813546]), 'E5': array([0.58897332, 0.28417026]), 'E6': array([0.22849001, 0.14746197]), 'E7': array([0.12398918, -0.03625168]), 'E8': array([0.01657238, 0.03793091]), 'E9': array([-0.23536224,  0.0870862]), 'E10': array([-0.77053952, -0.32734439]), 'E11': array([-0.89788418,  0.16726972]), 'E12': array([-0.69698463, -0.15607355]), 'E13': array([-0.5068514, -0.7447839]), 'E14': array([-0.71538439, -0.65377107])}
