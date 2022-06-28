import json

import networkx as nx
import matplotlib.pyplot as plt

from args import k_from, k_to, graph_n, params_n, TITLE


KK = 'kamada-kawai'
FR = 'fruchterman-rheingold'


DATA_PATH = f'data/{TITLE}.json'


def get_average_degree(G):
    s = 0
    ds = get_degrees(G)
    for d in ds:
        s += d

    return s / len(ds)


def get_degrees(G):
    ma = 0
    mi = float('inf')
    ds = []
    for n in G.nodes:
        ds.append(G.degree[n])
        if ma < G.degree[n]:
            ma = G.degree[n]
        if mi > G.degree[n]:
            mi = G.degree[n]

    print(ma, mi)
    return ds


def show_degree(data):
    x_label = 'edge_n'
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel(x_label)
    ax.set_ylabel('average_degree')
    ax.grid(True)

    for graph in data['graphs']:
        g = nx.node_link_graph(graph)

        average_degree = get_average_degree(g)
        x = {
            'node_n': len(g.nodes),
            'edge_n': len(g.edges)
        }

        ax.scatter(x[x_label], average_degree)
        print(average_degree)

    plt.show()


def show_degree_histogram(data):
    mu, sigma = 100, 15

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ds = []
    for graph in data['graphs']:
        g = nx.node_link_graph(graph)

        ds += get_degrees(g)
        print(get_average_degree(g))

    ax.hist(ds, bins=50)
    ax.set_title('$\mu=100,\ \sigma=15$')
    ax.set_xlabel('degree')
    ax.set_ylabel('')

    plt.savefig(f'images/info_{TITLE}.png')
    plt.show()


def main():
    with open(DATA_PATH) as f:
        data = json.load(f)

    # show_degree(data)
    show_degree_histogram(data)


if __name__ == '__main__':
    main()
