import networkx as nx
from py2cytoscape.data.cyrest_client import CyRestClient
import matplotlib.pyplot as plt

cy = CyRestClient(ip='127.0.0.1', port=1234)

cy.session.delete()


def main():
    g = nx.scale_free_graph(500)
    # g = nx.karate_club_graph()
    # g = nx.davis_southern_women_graph()
    # g = nx.complete_graph(50)

    deg = nx.degree(g)
    btw = nx.betweenness_centrality(g)

    # nx.set_node_attributes(g, 'degree', deg)
    # nx.set_node_attributes(g, 'betweenness', btw)
    # nx.set_node_attributes(g, deg, 'degree')
    # nx.set_node_attributes(g, btw, 'betweenness')

    g_cy = cy.network.create_from_networkx(g)
    # g_cy = cy.network.create(data=g)

    cy.layout.apply(name='kamada-kawai', network=g_cy)
    n = g_cy.get_first_view()
    # p = [item for item in n['elements']['nodes']]
    # p = [{'x': item['position']['x'], 'y': item['position']['y'],
    #       'id': item['data']['name']} for item in n['elements']['nodes']]
    # print(n['elements']['nodes'])
    pos = {}
    for p in [{'x': item['position']['x'], 'y': item['position']['y'],
               'id': item['data']['name']} for item in n['elements']['nodes']]:
        pos[p['id']] = [p['x'], p['y']]
    print(pos)
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
