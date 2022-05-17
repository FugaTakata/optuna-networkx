def stress(coordinates, distance, K, L):
    n = len(coordinates)
    s = 0

    for i in range(1, n):
        for j in range(0, i):
            dx = coordinates[i]['x'] - coordinates[j]['x']
            dy = coordinates[i]['y'] - coordinates[j]['y']
            norm = (dx ** 2 + dy ** 2) ** 0.5

            dij = distance[i][j]
            lij = L * dij
            kij = K / (dij ** 2)
            e = (kij * ((norm - lij) ** 2)) / 2

            s += e
    return s
