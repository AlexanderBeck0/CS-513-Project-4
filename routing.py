import heapq
from copy import deepcopy
from typing import Any
import networkx as nx
from graph_manager import GraphManager

class RoutingAlgorithm:
    """Base class for routing algorithms."""

    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager

    def run(self, source: str, iterative: bool = False) -> bool:
        raise NotImplementedError("Subclasses must implement this method.")

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


class LinkStateRouting(RoutingAlgorithm):
    """Implements the Link-State (Dijkstra) algorithm."""

    def __init__(self, graph_manager: GraphManager, graph: nx.Graph | None = None):
        super().__init__(graph_manager)

        self.graph = graph if graph is not None else graph_manager.graph

    def run(self, source: str, iterative=False) -> bool:
        # Ignore iterative but keep it for inheritence

        graph = self.graph
        if source not in graph.nodes:
            print(f"Node {source} not found in graph.")
            return False

        results = dijkstra(source=source, graph=graph)
        print_vias(results, source)

        return True



def dijkstra(
    source: str, graph: nx.Graph
) -> list[tuple[float, str, str]]:
    """Runs Dijkstra and returns a list of tuples (distance, node, via). If iterative is True, will run it iteratively

    Returns:
        list: [(distance: float, node: str, via: str)]
    """
    assert source in graph.nodes
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
    
    results = find_vias(graph, dist, prev, source)
    return results

    
def find_vias(graph: nx.Graph, dvs: dict, prev: dict, source: str) -> list[tuple]:
    results = []
    for node in graph.nodes:
        distance = dvs.get(node, float("inf"))
        if distance == float("inf"):
            continue
        if node == source:
            via = "-"
        elif prev[node] == None:
            via = source
        else:
            via = prev[node]
        results.append((distance, node, via))
    results.sort(key=lambda x: x[0])
    return results

def print_vias(vias: tuple[float, str, str], source: str) -> None:
    print(f"\nRouting Table for node {source} (Sorted by Cost):")
    for distance, node, via in vias:
        print(f"{node} <- {via} ({distance})")
    
def average_shortest_path(graph: nx.Graph) -> tuple[str, str, float, dict[str, float]]:
    dijkstra_len: dict[str, float] = dict.fromkeys(list(graph.nodes), 0.0)
    for node in graph:
        results = dijkstra(node, graph)
        dijkstra_len[node] = sum([result[0] for result in results]) / len(results)
    max_node: str = max(dijkstra_len, key=dijkstra_len.get)  # type: ignore
    min_node: str = min(dijkstra_len, key=dijkstra_len.get)  # type: ignore
    avg_len: float = sum(dijkstra_len.values()) / len(dijkstra_len)
    return max_node, min_node, avg_len, dijkstra_len


class DistributredLinkStateRouting(RoutingAlgorithm):
    """Implements the Distance Vector Routing Algorithm."""

    def __init__(self, graph_manager: GraphManager):
        super().__init__(graph_manager)

    def run(self, source: str, iterative: bool = False) -> bool:
        # Check if source node exists
        if source not in self.graph_manager.graph.nodes:
            print(f"Node {source} not found in graph.")
            return False
        
        if iterative:
            # Run iteratively 
            return self.run_iterative(source)
        else:
            # Run until completion
            run_count = 0
            while not self.run_iterative(source):
                run_count += 1
                if run_count == 10:
                    print("Distributed Link State Routing Algorithm ran 10 times and did not converge. Stopping.")
                    return False
            print(f"Distributed Link State Routing algorithm converged after {run_count + 1} runs")
            return True

    def run_iterative(self, source: str) -> bool:
        graphs = self.graph_manager.graphs  # Distributed graphs
        graph = self.graph_manager.graph  # Overall graph

        # Check if source node exists
        if source not in graph.nodes:
            print(f"Node {source} not found in graph.")
            return False

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
        LinkStateRouting(graph_manager=self.graph_manager, graph=graphs[source]).run(
            source, iterative=False
        )

        # Check if the graph has converged
        converged = nx.is_isomorphic(graphs[source], pre_graph)
        if converged:
            print(
                "The Distance Vector Routing Algorithm has converged! Any future use of the dv command with the same graph will not change the output."
            )
            return True
        return False

class DistanceVectorRouting(RoutingAlgorithm):
    """Implements the Distance Vector Routing Algorithm."""

    def __init__(self, graph_manager: GraphManager):
        super().__init__(graph_manager)

    def run(self, source: str, iterative: bool = False):
        # Check if source node exists
        if source not in self.graph_manager.graph.nodes:
            print(f"Node {source} not found in graph.")
            return False
        if iterative:
            # Run iteratively 
            return self.run_iterative(source)
        else:
            # Run until completion
            run_count = 0
            while not self.run_iterative(source):
                run_count += 1
                if run_count == 10:
                    print("Distance Vector Routing Algorithm ran 10 times and did not converge. Stopping.")
                    return False
            print(f"Distance Vector Routing algorithm converged after {run_count + 1} runs")
            return True

    def run_iterative(self, source: str) -> bool:
        graph = self.graph_manager.graph
        dvs = self.graph_manager.dvs
        prev: dict[Any, None | str] = {node: None for node in graph.nodes}
        
        for node in graph.nodes:
            if node not in dvs:
                dvs[node] = {}

            # distance to self is 0
            dvs[node][node] = 0

            # set direct neighors costs
            # for neighbor, attrs in graph[node].items():
            #     dvs[node][neighbor] = attrs["weight"]
                
        dvs_snapshot = deepcopy(dvs)
        for node1 in graph.nodes:
            for node2 in graph.nodes:
                if node1 == node2:
                    continue

                min_cost = float("inf")
                min_node = None
                for v, attrs in graph[node1].items():  # for each neighbor v of x
                    # A vertex v lies on a shortest path between vertices s, t iff
                    # d_G(x, y) = d_G(x,v) + d_G(v, y)
                    cost_xv = attrs["weight"]
                    cost_vy = dvs[v].get(node2, float("inf"))
                    min_cost = min(min_cost, cost_xv + cost_vy)
                    if min_cost == cost_xv + cost_vy:
                        min_node = v
                
                if min_node is not None:
                    prev[min_node] = node1
                dvs[node1][node2] = min_cost
                if dvs[node1][node2] == float("inf"):
                    dvs[node1].pop(node2)
        
        vias = find_vias(graph, dvs[source], prev, source)
        print_vias(vias, source)
        if DistanceVectorRouting.dvs_equal(dvs1=dvs, dvs2=dvs_snapshot):
            print(
                "The Distance Vector Routing Algorithm has converged! Any future use of the dv command with the same graph will not change the output."
            )
            return True

        return False