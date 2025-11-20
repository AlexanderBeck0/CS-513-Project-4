from routing import dijkstra
from graph_manager import GraphManager


def brandes_centrality(graph_manager: GraphManager) -> dict[str, float]:
    # An implementation of the algorithm found in "A faster algorithm for betweenness centrality"
    # doi: 10.1080/0022250X.2001.9990249
    # Google that to find it ^
    assert graph_manager is not None

    graph = graph_manager.graph
    V: list[str] = list(graph.nodes())  # The list of nodes
    CB: dict[str, float] = dict.fromkeys(V, 0.0)  # The betweenness

    for s in V:
        S = []  # Empty stack
        P = {w: [] for w in V}  # Predecessors
        sigma: dict[str, float] = dict.fromkeys(V, 0.0)  # Number of shortest paths
        sigma[s] = 1

        dist: dict[str, int] = dict.fromkeys(V, -1)  # d[t]
        dist[s] = 0

        # Since Dijkstra is already implemented in this project, I'm not going to reimplement it
        dijkstra_results = dijkstra(s, graph)

        # Build dist and predecessors
        # Not as efficient as if Dijkstra was built for this task (like in algorithm in paper)
        # But will give the same result
        for distance, node, via in dijkstra_results:
            dist[node] = distance  # type: ignore
            if via and via != "-":
                P[node].append(via)

        # Sort vertices in order of non-increasing distance from s
        sorted_nodes = sorted([v for v in V if dist[v] >= 0], key=lambda v: dist[v])

        for v in sorted_nodes:
            S.append(v)
            for w in graph.neighbors(v):
                weight = graph[v][w]["weight"]
                # // shortest path to w via v?
                if dist[w] == dist[v] + weight:
                    # Note that weight here is a 1 on the algorithm since they are using an unweighted version
                    sigma[w] = sigma[w] + sigma[v]
                    P[w].append(v)

        delta: dict[str, float] = dict.fromkeys(V, 0)
        while S:
            w = S.pop()
            for v in P[w]:
                delta[v] = delta[v] + (sigma[v] / sigma[w]) * (1 + delta[w])
                if w != s:
                    CB[w] = CB[w] + delta[w]

    # the centrality scores need to be divided by two if the graph is undirected, since all shortest paths are considered twice.
    if not graph.is_directed():
        for v in CB:
            CB[v] = CB[v] / 2
    return CB
