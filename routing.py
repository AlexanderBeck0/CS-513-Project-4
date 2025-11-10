import heapq
from copy import deepcopy
from typing import Any
import networkx as nx
from graph_manager import GraphManager


class RoutingAlgorithm:
    """Base class for routing algorithms."""

    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager

    def run(self, source: str):
        raise NotImplementedError("Subclasses must implement this method.")


class LinkStateRouting(RoutingAlgorithm):
    """Implements the Link-State (Dijkstra) algorithm."""

    def __init__(self, graph_manager: GraphManager, graph: nx.Graph | None = None):
        super().__init__(graph_manager)

        self.graph = graph if graph is not None else graph_manager.graph

    def run(self, source: str):
        graph = self.graph
        if source not in graph.nodes:
            print(f"Node {source} not found in graph.")
            return

        dist = {node: float("inf") for node in graph.nodes}
        prev: dict[Any, None | str] = {node: None for node in graph.nodes}
        dist[source] = 0

        pq = [(0, source)]
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            if current_dist > dist[current_node]:
                continue

            for neighbor, attrs in graph.adj[current_node].items():
                weight = attrs["weight"]
                new_dist = current_dist + weight

                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))

        results = []
        for node in graph.nodes:
            distance = dist[node]
            if distance == float("inf"):
                continue
            if node == source:
                via = "-"
            else:
                via = prev[node]
            results.append((distance, node, via))
        results.sort(key=lambda x: x[0])

        print(f"\nRouting Table for node {source} (Sorted by Cost):")
        for distance, node, via in results:
            print(f"{node} {via} {distance}")


class DistanceVectorRouting(RoutingAlgorithm):
    """Implements the Distance Vector Routing Algorithm."""

    def __init__(self, graph_manager: GraphManager):
        super().__init__(graph_manager)

    def run(self, source: str):
        graphs = self.graph_manager.graphs # Distributed graphs
        graph = self.graph_manager.graph # Overall graph

        # Loop through ALL the nodes
        for node in graph.nodes:
            graphs[node] = graphs.get(node, None) or nx.Graph()
            # Populate the direct neighbors
            for neighbor in graph.neighbors(node):
                w = graph.get_edge_data(node, neighbor)["weight"]
                graphs[node].add_edge(node, neighbor, weight=w)

            # Remove non-existent edges
            for u, v in list(graphs[node].edges()):
                if not graph.has_edge(u, v):
                    graphs[node].remove_edge(u, v)
        
        # Freeze graph state for convergence check
        pre_graph = deepcopy(graphs[source])

        # Combine the graphs
        for node in graph.nodes:
            for neighbor in graphs[node].nodes:
                graphs[node] = nx.compose(graphs[node], graphs[neighbor])

        # Find shortest path (reusing code :D)
        LinkStateRouting(graph_manager=self.graph_manager, graph=graphs[source]).run(source)
        
        # Check if the graph has converged
        converged = nx.is_isomorphic(graphs[source], pre_graph)
        if converged:
            print("The Distance Vector Routing Algorithm has converged! Any future use of the dv command with the same graph will not change the output.")


    @staticmethod
    def dv_difference(dvs1: dict, dvs2: dict):
        differences = {}
        real_diff = {}
        for key in set(dvs1.keys()) & set(dvs2.keys()):
            if dvs1[key] != dvs2[key]:
                differences[key] = (dvs1[key], dvs2[key])
        
        for k in differences:
            for key in set(differences[k][0].keys()) & set(differences[k][1].keys()):
                if differences[k][0][key] != differences[k][1][key]:
                    real_diff[key] = (differences[k][0][key], differences[k][1][key])


        for k in real_diff:
            print(f"Key: {k}")
            print(f"dvs: {real_diff[k][0]}")
            print(f"dvs_snapshot: {real_diff[k][1]}")

    @staticmethod
    def dvs_equal(
        dvs1: dict[str, dict[str, int]], dvs2: dict[str, dict[str, int]]
    ) -> bool:
        # Compares the equality of two dvs's.
        # This function is literally a waste of space but whatever
        # Could be handy to keep in case we decide to change our definition of equal
        # (i.e. not require node names to be equal)
        return dvs1 == dvs2
