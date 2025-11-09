import heapq
from copy import deepcopy
from typing import Any

from graph_manager import GraphManager


class RoutingAlgorithm:
    """Base class for routing algorithms."""

    def __init__(self, graph_manager: GraphManager):
        self.graph_manager = graph_manager

    def run(self, source: str):
        raise NotImplementedError("Subclasses must implement this method.")


class LinkStateRouting(RoutingAlgorithm):
    """Implements the Link-State (Dijkstra) algorithm."""

    def run(self, source: str):
        graph = self.graph_manager.graph
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
        # Mantain a distance vector for each node, initialized with costs to each directly-connected nodes
        # Each node updates its own distance vector based on updates it receives from its neighbors

        # source is ONLY used to print at the end
        # I'm thinking, when it sends it, use the min found weight

        # Send its dv to each of its neighbors
        # TODO: Add convergence testing
        dvs = self.graph_manager.dvs
        graph = self.graph_manager.graph
        changes = self.graph_manager.changes
        
        # Initialization
        for node in graph:
            if node not in dvs.keys():
                dvs[node] = {}

            neighbors = graph.neighbors(node)
            for neighbor in neighbors:
                w = graph.get_edge_data(node, neighbor)["weight"]
                # Does this follow the definition of "one iteration"?
                # What if the following occurs:
                # A J 9
                # C J 1
                # C J 999

                # Start from scratch when graph changes
                #   dvs - change AT NODE
                # Store vias
                
                if node == "C" and neighbor == "J":
                    print(changes)
                # TODO: Check for removed edges
                if node == "C" and neighbor == "J" and neighbor in dvs.keys():
                    print(f"W: {w}")
                    print(f"dvs[node][neighbore]: {dvs[node][neighbor]}")
                    print(f"not changes node and neighbor: {not (changes[node] and changes[neighbor])}")
                    print(f"Change in both: {changes[node] and changes[neighbor]}")
                    print(f"Full thing: {(w < dvs[node][neighbor] and not (changes[node] and changes[neighbor]))}")
                if neighbor not in dvs[node] or (w < dvs[node][neighbor] and not (changes[node] and changes[neighbor])) or (changes[node] and changes[neighbor]):
                    dvs[node][neighbor] = w
                    if node == "C" and neighbor == "J":
                        print("HIT")
                        print(dvs[node][neighbor])


            # Set distance to itself to 0
            dvs[node][node] = 0

        try:
            print(dvs["B"]["J"])
        except:
            ...
        dvs_snapshot = deepcopy(dvs)
        for node in dvs_snapshot.keys():
            dv = dvs_snapshot[node]
            for neighbor in dv.keys():
                neighbor_dv = dvs_snapshot[neighbor]

                # Combine node's dv with neighbor's dv
                for n in neighbor_dv.keys():
                    if n == node:
                        continue

                    current_cost = dvs_snapshot[node][neighbor]
                    if (changes[node] and changes[neighbor]):
                        current_cost = dvs[node][neighbor]
                        if node == "B" and neighbor == "J":
                            print("HIT2", current_cost)
                        
                    new_cost = current_cost + neighbor_dv[n]
                    if n not in dvs[node].keys():
                        # Add it to the keys
                        dvs[node][n] = new_cost
                    elif new_cost < dvs[node][n]:
                        dvs[node][n] = new_cost
        # TODO: Make this prettier
        print(dvs[source])
        if DistanceVectorRouting.dvs_equal(dvs1=dvs, dvs2=dvs_snapshot):
            print(
                "The Distance Vector Routing Algorithm has converged! Any future use of the dv command with the same graph will not change the output."
            )
        for node in graph:
            changes[node] = False

    @staticmethod
    def dvs_equal(
        dvs1: dict[str, dict[str, int]], dvs2: dict[str, dict[str, int]]
    ) -> bool:
        # Compares the equality of two dvs's.
        # This function is literally a waste of space but whatever
        # Could be handy to keep in case we decide to change our definition of equal
        # (i.e. not require node names to be equal)
        return dvs1 == dvs2
