import json
from re import L

import matplotlib.pyplot as plt

from args import k_from, k_to, graph_n, params_n, TITLE


KK = 'kamada-kawai'
FR = 'fruchterman-rheingold'


DATA_PATH = f'data/{TITLE}.json'


def main():
    with open(DATA_PATH) as f:
        data = json.load(f)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('k or d-t')
    ax.set_ylabel('sbm')
    ax.grid(True)

    plt.xticks(rotation=-90)

    s = {}
    for sbm in data['sbms']:
        for layout_name in sbm:
            if layout_name not in s:
                s[layout_name] = {}
            for label in sbm[layout_name]:
                if label not in s[layout_name]:
                    s[layout_name][label] = []
                s[layout_name][label].append(sbm[layout_name][label])
    i = 0
    for layout_name in sbm:
        for label in sbm[layout_name]:
            i += 1
            print(i)
            ax.scatter([label] * len(s[layout_name][label]), s[layout_name][label],
                       marker='o' if layout_name == KK else '^')

    plt.savefig(f'images/{TITLE}.png')
    plt.show()
    print(TITLE)


if __name__ == '__main__':
    main()
