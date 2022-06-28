import networkx as nx


def calc_distance(sx, sy, tx, ty):
    dx = sx - tx
    dy = sy - ty
    distance = (dx ** 2 + dy ** 2) ** 0.5

    return distance


def k_nearest(coordinates, K):
    G = nx.DiGraph()
    n = len(coordinates)

    distances = []
    for si, sc in enumerate(coordinates):
        distances.append([0] * n)
        for ti, tc in enumerate(coordinates):
            distances[si][ti] = {}
            distances[si][ti]['si'] = si
            distances[si][ti]['ti'] = ti
            if si == ti:
                distances[si][ti]['distance'] = float('inf')
            else:
                distances[si][ti]['distance'] = calc_distance(
                    sc['x'], sc['y'], tc['x'], tc['y'])

    for si, sc in enumerate(coordinates):
        distances[si].sort(key=lambda x: x['distance'])

    G.add_nodes_from(range(len(coordinates)))
    for si, sd in enumerate(distances):
        for td in distances[si][:K]:
            G.add_edge(td['si'], td['ti'])

    return G


def jaccard_similarity_sum(G, S):
    s = 0
    for node in G.nodes:
        g_n = [n for n in G.neighbors(node)]
        s_n = [n for n in S.neighbors(node)]
        s += len(set(g_n) & set(s_n)) / len(set(g_n + s_n))

    return s / len(G.nodes)


def shape_based(G, coordinates, K):
    S = k_nearest(coordinates, K)

    js_v = jaccard_similarity_sum(G, S)

    return js_v
